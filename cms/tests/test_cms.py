from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from website import models as m


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("staffuser", password="pass12345", is_staff=True)

    def test_login_required_for_dashboard(self):
        response = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("cms:login"), response.url)

    def test_login_success(self):
        response = self.client.post(reverse("cms:login"), {"username": "staffuser", "password": "pass12345"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get("_auth_user_id"))

    def test_logout(self):
        self.client.login(username="staffuser", password="pass12345")
        self.client.post(reverse("cms:logout"))
        response = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(response.status_code, 302)


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin", "admin@example.org", "pass12345")
        self.client.login(username="admin", password="pass12345")

    def test_dashboard_counts(self):
        m.Church.objects.create(name="Dash Church", region="kerala", status="published")
        m.ContactMessage.objects.create(name="A", email="a@example.org", message="hi", status="unread")
        response = self.client.get(reverse("cms:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_churches"], 1)
        self.assertEqual(response.context["unread_messages"], 1)


class RolePermissionTests(TestCase):
    """Verifies permissions are enforced on the backend, not just in the UI."""

    def setUp(self):
        call_command("setup_roles")
        self.editor = User.objects.create_user("editor", password="pass12345", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.manager = User.objects.create_user("manager", password="pass12345", is_staff=True)
        self.manager.groups.add(Group.objects.get(name="Content Manager"))
        self.church = m.Church.objects.create(name="Perm Church", region="kerala", status="published")

    def test_editor_can_view_and_add_but_not_delete(self):
        self.client.login(username="editor", password="pass12345")
        self.assertEqual(self.client.get(reverse("cms:church_list")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cms:church_add")).status_code, 200)
        self.assertEqual(self.client.get(reverse("cms:church_delete", args=[self.church.pk])).status_code, 403)

    def test_editor_cannot_reach_site_settings(self):
        self.client.login(username="editor", password="pass12345")
        self.assertEqual(self.client.get(reverse("cms:settings")).status_code, 403)

    def test_content_manager_can_delete(self):
        self.client.login(username="manager", password="pass12345")
        response = self.client.post(reverse("cms:church_delete", args=[self.church.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(m.Church.objects.filter(pk=self.church.pk).exists())

    def test_content_manager_can_edit_site_settings(self):
        self.client.login(username="manager", password="pass12345")
        self.assertEqual(self.client.get(reverse("cms:settings")).status_code, 200)


class CRUDLifecycleTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser("admin2", "admin2@example.org", "pass12345")
        self.client.login(username="admin2", password="pass12345")

    def _church_payload(self, **overrides):
        payload = {
            "name": "CRUD Church", "region": "kerala", "short_description": "desc",
            "description": "<p>desc</p>", "pastor": "Pastor", "city": "Kottayam",
            "state": "Kerala", "country": "India", "service_times": "Sunday 9AM",
            "status": "published", "order": "0",
        }
        payload.update(overrides)
        return payload

    def test_create_edit_delete_church(self):
        create_resp = self.client.post(reverse("cms:church_add"), self._church_payload())
        self.assertEqual(create_resp.status_code, 302)
        church = m.Church.objects.get(name="CRUD Church")

        edit_resp = self.client.post(
            reverse("cms:church_edit", args=[church.pk]),
            self._church_payload(name="CRUD Church Edited"),
        )
        self.assertEqual(edit_resp.status_code, 302)
        church.refresh_from_db()
        self.assertEqual(church.name, "CRUD Church Edited")

        delete_resp = self.client.post(reverse("cms:church_delete", args=[church.pk]))
        self.assertEqual(delete_resp.status_code, 302)
        self.assertFalse(m.Church.objects.filter(pk=church.pk).exists())

    def test_publish_unpublish_blog_post(self):
        post = m.BlogPost.objects.create(title="Draft Post", content="<p>x</p>", status="draft")
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 404)
        post.status = "published"
        post.save()
        self.assertEqual(self.client.get(post.get_absolute_url()).status_code, 200)

    def test_contact_message_mark_read_and_archive(self):
        msg = m.ContactMessage.objects.create(name="X", email="x@example.org", message="hi", status="unread")
        self.client.get(reverse("cms:message_detail", args=[msg.pk]))
        msg.refresh_from_db()
        self.assertEqual(msg.status, "read")

        self.client.post(reverse("cms:message_detail", args=[msg.pk]), {"action": "archive"})
        msg.refresh_from_db()
        self.assertEqual(msg.status, "archived")


class SignupScreenTests(TestCase):
    """Prayer list and newsletter sign-ups are visible, exportable and removable in the CMS."""

    def setUp(self):
        call_command("setup_roles")
        self.manager = User.objects.create_user("mgr", password="pass12345", is_staff=True)
        self.manager.groups.add(Group.objects.get(name="Content Manager"))
        self.editor = User.objects.create_user("ed", password="pass12345", is_staff=True)
        self.editor.groups.add(Group.objects.get(name="Editor"))
        self.signup = m.PrayerListSignup.objects.create(name="Ravi Kumar", email="ravi@example.org")
        m.NewsletterSubscriber.objects.create(email="sub@example.org")

    def test_manager_sees_and_exports_prayer_list(self):
        self.client.login(username="mgr", password="pass12345")
        response = self.client.get(reverse("cms:prayer_list"))
        self.assertContains(response, "Ravi Kumar")
        csv_response = self.client.get(reverse("cms:prayer_list") + "?export=csv")
        self.assertEqual(csv_response["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("ravi@example.org", csv_response.content.decode("utf-8-sig"))

    def test_newsletter_search(self):
        self.client.login(username="mgr", password="pass12345")
        self.assertContains(self.client.get(reverse("cms:newsletter_list") + "?q=sub"), "sub@example.org")
        self.assertNotContains(self.client.get(reverse("cms:newsletter_list") + "?q=nobody"), "sub@example.org")

    def test_editor_can_view_but_not_delete(self):
        self.client.login(username="ed", password="pass12345")
        self.assertEqual(self.client.get(reverse("cms:prayer_list")).status_code, 200)
        response = self.client.post(reverse("cms:prayer_list"), {"ids": [self.signup.pk]})
        self.assertEqual(response.status_code, 403)
        self.assertTrue(m.PrayerListSignup.objects.filter(pk=self.signup.pk).exists())

    def test_manager_can_delete(self):
        self.client.login(username="mgr", password="pass12345")
        self.client.post(reverse("cms:prayer_list"), {"ids": [self.signup.pk]})
        self.assertFalse(m.PrayerListSignup.objects.exists())


class GalleryVideoCMSTests(TestCase):
    def setUp(self):
        User.objects.create_superuser("admin", "admin@example.org", "pass12345")
        self.client.login(username="admin", password="pass12345")

    def test_add_youtube_video(self):
        response = self.client.post(reverse("cms:video_add"), {
            "title": "Baptism", "youtube_url": "https://youtu.be/dQw4w9WgXcQ?si=x", "order": 0, "is_active": "on"})
        self.assertEqual(response.status_code, 302)
        video = m.GalleryVideo.objects.get()
        self.assertEqual(video.youtube_id, "dQw4w9WgXcQ")
        self.assertContains(self.client.get(reverse("website:gallery")),
                            "youtube-nocookie.com/embed/dQw4w9WgXcQ")

    def test_rejects_non_youtube_link_and_empty(self):
        self.client.post(reverse("cms:video_add"), {
            "title": "Bad", "youtube_url": "https://example.com/watch", "order": 0, "is_active": "on"})
        self.client.post(reverse("cms:video_add"), {"title": "Empty", "order": 0, "is_active": "on"})
        self.assertFalse(m.GalleryVideo.objects.exists())


class PageSEOTests(TestCase):
    def setUp(self):
        User.objects.create_superuser("admin", "admin@example.org", "pass12345")
        self.client.login(username="admin", password="pass12345")

    def test_every_page_is_listed_and_editable(self):
        response = self.client.get(reverse("cms:pageseo_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(m.PageSEO.objects.count(), len(m.PageSEO.PAGE_CHOICES))

    def test_meta_and_og_tags_rendered(self):
        row = m.PageSEO.objects.get(page="about")
        self.client.post(reverse("cms:pageseo_edit", args=[row.pk]), {
            "meta_title": "About ICCM", "meta_description": "Since 1996.",
            "meta_keywords": "church", "og_title": "Meet ICCM", "og_description": ""})
        html = self.client.get(reverse("website:about")).content.decode()
        self.assertIn("<title>About ICCM</title>", html)
        self.assertIn('<meta name="description" content="Since 1996.">', html)
        self.assertIn('<meta property="og:title" content="Meet ICCM">', html)
        self.assertIn('<meta property="og:description" content="Since 1996.">', html)

    def test_noindex(self):
        m.PageSEO.objects.update_or_create(page="contact", defaults={"noindex": True})
        self.assertContains(self.client.get(reverse("website:contact")), 'content="noindex, nofollow"')

    def test_detail_page_uses_its_own_seo_fields(self):
        post = m.BlogPost.objects.create(title="A Post", content="<p>Body</p>", excerpt="Short",
                                         status="published", seo_title="Custom SEO title")
        html = self.client.get(post.get_absolute_url()).content.decode()
        self.assertIn("<title>Custom SEO title</title>", html)
        self.assertIn('<meta property="og:type" content="article">', html)
        self.assertIn('<meta name="description" content="Short">', html)

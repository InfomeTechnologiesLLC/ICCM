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

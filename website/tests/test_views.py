import datetime

from django.test import TestCase
from django.urls import reverse

from website import models as m


class HomePageTests(TestCase):
    def test_home_renders_with_empty_database(self):
        """Every homepage section must degrade gracefully with no content."""
        response = self.client.get(reverse("website:home"))
        self.assertEqual(response.status_code, 200)

    def test_home_shows_upcoming_event(self):
        m.Event.objects.create(
            name="Homepage Test Event",
            start_date=datetime.date.today() + datetime.timedelta(days=3),
            status="published",
        )
        response = self.client.get(reverse("website:home"))
        self.assertContains(response, "Homepage Test Event")


class ListingPageTests(TestCase):
    def test_church_list_empty_state(self):
        response = self.client.get(reverse("website:church_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "will appear here")

    def test_church_list_shows_published_only(self):
        m.Church.objects.create(name="Published Church", region="kerala", status="published")
        m.Church.objects.create(name="Draft Church", region="kerala", status="draft")
        response = self.client.get(reverse("website:church_list"))
        self.assertContains(response, "Published Church")
        self.assertNotContains(response, "Draft Church")

    def test_ministry_list(self):
        m.Ministry.objects.create(name="Youth Ministry", status="published")
        response = self.client.get(reverse("website:ministry_list"))
        self.assertContains(response, "Youth Ministry")

    def test_event_list_upcoming_filter_default(self):
        today = datetime.date.today()
        m.Event.objects.create(name="Future", start_date=today + datetime.timedelta(days=10), status="published")
        m.Event.objects.create(name="Bygone", start_date=today - datetime.timedelta(days=10),
                                status="published", is_completed=True)
        response = self.client.get(reverse("website:event_list"))
        self.assertContains(response, "Future")
        self.assertNotContains(response, "Bygone")

    def test_blog_list_pagination(self):
        for i in range(8):
            m.BlogPost.objects.create(title=f"Post {i}", content="<p>x</p>", status="published")
        response = self.client.get(reverse("website:blog_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["page_obj"].has_next())


class DetailPageTests(TestCase):
    def test_church_detail_200(self):
        church = m.Church.objects.create(name="Detail Church", region="kerala", status="published")
        response = self.client.get(church.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Detail Church")

    def test_unpublished_church_404(self):
        church = m.Church.objects.create(name="Hidden Church", region="kerala", status="draft")
        response = self.client.get(church.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_event_detail_200(self):
        event = m.Event.objects.create(name="Detail Event", start_date=datetime.date.today(), status="published")
        response = self.client.get(event.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_blog_detail_200(self):
        post = m.BlogPost.objects.create(title="Detail Post", content="<p>Body</p>", status="published")
        response = self.client.get(post.get_absolute_url())
        self.assertEqual(response.status_code, 200)


class ContactFormTests(TestCase):
    def test_valid_contact_submission_creates_message(self):
        response = self.client.post(reverse("website:contact"), {
            "form_type": "contact", "name": "Jane Visitor", "email": "jane@example.org",
            "subject": "Hello", "reason": "general", "message": "Testing the contact form.",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(m.ContactMessage.objects.count(), 1)
        self.assertEqual(m.ContactMessage.objects.first().status, "unread")

    def test_invalid_contact_submission_shows_errors(self):
        response = self.client.post(reverse("website:contact"), {
            "form_type": "contact", "name": "", "email": "not-an-email", "message": "",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(m.ContactMessage.objects.count(), 0)

    def test_newsletter_signup(self):
        response = self.client.post(reverse("website:contact"), {
            "form_type": "newsletter", "email": "subscriber@example.org",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(m.NewsletterSubscriber.objects.count(), 1)

    def test_newsletter_signup_is_idempotent(self):
        self.client.post(reverse("website:contact"), {"form_type": "newsletter", "email": "dup@example.org"})
        self.client.post(reverse("website:contact"), {"form_type": "newsletter", "email": "dup@example.org"})
        self.assertEqual(m.NewsletterSubscriber.objects.count(), 1)

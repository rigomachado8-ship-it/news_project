"""
Test cases for permissions, subscriptions, logout behavior,
email notifications, and API access.
"""

from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import Article, CustomUser, Publisher


class BaseTestCase(TestCase):
    """Provide shared test data for the news application test suite."""

    def setUp(self):
        """Create common users, a publisher, and a sample article."""
        self.reader = CustomUser.objects.create_user(
            username="reader",
            password="pass",
            role=CustomUser.ROLE_READER,
            email="reader@test.com",
        )
        self.journalist = CustomUser.objects.create_user(
            username="journalist",
            password="pass",
            role=CustomUser.ROLE_JOURNALIST,
            email="journalist@test.com",
        )
        self.editor = CustomUser.objects.create_user(
            username="editor",
            password="pass",
            role=CustomUser.ROLE_EDITOR,
            email="editor@test.com",
        )

        self.publisher = Publisher.objects.create(name="Test Publisher")

        self.article = Article.objects.create(
            title="Test Article",
            content="Test content",
            author=self.journalist,
            publisher=self.publisher,
            status=Article.STATUS_PENDING,
        )


class PermissionTests(BaseTestCase):
    """Test access control for article creation, editing, and approval views."""

    def test_reader_cannot_create_article(self):
        """Ensure readers are redirected away from article creation."""
        self.client.login(username="reader", password="pass")
        response = self.client.get(reverse("create_article"))
        self.assertRedirects(response, reverse("dashboard"))

    def test_journalist_can_create_article(self):
        """Ensure journalists can access the article creation page."""
        self.client.login(username="journalist", password="pass")
        response = self.client.get(reverse("create_article"))
        self.assertEqual(response.status_code, 200)

    def test_reader_cannot_edit_article(self):
        """Ensure readers cannot access the article edit page."""
        self.client.login(username="reader", password="pass")
        response = self.client.get(reverse("edit_article", args=[self.article.id]))
        self.assertRedirects(response, reverse("dashboard"))

    def test_editor_can_access_approve_page(self):
        """Ensure editors can access the article approval page."""
        self.client.login(username="editor", password="pass")
        response = self.client.get(reverse("approve_articles"))
        self.assertEqual(response.status_code, 200)


class SubscriptionTests(BaseTestCase):
    """Test reader article subscription behavior."""

    def test_reader_can_subscribe_to_article(self):
        """Ensure a reader can subscribe to an approved article."""
        self.article.status = Article.STATUS_APPROVED
        self.article.save()

        self.client.login(username="reader", password="pass")
        response = self.client.get(reverse("subscribe_article", args=[self.article.id]))

        self.assertRedirects(
            response,
            reverse("article_detail", args=[self.article.id]),
        )
        self.assertTrue(
            self.reader.subscribed_articles.filter(id=self.article.id).exists()
        )

    def test_non_reader_cannot_subscribe(self):
        """Ensure non-readers cannot subscribe to articles."""
        self.article.status = Article.STATUS_APPROVED
        self.article.save()

        self.client.login(username="journalist", password="pass")
        response = self.client.get(reverse("subscribe_article", args=[self.article.id]))

        self.assertEqual(response.status_code, 403)


class LogoutTests(BaseTestCase):
    """Test logout request methods."""

    def test_logout_requires_post(self):
        """Ensure logout only succeeds with a POST request."""
        self.client.login(username="reader", password="pass")

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 405)

        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)


class EmailNotificationTests(BaseTestCase):
    """Test email notifications sent after article approval."""

    def test_email_sent_on_article_approval(self):
        """Ensure subscribers receive an email when an article is approved."""
        self.reader.subscribed_articles.add(self.article)
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.journalist)

        self.client.login(username="editor", password="pass")

        response = self.client.post(
            reverse("approve_articles"),
            {
                "article_id": self.article.id,
                "action": "approve",
            },
        )
        self.assertEqual(response.status_code, 302)

        self.article.refresh_from_db()
        self.assertEqual(self.article.status, Article.STATUS_APPROVED)

        self.assertTrue(len(mail.outbox) > 0)

        email = mail.outbox[0]
        self.assertIn(self.reader.email, email.to)
        self.assertIn(self.article.title, email.subject)


class APITests(BaseTestCase):
    """Test role-based permissions for article API creation."""

    def test_only_journalist_can_create_api(self):
        """Ensure only journalists can create articles through the API."""
        self.client.login(username="reader", password="pass")
        response = self.client.post(
            reverse("api_article_list_create"),
            {"title": "API Test", "content": "Test"},
        )
        self.assertEqual(response.status_code, 403)

        self.client.login(username="journalist", password="pass")
        response = self.client.post(
            reverse("api_article_list_create"),
            {"title": "API Test", "content": "Test"},
        )
        self.assertIn(response.status_code, [200, 201])

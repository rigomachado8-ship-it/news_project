"""
Database models for users, publishers, newsletters, and articles.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class Publisher(models.Model):
    """Represent a publisher that can own many articles."""

    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        """Return the publisher name."""
        return self.name


class Newsletter(models.Model):
    """Represent a newsletter that can group related articles."""

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the newsletter title."""
        return self.title


class CustomUser(AbstractUser):
    """Extend Django's user model with application roles and subscriptions."""

    ROLE_READER = "reader"
    ROLE_EDITOR = "editor"
    ROLE_JOURNALIST = "journalist"

    ROLE_CHOICES = (
        (ROLE_READER, "Reader"),
        (ROLE_EDITOR, "Editor"),
        (ROLE_JOURNALIST, "Journalist"),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_READER,
    )

    subscribed_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name="subscribers",
    )

    subscribed_journalists = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="journalist_subscribers",
    )

    subscribed_articles = models.ManyToManyField(
        "Article",
        blank=True,
        related_name="subscribers",
    )

    def __str__(self):
        """Return a readable representation of the user and role."""
        return f"{self.username} ({self.role})"

    @property
    def is_reader(self):
        """Return True when the user is a reader."""
        return self.role == self.ROLE_READER

    @property
    def is_editor(self):
        """Return True when the user is an editor."""
        return self.role == self.ROLE_EDITOR

    @property
    def is_journalist(self):
        """Return True when the user is a journalist."""
        return self.role == self.ROLE_JOURNALIST


class Article(models.Model):
    """Represent an article written by a journalist and reviewed by editors."""

    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = (
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending Review"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()

    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="articles",
    )

    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )

    approved_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_articles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Model metadata for article ordering."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return the article title."""
        return self.title

    def get_absolute_url(self):
        """Return the URL for the article detail page."""
        return reverse("article_detail", kwargs={"pk": self.pk})

"""
Serializers for publishers, newsletters, users, and articles.
"""

from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher data."""

    class Meta:
        """Metadata for publisher serialization."""

        model = Publisher
        fields = ["id", "name", "description"]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletter data."""

    class Meta:
        """Metadata for newsletter serialization."""

        model = Newsletter
        fields = ["id", "title", "description", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serialize public user data."""

    class Meta:
        """Metadata for user serialization."""

        model = CustomUser
        fields = ["id", "username", "email", "role"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize article data for read and write operations."""

    author = UserSerializer(read_only=True)
    publisher = PublisherSerializer(read_only=True)
    newsletter = NewsletterSerializer(read_only=True)

    publisher_id = serializers.PrimaryKeyRelatedField(
        source="publisher",
        queryset=Publisher.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    newsletter_id = serializers.PrimaryKeyRelatedField(
        source="newsletter",
        queryset=Newsletter.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        """Metadata for article serialization."""

        model = Article
        fields = [
            "id",
            "title",
            "content",
            "author",
            "publisher",
            "newsletter",
            "publisher_id",
            "newsletter_id",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]

    def create(self, validated_data):
        """Attach the current request user as the article author."""
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

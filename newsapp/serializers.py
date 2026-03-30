"""
Serializers for publishers, newsletters, users, profiles, and articles.
"""

from rest_framework import serializers

from .models import Article, CustomUser, Newsletter, Publisher


class PublisherSerializer(serializers.ModelSerializer):
    """Serialize publisher data."""

    class Meta:
        model = Publisher
        fields = ["id", "name", "description"]


class NewsletterSerializer(serializers.ModelSerializer):
    """Serialize newsletter data."""

    class Meta:
        model = Newsletter
        fields = ["id", "title", "description", "created_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serialize user summary data."""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize editable profile data."""

    class Meta:
        model = CustomUser
        fields = ["id", "username", "email", "role"]

    def validate_role(self, value):
        request = self.context.get("request")
        if request and not request.user.is_editor:
            if self.instance and value != self.instance.role:
                raise serializers.ValidationError(
                    "Only editors can change user roles."
                )
        return value

    def validate_email(self, value):
        queryset = CustomUser.objects.filter(email__iexact=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError(
                "An account with this email already exists."
            )
        return value


class ArticleSerializer(serializers.ModelSerializer):
    """Serialize article data with nested related objects."""

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

    def validate_status(self, value):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.is_journalist:
            allowed = {Article.STATUS_DRAFT, Article.STATUS_PENDING}
            if value not in allowed:
                raise serializers.ValidationError(
                    "Journalists can only save drafts or submit for review."
                )
        return value

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
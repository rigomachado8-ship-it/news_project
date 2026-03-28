from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, CustomUser, Newsletter, Publisher


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "News Project Roles",
            {
                "fields": (
                    "role",
                    "subscribed_publishers",
                    "subscribed_journalists",
                )
            },
        ),
    )


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")
    search_fields = ("title",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "publisher", "status", "created_at")
    list_filter = ("status", "publisher", "created_at")
    search_fields = ("title", "content", "author__username")

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .api_permissions import IsEditor, IsOwnerOrEditor, IsJournalistOrReadOnly
from .forms import (
    ArticleForm,
    CustomLoginForm,
    CustomUserRegisterForm,
    ProfileUpdateForm,
)
from .models import Article, CustomUser, Publisher
from .serializers import ArticleSerializer, ProfileSerializer


def can_manage_profile(current_user, profile):
    """Editors can manage all profiles; users can manage their own."""
    return current_user.is_authenticated and (
        current_user.is_editor or current_user == profile
    )


def can_delete_article(current_user, article):
    """
    Editors can delete any article.
    Journalists can delete their own article only if not approved yet.
    """
    if not current_user.is_authenticated:
        return False

    if current_user.is_editor:
        return True

    return bool(
        current_user.is_journalist
        and article.author == current_user
        and article.status != Article.STATUS_APPROVED
    )


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = "login.html"


def register_view(request):
    """Register a new account."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = CustomUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("dashboard")
    else:
        form = CustomUserRegisterForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    """Render login view."""
    view = CustomLoginView.as_view()
    return view(request)


def article_list(request):
    """Show approved articles."""
    articles = (
        Article.objects.select_related("author", "publisher", "newsletter")
        .filter(status=Article.STATUS_APPROVED)
    )
    return render(request, "article_list.html", {"articles": articles})


def article_detail(request, pk):
    """Show article details with access checks for non-approved content."""
    article = get_object_or_404(
        Article.objects.select_related("author", "publisher", "newsletter"),
        pk=pk,
    )

    if article.status != Article.STATUS_APPROVED:
        if not request.user.is_authenticated:
            messages.error(request, "You must log in to view this article.")
            return redirect("login")

        if request.user != article.author and not request.user.is_editor:
            messages.error(
                request,
                "You do not have permission to view this article.",
            )
            return redirect("article_list")

    is_subscribed = False
    can_delete = False

    if request.user.is_authenticated and request.user.is_reader:
        is_subscribed = request.user.subscribed_articles.filter(pk=article.pk).exists()

    if request.user.is_authenticated:
        can_delete = can_delete_article(request.user, article)

    context = {
        "article": article,
        "is_subscribed": is_subscribed,
        "can_delete": can_delete,
    }
    return render(request, "article_detail.html", context)


@login_required
def dashboard_view(request):
    """Role-based dashboard."""
    my_articles = Article.objects.filter(author=request.user).select_related(
        "publisher",
        "newsletter",
    )
    pending_articles = (
        Article.objects.filter(status=Article.STATUS_PENDING)
        .select_related("author", "publisher")
        if request.user.is_editor
        else Article.objects.none()
    )

    context = {
        "my_articles": my_articles,
        "pending_articles": pending_articles,
    }
    return render(request, "dashboard.html", context)


@login_required
def create_article(request):
    """Create a new article."""
    if not (request.user.is_journalist or request.user.is_editor):
        messages.error(request, "Only journalists and editors can create articles.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user

            if request.user.is_journalist and article.status == Article.STATUS_APPROVED:
                article.status = Article.STATUS_PENDING

            if request.user.is_editor and article.status == Article.STATUS_APPROVED:
                article.approved_by = request.user
            else:
                article.approved_by = None

            article.save()
            messages.success(request, "Article saved successfully.")
            return redirect("article_detail", pk=article.pk)
    else:
        form = ArticleForm(user=request.user)

    return render(request, "create_article.html", {"form": form})


@login_required
def edit_article(request, pk):
    """Edit an article with role checks."""
    article = get_object_or_404(Article, pk=pk)

    if request.user.is_reader:
        messages.error(request, "Readers cannot edit articles.")
        return redirect("dashboard")

    if request.user.is_journalist and request.user != article.author:
        messages.error(request, "Journalists can only edit their own articles.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            updated_article = form.save(commit=False)

            if request.user.is_journalist:
                updated_article.author = article.author
                if updated_article.status == Article.STATUS_APPROVED:
                    updated_article.status = Article.STATUS_PENDING
                updated_article.approved_by = None

            if request.user.is_editor:
                if updated_article.status == Article.STATUS_APPROVED:
                    updated_article.approved_by = request.user
                else:
                    updated_article.approved_by = None

            updated_article.save()
            messages.success(request, "Article updated successfully.")
            return redirect("article_detail", pk=updated_article.pk)
    else:
        form = ArticleForm(instance=article, user=request.user)

    return render(
        request,
        "edit_article.html",
        {"form": form, "article": article},
    )


@login_required
def delete_article(request, pk):
    """Delete article with permission rules."""
    article = get_object_or_404(Article, pk=pk)

    if not can_delete_article(request.user, article):
        messages.error(
            request,
            "You do not have permission to delete this article.",
        )
        return redirect("article_detail", pk=article.pk)

    if request.method == "POST":
        title = article.title
        article.delete()
        messages.success(request, f'"{title}" was deleted successfully.')
        return redirect("dashboard")

    return render(request, "delete_article.html", {"article": article})


@login_required
def approve_articles(request):
    """Approve or reject pending articles."""
    if not request.user.is_editor:
        messages.error(request, "Only editors can approve articles.")
        return redirect("dashboard")

    if request.method == "POST":
        article_id = request.POST.get("article_id")
        action = request.POST.get("action")
        article = get_object_or_404(Article, pk=article_id)

        if action == "approve":
            article.status = Article.STATUS_APPROVED
            article.approved_by = request.user
            article.save()

            subscribers = article.subscribers.all()
            recipient_emails = [user.email for user in subscribers if user.email]

            if recipient_emails:
                send_mail(
                    subject=f"New Article: {article.title}",
                    message=(
                        f"A new article has been published.\n\n"
                        f"Title: {article.title}\n"
                        f"Author: {article.author.username}\n"
                        f"Publisher: {article.publisher if article.publisher else 'None'}\n\n"
                        f"{article.content}"
                    ),
                    from_email=None,
                    recipient_list=recipient_emails,
                    fail_silently=True,
                )

            messages.success(
                request,
                f'"{article.title}" was approved and subscribers notified.',
            )

        elif action == "reject":
            article.status = Article.STATUS_REJECTED
            article.approved_by = None
            article.save()
            messages.warning(request, f'"{article.title}" was rejected.')

        return redirect("approve_articles")

    articles = (
        Article.objects.select_related("author", "publisher")
        .filter(status=Article.STATUS_PENDING)
    )
    return render(request, "approve_articles.html", {"articles": articles})


@login_required
def profile_detail(request, pk):
    """Read profile details."""
    profile = get_object_or_404(CustomUser, pk=pk)

    if not can_manage_profile(request.user, profile):
        messages.error(request, "You do not have permission to view this profile.")
        return redirect("dashboard")

    return render(request, "profile_detail.html", {"profile_user": profile})


@login_required
def profile_update(request, pk):
    """Update profile details."""
    profile = get_object_or_404(CustomUser, pk=pk)

    if not can_manage_profile(request.user, profile):
        messages.error(request, "You do not have permission to edit this profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ProfileUpdateForm(
            request.POST,
            instance=profile,
            acting_user=request.user,
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile_detail", pk=profile.pk)
    else:
        form = ProfileUpdateForm(instance=profile, acting_user=request.user)

    return render(
        request,
        "profile_form.html",
        {"form": form, "profile_user": profile},
    )


@login_required
def profile_delete(request, pk):
    """Delete a profile."""
    profile = get_object_or_404(CustomUser, pk=pk)

    if not can_manage_profile(request.user, profile):
        messages.error(request, "You do not have permission to delete this profile.")
        return redirect("dashboard")

    if request.method == "POST":
        deleting_self = request.user == profile
        username = profile.username
        profile.delete()
        messages.success(request, f'Profile "{username}" was deleted successfully.')

        if deleting_self:
            return redirect("article_list")
        return redirect("dashboard")

    return render(
        request,
        "profile_confirm_delete.html",
        {"profile_user": profile},
    )


@login_required
def my_subscriptions(request):
    """Show subscriptions for readers."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can view subscriptions.")

    publishers = request.user.subscribed_publishers.all()
    journalists = request.user.subscribed_journalists.all()
    articles = request.user.subscribed_articles.filter(
        status=Article.STATUS_APPROVED
    )

    return render(
        request,
        "my_subscriptions.html",
        {
            "publishers": publishers,
            "journalists": journalists,
            "articles": articles,
        },
    )


@login_required
def subscribed_articles(request):
    """Show subscribed articles for readers."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can view subscribed articles.")

    articles = request.user.subscribed_articles.filter(
        status=Article.STATUS_APPROVED
    ).select_related("author", "publisher", "newsletter")

    return render(request, "subscribed_articles.html", {"articles": articles})


@login_required
def subscribe_article(request, pk):
    """Subscribe to an article."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to articles.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.add(article)
    messages.success(request, f'You subscribed to "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def unsubscribe_article(request, pk):
    """Unsubscribe from an article."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can manage article subscriptions.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.remove(article)
    messages.success(request, f'You unsubscribed from "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def subscribe_publisher(request, publisher_id):
    """Subscribe to a publisher."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to publishers.")

    publisher = get_object_or_404(Publisher, pk=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    messages.success(request, f"You subscribed to {publisher.name}.")
    return redirect("article_list")


@login_required
def subscribe_journalist(request, user_id):
    """Subscribe to a journalist."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to journalists.")

    journalist = get_object_or_404(
        CustomUser,
        pk=user_id,
        role=CustomUser.ROLE_JOURNALIST,
    )
    request.user.subscribed_journalists.add(journalist)
    messages.success(request, f"You subscribed to {journalist.username}.")
    return redirect("article_list")


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_editor:
            return Article.objects.select_related(
                "author",
                "publisher",
                "newsletter",
            ).all()

        if user.is_authenticated:
            return (
                Article.objects.select_related("author", "publisher", "newsletter")
                .filter(Q(status=Article.STATUS_APPROVED) | Q(author=user))
                .distinct()
            )

        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_APPROVED)

    def perform_create(self, serializer):
        user = self.request.user

        if not (user.is_journalist or user.is_editor):
            raise PermissionDenied("Only journalists and editors can create articles.")

        article = serializer.save(author=user)

        if user.is_journalist and article.status == Article.STATUS_APPROVED:
            article.status = Article.STATUS_PENDING
            article.approved_by = None
            article.save()

        if user.is_editor and article.status == Article.STATUS_APPROVED:
            article.approved_by = user
            article.save()


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and user.is_editor:
            return Article.objects.select_related(
                "author",
                "publisher",
                "newsletter",
            ).all()

        if user.is_authenticated:
            return (
                Article.objects.select_related("author", "publisher", "newsletter")
                .filter(Q(status=Article.STATUS_APPROVED) | Q(author=user))
                .distinct()
            )

        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_APPROVED)

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def update(self, request, *args, **kwargs):
        article = self.get_object()

        if request.user.is_reader:
            raise PermissionDenied("Readers cannot edit articles.")

        if request.user.is_editor:
            response = super().update(request, *args, **kwargs)
            article.refresh_from_db()
            if article.status == Article.STATUS_APPROVED:
                article.approved_by = request.user
                article.save()
            else:
                article.approved_by = None
                article.save()
            return response

        if request.user.is_journalist:
            if article.author != request.user:
                raise PermissionDenied(
                    "Journalists can only edit their own articles."
                )

            response = super().update(request, *args, **kwargs)
            article.refresh_from_db()

            if article.status == Article.STATUS_APPROVED:
                article.status = Article.STATUS_PENDING

            article.approved_by = None
            article.save()
            return response

        raise PermissionDenied("You do not have permission to edit this article.")

    def destroy(self, request, *args, **kwargs):
        article = self.get_object()

        if request.user.is_editor:
            return super().destroy(request, *args, **kwargs)

        if (
            request.user.is_journalist
            and article.author == request.user
            and article.status != Article.STATUS_APPROVED
        ):
            return super().destroy(request, *args, **kwargs)

        raise PermissionDenied(
            "Journalists can only delete their own unapproved articles."
        )


class SubscribedArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if not user.is_reader:
            raise PermissionDenied("Only readers can view subscribed articles.")

        return user.subscribed_articles.filter(
            status=Article.STATUS_APPROVED
        ).select_related("author", "publisher", "newsletter")


class PendingArticlesAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_PENDING)


class ProfileDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    queryset = CustomUser.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrEditor]

    def get_object(self):
        profile = super().get_object()
        self.check_object_permissions(self.request, profile)
        return profile
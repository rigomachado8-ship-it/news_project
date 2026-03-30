"""
Views for authentication, article management, subscriptions,
publisher/newsletter creation, and article-related API endpoints.
"""

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

from .api_permissions import IsEditor, IsJournalistOrReadOnly
from .forms import (
    ArticleForm,
    CustomLoginForm,
    CustomUserRegisterForm,
    NewsletterForm,
    PublisherForm,
)
from .models import Article, CustomUser, Newsletter, Publisher
from .serializers import ArticleSerializer


class CustomLoginView(LoginView):
    """Render and process the custom login form."""

    authentication_form = CustomLoginForm
    template_name = "login.html"


def register_view(request):
    """Register a new user and log them in after successful signup."""
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
    """Delegate login requests to the custom login view."""
    view = CustomLoginView.as_view()
    return view(request)


def article_list(request):
    """Display all approved articles."""
    articles = Article.objects.select_related(
        "author", "publisher", "newsletter"
    ).filter(status=Article.STATUS_APPROVED)
    return render(request, "article_list.html", {"articles": articles})


def article_detail(request, pk):
    """
    Display a single article.

    Approved articles are visible to everyone. Unapproved articles are only
    visible to their author or an editor.
    """
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
    if request.user.is_authenticated and request.user.is_reader:
        is_subscribed = request.user.subscribed_articles.filter(pk=article.pk).exists()

    context = {
        "article": article,
        "is_subscribed": is_subscribed,
    }
    return render(request, "article_detail.html", context)


@login_required
def dashboard_view(request):
    """Display the logged-in user's dashboard content."""
    context = {
        "my_articles": Article.objects.filter(author=request.user),
        "pending_articles": Article.objects.filter(status=Article.STATUS_PENDING),
        "publishers": Publisher.objects.all(),
        "newsletters": Newsletter.objects.all(),
    }
    return render(request, "dashboard.html", context)


@login_required
def create_publisher(request):
    """Allow editors to create publishers."""
    if not request.user.is_editor:
        messages.error(request, "Only editors can create publishers.")
        return redirect("dashboard")

    if request.method == "POST":
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Publisher created successfully.")
            return redirect("dashboard")
    else:
        form = PublisherForm()

    return render(request, "create_publisher.html", {"form": form})


@login_required
def create_newsletter(request):
    """Allow editors and journalists to create newsletters."""
    if not (request.user.is_editor or request.user.is_journalist):
        messages.error(request, "You do not have permission to create newsletters.")
        return redirect("dashboard")

    if request.method == "POST":
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Newsletter created successfully.")
            return redirect("dashboard")
    else:
        form = NewsletterForm()

    return render(request, "create_newsletter.html", {"form": form})


@login_required
def create_article(request):
    """
    Allow journalists to create a new article.

    If a journalist attempts to create an already approved article, it is
    changed back to pending review.
    """
    if not request.user.is_journalist:
        messages.error(request, "Only journalists can create articles.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user

            if article.status == Article.STATUS_APPROVED:
                article.status = Article.STATUS_PENDING

            article.save()
            messages.success(request, "Article saved successfully.")
            return redirect("article_detail", pk=article.pk)
    else:
        form = ArticleForm(user=request.user)

    return render(request, "create_article.html", {"form": form})


@login_required
def edit_article(request, pk):
    """
    Allow editors to edit any article and journalists to edit their own.

    Readers and unauthorized users are redirected away from the edit page.
    """
    article = get_object_or_404(Article, pk=pk)

    if request.user.is_reader:
        messages.error(request, "Readers cannot edit articles.")
        return redirect("dashboard")

    if request.user.is_editor:
        pass
    elif request.user.is_journalist:
        if request.user != article.author:
            messages.error(
                request,
                "Journalists can only edit their own articles.",
            )
            return redirect("dashboard")
    else:
        messages.error(request, "You do not have permission to edit this article.")
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

            if (
                request.user.is_editor
                and updated_article.status == Article.STATUS_APPROVED
            ):
                updated_article.approved_by = request.user

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
def approve_articles(request):
    """
    Allow editors to approve or reject pending articles.

    When an article is approved, notifications are sent to subscribed users
    following the article, its publisher, or its author.
    """
    if not request.user.is_editor:
        messages.error(request, "Only editors can approve articles.")
        return redirect("dashboard")

    if request.method == "POST":
        article_id = request.POST.get("article_id")
        action = request.POST.get("action")
        article = get_object_or_404(
            Article.objects.select_related("author", "publisher"),
            pk=article_id,
        )

        if action == "approve":
            article.status = Article.STATUS_APPROVED
            article.approved_by = request.user
            article.save()

            article_subscribers = article.subscribers.all()
            publisher_subscribers = (
                article.publisher.subscribers.all()
                if article.publisher
                else CustomUser.objects.none()
            )
            journalist_subscribers = article.author.journalist_subscribers.all()

            recipients = (
                article_subscribers | publisher_subscribers | journalist_subscribers
            ).distinct()

            recipient_emails = [user.email for user in recipients if user.email]

            if recipient_emails:
                publisher_name = article.publisher.name if article.publisher else "None"

                send_mail(
                    subject=f"New Article Published: {article.title}",
                    message=(
                        f"A new article has been published.\n\n"
                        f"Title: {article.title}\n"
                        f"Author: {article.author.username}\n"
                        f"Publisher: {publisher_name}\n\n"
                        f"{article.content}"
                    ),
                    from_email=None,
                    recipient_list=recipient_emails,
                    fail_silently=True,
                )

            messages.success(
                request,
                (
                    f'"{article.title}" was approved and all relevant '
                    "subscribers were notified."
                ),
            )

        elif action == "reject":
            article.status = Article.STATUS_REJECTED
            article.approved_by = None
            article.save()
            messages.warning(request, f'"{article.title}" was rejected.')

        return redirect("approve_articles")

    articles = Article.objects.select_related("author", "publisher").filter(
        status=Article.STATUS_PENDING
    )
    return render(request, "approve_articles.html", {"articles": articles})


@login_required
def my_subscriptions(request):
    """Display the current reader's subscribed publishers, journalists, and articles."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can view subscriptions.")

    publishers = request.user.subscribed_publishers.all()
    journalists = request.user.subscribed_journalists.all()
    articles = request.user.subscribed_articles.filter(status=Article.STATUS_APPROVED)

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
    """Display all approved articles subscribed to by the current reader."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can view subscribed articles.")

    articles = request.user.subscribed_articles.filter(
        status=Article.STATUS_APPROVED
    ).select_related("author", "publisher", "newsletter")

    return render(request, "subscribed_articles.html", {"articles": articles})


@login_required
def subscribe_article(request, pk):
    """Subscribe the current reader to a specific approved article."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to articles.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.add(article)
    messages.success(request, f'You subscribed to "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def unsubscribe_article(request, pk):
    """Remove the current reader's subscription from a specific approved article."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can manage article subscriptions.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.remove(article)
    messages.success(request, f'You unsubscribed from "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def subscribe_publisher(request, publisher_id):
    """Subscribe the current reader to a publisher."""
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to publishers.")

    publisher = get_object_or_404(Publisher, pk=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    messages.success(request, f"You subscribed to {publisher.name}.")
    return redirect("article_list")


@login_required
def subscribe_journalist(request, user_id):
    """Subscribe the current reader to a journalist."""
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
    """API endpoint for listing articles and allowing journalists to create them."""

    serializer_class = ArticleSerializer
    permission_classes = [IsJournalistOrReadOnly]

    def get_queryset(self):
        """Return articles visible to the current user."""
        user = self.request.user

        if user.is_authenticated and getattr(user, "is_editor", False):
            return Article.objects.select_related(
                "author",
                "publisher",
                "newsletter",
            ).all()

        if user.is_authenticated:
            return (
                Article.objects.select_related(
                    "author",
                    "publisher",
                    "newsletter",
                )
                .filter(Q(status=Article.STATUS_APPROVED) | Q(author=user))
                .distinct()
            )

        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_APPROVED)

    def perform_create(self, serializer):
        """Create an article for the current journalist user."""
        user = self.request.user

        if not user.is_journalist:
            raise PermissionDenied("Only journalists can create articles.")

        article = serializer.save(author=user)

        if article.status == Article.STATUS_APPROVED:
            article.status = Article.STATUS_PENDING
            article.approved_by = None
            article.save()


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for retrieving, updating, and deleting a single article."""

    serializer_class = ArticleSerializer

    def get_queryset(self):
        """Return articles accessible to the current user."""
        user = self.request.user

        if user.is_authenticated and getattr(user, "is_editor", False):
            return Article.objects.select_related(
                "author",
                "publisher",
                "newsletter",
            ).all()

        if user.is_authenticated:
            return (
                Article.objects.select_related(
                    "author",
                    "publisher",
                    "newsletter",
                )
                .filter(Q(status=Article.STATUS_APPROVED) | Q(author=user))
                .distinct()
            )

        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_APPROVED)

    def get_permissions(self):
        """Return permissions based on the request method."""
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def update(self, request, *args, **kwargs):
        """
        Update an article.

        Editors can edit any article. Journalists can edit only their own
        articles, and approved edits are sent back to pending review.
        """
        article = self.get_object()

        if request.user.is_reader:
            raise PermissionDenied("Readers cannot edit articles.")

        if request.user.is_editor:
            return super().update(request, *args, **kwargs)

        if request.user.is_journalist:
            if article.author != request.user:
                raise PermissionDenied("Journalists can only edit their own articles.")

            response = super().update(request, *args, **kwargs)
            article.refresh_from_db()

            if article.status == Article.STATUS_APPROVED:
                article.status = Article.STATUS_PENDING
                article.approved_by = None
                article.save()

            return response

        raise PermissionDenied("You do not have permission to edit this article.")

    def destroy(self, request, *args, **kwargs):
        """Allow only editors to delete articles."""
        if not request.user.is_editor:
            raise PermissionDenied("Only editors can delete articles.")
        return super().destroy(request, *args, **kwargs)


class SubscribedArticlesAPIView(generics.ListAPIView):
    """API endpoint for listing a reader's subscribed approved articles."""

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return subscribed approved articles for the current reader."""
        user = self.request.user

        if not user.is_reader:
            raise PermissionDenied("Only readers can view subscribed articles.")

        return user.subscribed_articles.filter(
            status=Article.STATUS_APPROVED
        ).select_related("author", "publisher", "newsletter")


class PendingArticlesAPIView(generics.ListAPIView):
    """API endpoint for listing pending articles for editors."""

    serializer_class = ArticleSerializer
    permission_classes = [permissions.IsAuthenticated, IsEditor]

    def get_queryset(self):
        """Return all pending articles."""
        return Article.objects.select_related(
            "author",
            "publisher",
            "newsletter",
        ).filter(status=Article.STATUS_PENDING)
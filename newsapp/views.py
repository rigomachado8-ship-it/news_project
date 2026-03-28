from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .api_permissions import IsEditor, IsJournalistOrReadOnly
from .forms import ArticleForm, CustomLoginForm, CustomUserRegisterForm
from .models import Article, CustomUser, Publisher
from .serializers import ArticleSerializer


class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm
    template_name = "login.html"


def register_view(request):
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
    view = CustomLoginView.as_view()
    return view(request)


def article_list(request):
    articles = Article.objects.select_related("author", "publisher").filter(
        status=Article.STATUS_APPROVED
    )
    return render(request, "article_list.html", {"articles": articles})


def article_detail(request, pk):
    article = get_object_or_404(
        Article.objects.select_related("author", "publisher", "newsletter"),
        pk=pk,
    )

    if article.status != Article.STATUS_APPROVED:
        if not request.user.is_authenticated:
            messages.error(request, "You must log in to view this article.")
            return redirect("login")

        if request.user != article.author and not request.user.is_editor:
            messages.error(request, "You do not have permission to view this article.")
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
    context = {
        "my_articles": Article.objects.filter(author=request.user),
        "pending_articles": Article.objects.filter(status=Article.STATUS_PENDING),
    }
    return render(request, "dashboard.html", context)


@login_required
def create_article(request):
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
    article = get_object_or_404(Article, pk=pk)

    if request.user.is_reader:
        messages.error(request, "Readers cannot edit articles.")
        return redirect("dashboard")

    if request.user.is_journalist and request.user != article.author:
        messages.error(request, "Journalists can only edit their own articles.")
        return redirect("dashboard")

    if not (request.user.is_editor or request.user == article.author):
        messages.error(request, "You do not have permission to edit this article.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            updated_article = form.save(commit=False)

            if request.user.is_journalist and updated_article.status == Article.STATUS_APPROVED:
                updated_article.status = Article.STATUS_PENDING
                updated_article.approved_by = None

            if request.user.is_editor and updated_article.status == Article.STATUS_APPROVED:
                updated_article.approved_by = request.user

            updated_article.save()
            messages.success(request, "Article updated successfully.")
            return redirect("article_detail", pk=updated_article.pk)
    else:
        form = ArticleForm(instance=article, user=request.user)

    return render(request, "edit_article.html", {"form": form, "article": article})


@login_required
def approve_articles(request):
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
            messages.success(request, f'"{article.title}" was approved.')

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
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can view subscribed articles.")

    articles = request.user.subscribed_articles.filter(
        status=Article.STATUS_APPROVED
    ).select_related("author", "publisher", "newsletter")

    return render(request, "subscribed_articles.html", {"articles": articles})


@login_required
def subscribe_article(request, pk):
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to articles.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.add(article)
    messages.success(request, f'You subscribed to "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def unsubscribe_article(request, pk):
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can manage article subscriptions.")

    article = get_object_or_404(Article, pk=pk, status=Article.STATUS_APPROVED)
    request.user.subscribed_articles.remove(article)
    messages.success(request, f'You unsubscribed from "{article.title}".')
    return redirect("article_detail", pk=pk)


@login_required
def subscribe_publisher(request, publisher_id):
    if not request.user.is_reader:
        return HttpResponseForbidden("Only readers can subscribe to publishers.")

    publisher = get_object_or_404(Publisher, pk=publisher_id)
    request.user.subscribed_publishers.add(publisher)
    messages.success(request, f"You subscribed to {publisher.name}.")
    return redirect("article_list")


@login_required
def subscribe_journalist(request, user_id):
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

        if user.is_authenticated and getattr(user, "is_editor", False):
            return Article.objects.select_related("author", "publisher", "newsletter").all()

        if user.is_authenticated:
            return Article.objects.select_related("author", "publisher", "newsletter").filter(
                Q(status=Article.STATUS_APPROVED) | Q(author=user)
            ).distinct()

        return Article.objects.select_related("author", "publisher", "newsletter").filter(
            status=Article.STATUS_APPROVED
        )

    def perform_create(self, serializer):
        user = self.request.user

        if not user.is_journalist:
            raise PermissionDenied("Only journalists can create articles.")

        article = serializer.save(author=user)

        if article.status == Article.STATUS_APPROVED:
            article.status = Article.STATUS_PENDING
            article.save()


class ArticleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated and getattr(user, "is_editor", False):
            return Article.objects.select_related("author", "publisher", "newsletter").all()

        if user.is_authenticated:
            return Article.objects.select_related("author", "publisher", "newsletter").filter(
                Q(status=Article.STATUS_APPROVED) | Q(author=user)
            ).distinct()

        return Article.objects.select_related("author", "publisher", "newsletter").filter(
            status=Article.STATUS_APPROVED
        )

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def update(self, request, *args, **kwargs):
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
        if not request.user.is_editor:
            raise PermissionDenied("Only editors can delete articles.")
        return super().destroy(request, *args, **kwargs)


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
        return Article.objects.select_related("author", "publisher", "newsletter").filter(
            status=Article.STATUS_PENDING
        )
from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("article/<int:pk>/", views.article_detail, name="article_detail"),
    path("article/<int:pk>/edit/", views.edit_article, name="edit_article"),
    path("article/<int:pk>/delete/", views.delete_article, name="delete_article"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("create/", views.create_article, name="create_article"),
    path("editor/approve/", views.approve_articles, name="approve_articles"),
    path("subscriptions/", views.my_subscriptions, name="my_subscriptions"),
    path("subscriptions/articles/", views.subscribed_articles, name="subscribed_articles"),
    path("subscribe/article/<int:pk>/", views.subscribe_article, name="subscribe_article"),
    path("unsubscribe/article/<int:pk>/", views.unsubscribe_article, name="unsubscribe_article"),
    path("subscribe/publisher/<int:publisher_id>/", views.subscribe_publisher, name="subscribe_publisher"),
    path("subscribe/journalist/<int:user_id>/", views.subscribe_journalist, name="subscribe_journalist"),
    path("profiles/<int:pk>/", views.profile_detail, name="profile_detail"),
    path("profiles/<int:pk>/edit/", views.profile_update, name="profile_update"),
    path("profiles/<int:pk>/delete/", views.profile_delete, name="profile_delete"),
    path("api/articles/", views.ArticleListCreateAPIView.as_view(), name="api_article_list_create"),
    path("api/articles/<int:pk>/", views.ArticleDetailAPIView.as_view(), name="api_article_detail"),
    path("api/articles/subscribed/", views.SubscribedArticlesAPIView.as_view(), name="api_subscribed_articles"),
    path("api/articles/pending/", views.PendingArticlesAPIView.as_view(), name="api_pending_articles"),
    path("api/profiles/<int:pk>/", views.ProfileDetailAPIView.as_view(), name="api_profile_detail"),
]
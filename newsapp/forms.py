"""
Forms for user authentication, registration, and article creation/editing.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Article, CustomUser


class CustomUserRegisterForm(UserCreationForm):
    """Form for registering a new user with a selected role."""

    class Meta:
        """Metadata for the registration form."""

        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]


class CustomLoginForm(AuthenticationForm):
    """Authentication form with explicit username and password fields."""

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""

    class Meta:
        """Metadata for the article form."""

        model = Article
        fields = ["title", "content", "publisher", "newsletter", "status"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        """Limit available status choices for journalists."""
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_journalist:
            self.fields["status"].choices = [
                (Article.STATUS_DRAFT, "Draft"),
                (Article.STATUS_PENDING, "Pending Review"),
            ]

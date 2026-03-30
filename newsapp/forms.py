"""
Forms for user authentication, registration, and article creation/editing.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class CustomUserRegisterForm(UserCreationForm):
    """Form for registering a new user with a selected role."""

    email = forms.EmailField(required=True)

    class Meta:
        """Metadata for the registration form."""

        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]

    def clean_email(self):
        """Prevent registration with a duplicate email address."""
        email = self.cleaned_data.get("email", "").strip().lower()

        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email address already exists."
            )

        return email

    def save(self, commit=True):
        """Save the user with a normalised email address."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()

        if commit:
            user.save()

        return user


class CustomLoginForm(AuthenticationForm):
    """Authentication form with explicit username and password fields."""

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class PublisherForm(forms.ModelForm):
    """Form for creating and editing publishers."""

    class Meta:
        """Metadata for the publisher form."""

        model = Publisher
        fields = ["name", "description"]


class NewsletterForm(forms.ModelForm):
    """Form for creating and editing newsletters."""

    class Meta:
        """Metadata for the newsletter form."""

        model = Newsletter
        fields = ["title", "description"]


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
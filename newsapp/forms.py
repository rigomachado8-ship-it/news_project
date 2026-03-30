"""
Forms for user authentication, registration, profile management,
publisher/newsletter creation, and article creation/editing.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Article, CustomUser, Newsletter, Publisher


class CustomUserRegisterForm(UserCreationForm):
    """Form for registering a new user with a selected role."""

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]

    def clean_email(self):
        """Prevent duplicate email registration."""
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class CustomLoginForm(AuthenticationForm):
    """Custom login form."""

    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ProfileUpdateForm(forms.ModelForm):
    """Profile update form with role protection."""

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role"]

    def __init__(self, *args, **kwargs):
        acting_user = kwargs.pop("acting_user", None)
        super().__init__(*args, **kwargs)

        if not acting_user or not acting_user.is_editor:
            self.fields["role"].disabled = True
            self.fields["role"].help_text = "Only editors can change user roles."

    def clean_email(self):
        """Prevent duplicate emails during profile update."""
        email = self.cleaned_data["email"].strip().lower()
        queryset = CustomUser.objects.filter(email__iexact=email)

        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class PublisherForm(forms.ModelForm):
    """Form for creating a publisher."""

    class Meta:
        model = Publisher
        fields = ["name", "description"]


class NewsletterForm(forms.ModelForm):
    """Form for creating a newsletter."""

    class Meta:
        model = Newsletter
        fields = ["title", "description"]


class ArticleForm(forms.ModelForm):
    """Form for creating and editing articles."""

    class Meta:
        model = Article
        fields = ["title", "content", "publisher", "newsletter", "status"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 12}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user and user.is_journalist:
            self.fields["status"].choices = [
                (Article.STATUS_DRAFT, "Draft"),
                (Article.STATUS_PENDING, "Pending Review"),
            ]
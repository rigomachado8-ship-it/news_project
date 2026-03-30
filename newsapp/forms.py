from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Article, CustomUser


class CustomUserRegisterForm(UserCreationForm):
    """Registration form for new users."""

    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]


class CustomLoginForm(AuthenticationForm):
    """Login form."""

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
            self.fields["role"].help_text = (
                "Only editors can change user roles."
            )


class ArticleForm(forms.ModelForm):
    """Article create/update form."""

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
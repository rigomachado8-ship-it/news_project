from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Article, CustomUser


class CustomUserRegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "role", "password1", "password2"]


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ["title", "content", "publisher", "newsletter", "status"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # Journalists should submit for review, not approve their own content.
        if user and user.is_journalist:
            self.fields["status"].choices = [
                (Article.STATUS_DRAFT, "Draft"),
                (Article.STATUS_PENDING, "Pending Review"),
            ]
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Article, Newsletter


@receiver(post_migrate)
def create_groups_and_permissions(sender, **kwargs):
    if sender.name != 'newsapp':
        return

    reader_group, _ = Group.objects.get_or_create(name='Reader')
    editor_group, _ = Group.objects.get_or_create(name='Editor')
    journalist_group, _ = Group.objects.get_or_create(name='Journalist')

    article_ct = ContentType.objects.get_for_model(Article)
    newsletter_ct = ContentType.objects.get_for_model(Newsletter)

    # Article permissions
    view_article = Permission.objects.get(codename='view_article', content_type=article_ct)
    add_article = Permission.objects.get(codename='add_article', content_type=article_ct)
    change_article = Permission.objects.get(codename='change_article', content_type=article_ct)
    delete_article = Permission.objects.get(codename='delete_article', content_type=article_ct)

    # Newsletter permissions
    view_newsletter = Permission.objects.get(codename='view_newsletter', content_type=newsletter_ct)
    add_newsletter = Permission.objects.get(codename='add_newsletter', content_type=newsletter_ct)
    change_newsletter = Permission.objects.get(codename='change_newsletter', content_type=newsletter_ct)
    delete_newsletter = Permission.objects.get(codename='delete_newsletter', content_type=newsletter_ct)

    # Reader: view only
    reader_group.permissions.set([
        view_article,
        view_newsletter,
    ])

    # Editor: view, update, delete
    editor_group.permissions.set([
        view_article,
        change_article,
        delete_article,
        view_newsletter,
        change_newsletter,
        delete_newsletter,
    ])

    # Journalist: create, view, update, delete
    journalist_group.permissions.set([
        add_article,
        view_article,
        change_article,
        delete_article,
        add_newsletter,
        view_newsletter,
        change_newsletter,
        delete_newsletter,
    ])
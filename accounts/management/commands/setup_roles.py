from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from website import models as m

# Models a Content Manager may fully manage (add/change/delete/publish).
CONTENT_MODELS = [
    m.Church, m.ChurchImage, m.Ministry, m.MinistryImage, m.Event, m.EventImage,
    m.GalleryAlbum, m.GalleryImage, m.BlogPost, m.BlogCategory, m.BlogTag,
    m.BibleSchoolCourse, m.Faculty, m.Leader, m.BeliefStatement, m.TimelineEvent,
    m.Statistic, m.FlatPage, m.MediaAsset, m.MenuItem, m.ContactMessage,
]

# Singletons/settings a Content Manager may edit but that only a Super Admin
# should be able to touch structurally.
SETTINGS_MODELS = [
    m.SiteSettings, m.HeroSection, m.HomeAboutSection, m.AboutPage,
    m.BibleSchool, m.CallToAction,
]


class Command(BaseCommand):
    help = "Create the Content Manager and Editor groups with real Django permissions."

    def handle(self, *args, **options):
        content_manager, _ = Group.objects.get_or_create(name="Content Manager")
        editor, _ = Group.objects.get_or_create(name="Editor")

        cm_perms = []
        for model in CONTENT_MODELS + SETTINGS_MODELS:
            cm_perms += list(Permission.objects.filter(
                content_type__app_label=model._meta.app_label,
                content_type__model=model._meta.model_name,
            ))
        content_manager.permissions.set(cm_perms)

        # Editors can add and change content, but not delete it, and cannot
        # touch site-wide settings/singletons at all.
        editor_perms = []
        for model in CONTENT_MODELS:
            editor_perms += list(Permission.objects.filter(
                content_type__app_label=model._meta.app_label,
                content_type__model=model._meta.model_name,
                codename__in=[
                    f"add_{model._meta.model_name}",
                    f"change_{model._meta.model_name}",
                    f"view_{model._meta.model_name}",
                ],
            ))
        editor.permissions.set(editor_perms)

        self.stdout.write(self.style.SUCCESS(
            f"Content Manager: {content_manager.permissions.count()} permissions. "
            f"Editor: {editor.permissions.count()} permissions."
        ))

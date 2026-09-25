from .models import MenuItem, SiteSettings


def site_settings(request):
    settings_obj = getattr(request, "site_settings", None) or SiteSettings.load()
    return {"site_settings": settings_obj}


def main_menu(request):
    items = MenuItem.objects.filter(is_active=True, parent__isnull=True).prefetch_related("children")
    return {"main_menu": items}

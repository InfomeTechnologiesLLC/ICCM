from .models import SiteSettings


class SiteSettingsMiddleware:
    """Attaches the singleton SiteSettings row to every request so views
    and templates can reach it as request.site_settings without an extra
    query per template (the context processor reuses this)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.site_settings = SiteSettings.load()
        return self.get_response(request)

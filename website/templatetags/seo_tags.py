"""Meta, Open Graph and Twitter card details for every public page.

Where each value comes from, first match wins:

  Detail pages (a blog post, event, ministry, church, album, flat page):
      the item's own "Google search & social sharing" fields
      -> the item's own summary text and main photo
      -> Website Settings defaults

  Main pages (Home, About, Ministries, ICTC, Events, Gallery, Blog, Contact, Churches):
      CMS -> SEO & sharing -> that page
      -> Website Settings defaults

Used in base.html as {% page_seo as seo %}.
"""

import re

from django import template
from django.utils.html import strip_tags
from django.utils.text import Truncator

register = template.Library()

# url name -> context variable holding the item shown on that page
DETAIL_PAGES = {
    "blog_detail": "post",
    "event_detail": "event",
    "ministry_detail": "ministry",
    "church_detail": "church",
    "gallery_album": "album",
    "flatpage": "page",
}

NAME_FIELDS = ("seo_title", "title", "name")
SUMMARY_FIELDS = ("excerpt", "short_description", "description", "content")
IMAGE_FIELDS = ("featured_image", "main_image", "image", "cover_image")


def _first(obj, fields):
    for name in fields:
        val = getattr(obj, name, None)
        if val:
            return val
    return None


def _clean(text, limit):
    text = re.sub(r"\s+", " ", strip_tags(str(text or ""))).strip()
    return Truncator(text).chars(limit) if text else ""


def _file_url(f):
    try:
        return f.url if f else ""
    except ValueError:
        return ""


@register.simple_tag(takes_context=True)
def page_seo(context):
    seo = {
        "title": "", "default_title": "", "description": "", "keywords": "",
        "og_title": "", "og_description": "", "image": "", "image_alt": "",
        "type": "website", "url": "", "canonical": "", "robots": "index, follow",
        "site_name": "", "published_time": "", "modified_time": "", "google_verification": "",
    }
    request = context.get("request")
    site = context.get("site_settings")
    if request is None or site is None:      # e.g. the plain 500 error page
        return seo

    try:
        from website.models import PageSEO

        match = getattr(request, "resolver_match", None)
        url_name = match.url_name if match else ""
        site_name = site.site_name or ""
        seo["site_name"] = site_name
        seo["google_verification"] = site.google_site_verification
        seo["canonical"] = seo["url"] = request.build_absolute_uri(request.path)

        title = description = keywords = og_title = og_description = ""
        image = None

        obj_key = DETAIL_PAGES.get(url_name)
        obj = context.get(obj_key) if obj_key else None

        if obj is not None:
            name = _first(obj, ("title", "name")) or ""
            seo["default_title"] = f"{name} — {site_name}" if name else site_name
            title = getattr(obj, "seo_title", "")
            description = getattr(obj, "seo_description", "") or _first(obj, SUMMARY_FIELDS) or ""
            image = getattr(obj, "seo_image", None) or _first(obj, IMAGE_FIELDS)
            seo["image_alt"] = name
            if url_name == "blog_detail":
                seo["type"] = "article"
                if getattr(obj, "published_at", None):
                    seo["published_time"] = obj.published_at.isoformat()
                if getattr(obj, "updated_at", None):
                    seo["modified_time"] = obj.updated_at.isoformat()
        else:
            row = PageSEO.objects.filter(page=url_name).first() if url_name else None
            label = dict(PageSEO.PAGE_CHOICES).get(url_name, "")
            seo["default_title"] = (site.default_seo_title or site_name) if url_name == "home" or not label \
                else f"{label} — {site_name}"
            if row:
                title = row.meta_title
                description = row.meta_description
                keywords = row.meta_keywords
                og_title = row.og_title
                og_description = row.og_description
                image = row.og_image or None
                if row.noindex:
                    seo["robots"] = "noindex, nofollow"
            if url_name == "home" and not title:
                title = site.default_seo_title

        description = description or site.default_seo_description or site.description
        image = image or site.default_seo_image or site.logo

        seo["title"] = _clean(title, 70)
        seo["description"] = _clean(description, 160)
        seo["keywords"] = _clean(keywords or site.default_seo_keywords, 255)
        seo["og_title"] = _clean(og_title, 95) or seo["title"] or seo["default_title"]
        seo["og_description"] = _clean(og_description, 200) or seo["description"]
        img_url = _file_url(image)
        if img_url:
            seo["image"] = request.build_absolute_uri(img_url)
            seo["image_alt"] = seo["image_alt"] or seo["og_title"]
    except Exception:  # never let SEO details break a page
        pass
    return seo

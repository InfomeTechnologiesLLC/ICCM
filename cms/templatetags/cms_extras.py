from django import template
from django.urls import NoReverseMatch, reverse

register = template.Library()


@register.filter
def attr(obj, dotted_path):
    """Resolve a dotted attribute path at render time, e.g. 'images.count'
    or 'get_region_display', calling any callables along the way. Used by
    the generic CMS list table so one template can drive every model."""
    value = obj
    for part in dotted_path.split("."):
        if value is None:
            return ""
        value = getattr(value, part, "")
        if callable(value):
            try:
                value = value()
            except TypeError:
                pass
    return value


# ---------------------------------------------------------------------------
# Plain-language help for first-time users
# ---------------------------------------------------------------------------

# section key -> (what this screen is for, where it appears, public URL name or path)
SECTION_HELP = {
    "dashboard": ("Start here. Pick a task below, or use the menu on the left.", "", ""),
    "settings": ("Your organisation's name, logo, contact details (email, phone, address), "
                 "footer text and social media links.",
                 "The top and bottom of every page, and the Contact page.", "website:contact"),
    "menuitem": ("The links in the menu at the top of the website. Untick “Show on the website” "
                 "to hide a link without deleting it.", "The top of every page.", "website:home"),
    "hero": ("The large banner with a photo that visitors see first.",
             "The top of the home page.", "website:home"),
    "heroslide": ("The photos that slide one after another behind the banner heading. "
                  "Add two or more to make the banner a slider; with one photo it stays still. "
                  "Use wide landscape photos (at least 1600 pixels wide).",
                  "The top of the home page.", "website:home"),
    "home_about": ("The short “About us” box with a photo, below the banner.",
                   "The home page, under the banner.", "website:home"),
    "statistic": ("The numbers strip, for example “10 Local churches”.",
                  "The home page, just below the banner.", "website:home"),
    "cta": ("The green “Support the Mission” box that asks visitors to partner with you.",
            "Near the bottom of the home page.", "website:home"),
    "about_page": ("The main text and photos of the About page.", "The About page.", "website:about"),
    "leader": ("People shown in the Leadership section, with photo and role.",
               "The About page, Leadership section.", "website:about"),
    "belief": ("The statements in “What We Believe”.",
               "The About page, What We Believe section.", "website:about"),
    "timeline": ("Important years in the history of the mission.",
                 "The About page, Timeline section.", "website:about"),
    "church": ("Your local churches, with address, service times and photos.",
               "The Churches page.", "website:church_list"),
    "ministry": ("Each ministry has its own page with text, photo and meeting details.",
                 "The Ministries page. Highlighted ones also appear on the home page.",
                 "website:ministry_list"),
    "event": ("Upcoming gatherings and programmes. Past events move to “Past” automatically.",
              "The Events page, and the home page.", "website:event_list"),
    "album": ("Photo albums. Create an album first, then add photos to it in “All Photos”.",
              "The Gallery page.", "website:gallery"),
    "image": ("Every photo in the gallery. Choose an album and a category for each photo.",
              "The Gallery page, and the home page.", "website:gallery"),
    "post": ("News articles and reports. Set Visibility to Published to show one on the website.",
             "The Blog page, and the home page.", "website:blog_list"),
    "category": ("Groups for blog posts, such as “Ministry” or “News”.", "The Blog page.",
                 "website:blog_list"),
    "bible_school": ("The text, photos, admissions and requirements for ICTC.",
                     "The ICTC page.", "website:bible_school"),
    "course": ("The study programmes offered at ICTC.", "The ICTC page, Courses section.",
               "website:bible_school"),
    "faculty": ("ICTC teachers, with photo and subject.", "The ICTC page, Faculty section.",
                "website:bible_school"),
    "message": ("Messages sent by visitors through the Contact page form.", "", ""),
    "user": ("People who can log in to this CMS.", "", ""),
}

SUFFIXES = ("_list", "_add", "_edit", "_delete", "_detail")


@register.filter
def section(url_name):
    """'ministry_edit' -> 'ministry'. Used to highlight the current menu item."""
    url_name = url_name or ""
    for suffix in SUFFIXES:
        if url_name.endswith(suffix):
            return url_name[: -len(suffix)]
    return url_name


@register.simple_tag(takes_context=True)
def section_help(context):
    request = context.get("request")
    match = getattr(request, "resolver_match", None)
    key = section(match.url_name if match else "")
    what, where, target = SECTION_HELP.get(key, ("", "", ""))
    url = ""
    if target:
        try:
            url = reverse(target)
        except NoReverseMatch:
            url = ""
    return {"what": what, "where": where, "url": url}


# field name -> (friendly label, help text). Applied to every CMS form.
FIELD_TEXT = {
    "status": ("Visibility", "Published = shown on the website. Draft = saved but hidden. "
                             "Archived = hidden, kept for records."),
    "is_featured": ("Highlight this", "Highlighted items are shown first and may appear on the home page."),
    "is_active": ("Show on the website", "Untick to hide without deleting."),
    "is_completed": ("This event is over", "Tick after the event has happened."),
    "order": ("Position", "Lower numbers are shown first (0 comes before 1)."),
    "slug": ("Web address", "Leave empty. It is created automatically from the name."),
    "icon": ("Icon", "Name of a small icon from fonts.google.com/icons, for example: church, groups, school."),
    "short_description": (None, "One or two sentences, shown on cards and lists."),
    "excerpt": ("Short summary", "One or two sentences, shown in the list of posts."),
    "description": (None, "The main text."),
    "content": ("Article text", None),
    "button_url": ("Button link", "Where the button goes, for example /about/ or /contact/"),
    "button2_url": ("Second button link", "Where the button goes, for example /ministries/"),
    "button_text": (None, "Leave empty to hide the button."),
    "button2_text": ("Second button text", "Leave empty to hide the button."),
    "open_in_new_tab": ("Open in a new browser tab", None),
    "parent": ("Show under", "Choose a menu item to make this a sub-link. Leave empty for a main link."),
    "url": ("Link", "A page on this site, for example /about/, or a full address starting with https://"),
    "google_maps_url": ("Google Maps link", "Open the place in Google Maps, click Share, and paste the link here."),
    "whatsapp_number": ("WhatsApp number", "Country code and number, no spaces or + sign, for example 919876543210."),
    "utility_bar_text": ("Top strip text", "The short line of text at the very top of every page."),
    "footer_hours": ("Regular gatherings", "Shown in the footer. Put each item on its own line."),
    "published_at": ("Publish date", None),
    "author_name": ("Author name shown", "Leave empty to use your account name."),
    "tag": ("Photo category", "Used by the filter buttons on the Gallery page."),
    "album": (None, "The album this photo belongs to."),
    "value": ("Number", "For example 10, 1996 or 150+"),
    "year": (None, "A year, or a word such as “Today”."),
}

IMAGE_HELP = "JPG or PNG photo. Wide (landscape) photos look best."


@register.filter
def nice_label(field):
    label, _ = FIELD_TEXT.get(field.name, (None, None))
    return label or field.label


@register.filter
def nice_help(field):
    _, help_text = FIELD_TEXT.get(field.name, (None, None))
    if help_text:
        return help_text
    if field.help_text:
        return field.help_text
    if field.widget_type in ("clearablefile", "file"):
        return IMAGE_HELP
    return ""


@register.filter
def is_seo(field):
    return field.name.startswith("seo_") or field.name.startswith("default_seo_")


THUMB_FIELDS = ("image", "main_image", "featured_image", "cover_image", "photo", "background_image")


@register.filter
def thumb(obj):
    """URL of the first photo on an object, for list previews."""
    for name in THUMB_FIELDS:
        f = getattr(obj, name, None)
        if f and hasattr(f, "url"):
            try:
                return f.url
            except ValueError:
                continue
    return ""
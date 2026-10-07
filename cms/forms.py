from django import forms
from django.contrib.auth.forms import AuthenticationForm

from website import models as m


class BootstrapModelForm(forms.ModelForm):
    """Adds Bootstrap classes to every widget automatically so each CMS
    form doesn't have to restate them field by field."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = (existing + " form-check-input").strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (existing + " form-select").strip()
            elif isinstance(widget, (forms.FileInput, forms.ClearableFileInput)):
                widget.attrs["class"] = (existing + " form-control").strip()
            else:
                widget.attrs["class"] = (existing + " form-control").strip()


class CMSLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control", "autofocus": True})
        self.fields["password"].widget.attrs.update({"class": "form-control"})


class SiteSettingsForm(BootstrapModelForm):
    class Meta:
        model = m.SiteSettings
        exclude = []


class HeroSectionForm(BootstrapModelForm):
    class Meta:
        model = m.HeroSection
        exclude = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["background_image"].help_text = (
            "Only used when there are no banner slides. To change the sliding photos, "
            "go to Home page → Banner slides.")


class HeroSlideForm(BootstrapModelForm):
    class Meta:
        model = m.HeroSlide
        fields = ["image", "alt_text", "order", "is_active"]


class HomeAboutSectionForm(BootstrapModelForm):
    class Meta:
        model = m.HomeAboutSection
        exclude = []


class CallToActionForm(BootstrapModelForm):
    class Meta:
        model = m.CallToAction
        exclude = []


class AboutPageForm(BootstrapModelForm):
    class Meta:
        model = m.AboutPage
        exclude = []


class BibleSchoolForm(BootstrapModelForm):
    class Meta:
        model = m.BibleSchool
        exclude = []


class ChurchForm(BootstrapModelForm):
    class Meta:
        model = m.Church
        exclude = ["slug", "created_by", "updated_by"]


class MinistryForm(BootstrapModelForm):
    class Meta:
        model = m.Ministry
        exclude = ["slug", "created_by", "updated_by"]


class EventForm(BootstrapModelForm):
    class Meta:
        model = m.Event
        exclude = ["slug", "created_by", "updated_by"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class GalleryAlbumForm(BootstrapModelForm):
    class Meta:
        model = m.GalleryAlbum
        exclude = ["slug", "created_by", "updated_by"]


class GalleryImageForm(BootstrapModelForm):
    class Meta:
        model = m.GalleryImage
        fields = ["album", "image", "title", "description", "tag", "order"]


class GalleryVideoForm(BootstrapModelForm):
    class Meta:
        model = m.GalleryVideo
        fields = ["title", "album", "youtube_url", "video_file", "thumbnail", "description",
                  "order", "is_active"]
        widgets = {
            "youtube_url": forms.URLInput(attrs={"placeholder": "https://www.youtube.com/watch?v=..."}),
            "video_file": forms.ClearableFileInput(attrs={"accept": "video/mp4,video/webm,video/quicktime,.m4v"}),
        }


class PageSEOForm(BootstrapModelForm):
    class Meta:
        model = m.PageSEO
        exclude = ["page"]
        widgets = {
            "meta_description": forms.Textarea(attrs={"rows": 3, "maxlength": 160}),
            "og_description": forms.Textarea(attrs={"rows": 3, "maxlength": 200}),
        }


class BlogPostForm(BootstrapModelForm):
    class Meta:
        model = m.BlogPost
        exclude = ["slug", "created_by", "updated_by", "author"]
        widgets = {
            "published_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }


class BlogCategoryForm(BootstrapModelForm):
    class Meta:
        model = m.BlogCategory
        exclude = ["slug"]


class BibleSchoolCourseForm(BootstrapModelForm):
    class Meta:
        model = m.BibleSchoolCourse
        fields = "__all__"


class FacultyForm(BootstrapModelForm):
    class Meta:
        model = m.Faculty
        fields = "__all__"


class LeaderForm(BootstrapModelForm):
    class Meta:
        model = m.Leader
        fields = "__all__"


class BeliefStatementForm(BootstrapModelForm):
    class Meta:
        model = m.BeliefStatement
        fields = "__all__"


class TimelineEventForm(BootstrapModelForm):
    class Meta:
        model = m.TimelineEvent
        fields = "__all__"


class StatisticForm(BootstrapModelForm):
    class Meta:
        model = m.Statistic
        fields = "__all__"


class MenuItemForm(BootstrapModelForm):
    class Meta:
        model = m.MenuItem
        fields = "__all__"


class MediaAssetForm(BootstrapModelForm):
    class Meta:
        model = m.MediaAsset
        fields = ["file", "title"]

from django.contrib import admin

from . import models as m


@admin.register(m.SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not m.SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "parent", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)


@admin.register(m.HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not m.HeroSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.HomeAboutSection)
class HomeAboutSectionAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not m.HomeAboutSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.Statistic)
class StatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "order")
    list_editable = ("value", "order")


@admin.register(m.CallToAction)
class CallToActionAdmin(admin.ModelAdmin):
    list_display = ("key", "heading")


@admin.register(m.AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not m.AboutPage.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.BeliefStatement)
class BeliefStatementAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(m.TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ("year", "title", "order")
    list_editable = ("order",)


@admin.register(m.Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "is_active", "order")
    list_editable = ("order", "is_active")


class ChurchImageInline(admin.TabularInline):
    model = m.ChurchImage
    extra = 1


@admin.register(m.Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = ("name", "region", "status", "is_featured", "order")
    list_filter = ("region", "status", "is_featured")
    search_fields = ("name", "city", "pastor")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ChurchImageInline]


class MinistryImageInline(admin.TabularInline):
    model = m.MinistryImage
    extra = 1


@admin.register(m.Ministry)
class MinistryAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "is_featured", "order")
    list_filter = ("status", "is_featured")
    search_fields = ("name", "leader")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MinistryImageInline]


@admin.register(m.BibleSchool)
class BibleSchoolAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not m.BibleSchool.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(m.BibleSchoolCourse)
class BibleSchoolCourseAdmin(admin.ModelAdmin):
    list_display = ("title", "duration", "order")
    list_editable = ("order",)


@admin.register(m.Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "order")


class EventImageInline(admin.TabularInline):
    model = m.EventImage
    extra = 1


@admin.register(m.Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "status", "is_featured", "is_completed")
    list_filter = ("status", "is_featured", "is_completed")
    search_fields = ("name", "venue", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [EventImageInline]


class GalleryImageInline(admin.TabularInline):
    model = m.GalleryImage
    extra = 1


@admin.register(m.GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "is_featured", "order")
    list_filter = ("status", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [GalleryImageInline]


@admin.register(m.GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "album", "tag", "order")
    list_filter = ("tag", "album")


@admin.register(m.BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(m.BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(m.BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "is_featured", "published_at")
    list_filter = ("status", "is_featured", "category")
    search_fields = ("title", "excerpt", "content")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)


@admin.register(m.ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "reason", "status", "created_at")
    list_filter = ("status", "reason")
    search_fields = ("name", "email", "subject", "message")
    list_editable = ("status",)


@admin.register(m.NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "created_at")


@admin.register(m.PrayerListSignup)
class PrayerListSignupAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")


@admin.register(m.FlatPage)
class FlatPageAdmin(admin.ModelAdmin):
    list_display = ("title", "status")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(m.MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ("title", "file_type", "uploaded_by", "created_at")

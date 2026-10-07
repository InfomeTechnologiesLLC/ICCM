import csv

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect, render

from website import models as m
from . import forms as f


# ============================================================================
# Auth
# ============================================================================

class CMSLoginView(auth_views.LoginView):
    template_name = "cms/login.html"
    authentication_form = f.CMSLoginForm
    redirect_authenticated_user = True


class CMSLogoutView(auth_views.LogoutView):
    next_page = "cms:login"


# ============================================================================
# Dashboard
# ============================================================================

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "cms/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.localdate()
        ctx.update({
            "total_churches": m.Church.objects.count(),
            "total_ministries": m.Ministry.objects.count(),
            "total_events": m.Event.objects.count(),
            "upcoming_events": m.Event.objects.filter(is_completed=False, start_date__gte=today).count(),
            "total_posts": m.BlogPost.objects.count(),
            "published_posts": m.BlogPost.objects.filter(status="published").count(),
            "gallery_images": m.GalleryImage.objects.count(),
            "total_messages": m.ContactMessage.objects.count(),
            "unread_messages": m.ContactMessage.objects.filter(status="unread").count(),
            "gallery_videos": m.GalleryVideo.objects.count(),
            "prayer_signups": m.PrayerListSignup.objects.count(),
            "newsletter_signups": m.NewsletterSubscriber.objects.filter(is_active=True).count(),
            "recent_prayer": m.PrayerListSignup.objects.order_by("-created_at")[:5],
            "total_pages": m.FlatPage.objects.count(),
            "recent_messages": m.ContactMessage.objects.all()[:5],
            "recent_posts": m.BlogPost.objects.all()[:5],
        })
        return ctx


# ============================================================================
# Reusable generic CRUD (list / create / update / delete)
# ============================================================================

class CMSListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    template_name = "cms/generic_list.html"
    paginate_by = 20
    title = "Items"
    columns = []          # list of (label, attribute_path)
    add_url_name = None
    edit_url_name = None
    delete_url_name = None

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            "title": self.title, "columns": self.columns,
            "add_url_name": self.add_url_name, "edit_url_name": self.edit_url_name,
            "delete_url_name": self.delete_url_name,
        })
        return ctx


class CMSCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = "cms/generic_form.html"
    title = "Add item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        return ctx

    def form_valid(self, form):
        if hasattr(form.instance, "created_by_id"):
            form.instance.created_by = self.request.user
        if hasattr(form.instance, "updated_by_id"):
            form.instance.updated_by = self.request.user
        messages.success(self.request, f"{self.title.replace('Add ', '')} created.")
        return super().form_valid(form)


class CMSUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = "cms/generic_form.html"
    title = "Edit item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        return ctx

    def form_valid(self, form):
        if hasattr(form.instance, "updated_by_id"):
            form.instance.updated_by = self.request.user
        messages.success(self.request, "Saved.")
        return super().form_valid(form)


class CMSDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    template_name = "cms/generic_confirm_delete.html"
    title = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        return ctx

    def form_valid(self, form):
        messages.success(self.request, "Deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Churches
# ---------------------------------------------------------------------------

class ChurchListView(CMSListView):
    model = m.Church
    title = "Churches"
    permission_required = "website.view_church"
    columns = [("Name", "name"), ("Region", "get_region_display"), ("Status", "status"), ("Featured", "is_featured")]
    add_url_name = "cms:church_add"
    edit_url_name = "cms:church_edit"
    delete_url_name = "cms:church_delete"


class ChurchCreateView(CMSCreateView):
    model = m.Church
    form_class = f.ChurchForm
    title = "Add church"
    permission_required = "website.add_church"
    success_url = reverse_lazy("cms:church_list")


class ChurchUpdateView(CMSUpdateView):
    model = m.Church
    form_class = f.ChurchForm
    title = "Edit church"
    permission_required = "website.change_church"
    success_url = reverse_lazy("cms:church_list")


class ChurchDeleteView(CMSDeleteView):
    model = m.Church
    title = "church"
    permission_required = "website.delete_church"
    success_url = reverse_lazy("cms:church_list")


# ---------------------------------------------------------------------------
# Ministries
# ---------------------------------------------------------------------------

class MinistryListView(CMSListView):
    model = m.Ministry
    title = "Ministries"
    permission_required = "website.view_ministry"
    columns = [("Name", "name"), ("Leader", "leader"), ("Status", "status"), ("Featured", "is_featured")]
    add_url_name = "cms:ministry_add"
    edit_url_name = "cms:ministry_edit"
    delete_url_name = "cms:ministry_delete"


class MinistryCreateView(CMSCreateView):
    model = m.Ministry
    form_class = f.MinistryForm
    title = "Add ministry"
    permission_required = "website.add_ministry"
    success_url = reverse_lazy("cms:ministry_list")


class MinistryUpdateView(CMSUpdateView):
    model = m.Ministry
    form_class = f.MinistryForm
    title = "Edit ministry"
    permission_required = "website.change_ministry"
    success_url = reverse_lazy("cms:ministry_list")


class MinistryDeleteView(CMSDeleteView):
    model = m.Ministry
    title = "ministry"
    permission_required = "website.delete_ministry"
    success_url = reverse_lazy("cms:ministry_list")


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class EventListView(CMSListView):
    model = m.Event
    title = "Events"
    permission_required = "website.view_event"
    columns = [("Name", "name"), ("Start date", "start_date"), ("Status", "status"), ("Completed", "is_completed")]
    add_url_name = "cms:event_add"
    edit_url_name = "cms:event_edit"
    delete_url_name = "cms:event_delete"


class EventCreateView(CMSCreateView):
    model = m.Event
    form_class = f.EventForm
    title = "Add event"
    permission_required = "website.add_event"
    success_url = reverse_lazy("cms:event_list")


class EventUpdateView(CMSUpdateView):
    model = m.Event
    form_class = f.EventForm
    title = "Edit event"
    permission_required = "website.change_event"
    success_url = reverse_lazy("cms:event_list")


class EventDeleteView(CMSDeleteView):
    model = m.Event
    title = "event"
    permission_required = "website.delete_event"
    success_url = reverse_lazy("cms:event_list")


# ---------------------------------------------------------------------------
# Gallery
# ---------------------------------------------------------------------------

class GalleryAlbumListView(CMSListView):
    model = m.GalleryAlbum
    title = "Gallery Albums"
    permission_required = "website.view_galleryalbum"
    columns = [("Title", "title"), ("Status", "status"), ("Images", "images.count"), ("Featured", "is_featured")]
    add_url_name = "cms:album_add"
    edit_url_name = "cms:album_edit"
    delete_url_name = "cms:album_delete"


class GalleryAlbumCreateView(CMSCreateView):
    model = m.GalleryAlbum
    form_class = f.GalleryAlbumForm
    title = "Add album"
    permission_required = "website.add_galleryalbum"
    success_url = reverse_lazy("cms:album_list")


class GalleryAlbumUpdateView(CMSUpdateView):
    model = m.GalleryAlbum
    form_class = f.GalleryAlbumForm
    title = "Edit album"
    permission_required = "website.change_galleryalbum"
    success_url = reverse_lazy("cms:album_list")


class GalleryAlbumDeleteView(CMSDeleteView):
    model = m.GalleryAlbum
    title = "album"
    permission_required = "website.delete_galleryalbum"
    success_url = reverse_lazy("cms:album_list")


class GalleryImageListView(CMSListView):
    model = m.GalleryImage
    title = "Gallery Images"
    permission_required = "website.view_galleryimage"
    columns = [("Title", "title"), ("Album", "album"), ("Tag", "tag"), ("Order", "order")]
    add_url_name = "cms:image_add"
    edit_url_name = "cms:image_edit"
    delete_url_name = "cms:image_delete"


class GalleryImageCreateView(CMSCreateView):
    model = m.GalleryImage
    form_class = f.GalleryImageForm
    title = "Add gallery image"
    permission_required = "website.add_galleryimage"
    success_url = reverse_lazy("cms:image_list")


class GalleryImageUpdateView(CMSUpdateView):
    model = m.GalleryImage
    form_class = f.GalleryImageForm
    title = "Edit gallery image"
    permission_required = "website.change_galleryimage"
    success_url = reverse_lazy("cms:image_list")


class GalleryImageDeleteView(CMSDeleteView):
    model = m.GalleryImage
    title = "image"
    permission_required = "website.delete_galleryimage"
    success_url = reverse_lazy("cms:image_list")


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------

class BlogPostListView(CMSListView):
    model = m.BlogPost
    title = "Blog Posts"
    permission_required = "website.view_blogpost"
    columns = [("Title", "title"), ("Category", "category"), ("Status", "status"), ("Published", "published_at")]
    add_url_name = "cms:post_add"
    edit_url_name = "cms:post_edit"
    delete_url_name = "cms:post_delete"


class BlogPostCreateView(CMSCreateView):
    model = m.BlogPost
    form_class = f.BlogPostForm
    title = "Add blog post"
    permission_required = "website.add_blogpost"
    success_url = reverse_lazy("cms:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class BlogPostUpdateView(CMSUpdateView):
    model = m.BlogPost
    form_class = f.BlogPostForm
    title = "Edit blog post"
    permission_required = "website.change_blogpost"
    success_url = reverse_lazy("cms:post_list")


class BlogPostDeleteView(CMSDeleteView):
    model = m.BlogPost
    title = "post"
    permission_required = "website.delete_blogpost"
    success_url = reverse_lazy("cms:post_list")


class BlogCategoryListView(CMSListView):
    model = m.BlogCategory
    title = "Blog Categories"
    permission_required = "website.view_blogcategory"
    columns = [("Name", "name")]
    add_url_name = "cms:category_add"
    edit_url_name = "cms:category_edit"
    delete_url_name = "cms:category_delete"


class BlogCategoryCreateView(CMSCreateView):
    model = m.BlogCategory
    form_class = f.BlogCategoryForm
    title = "Add category"
    permission_required = "website.add_blogcategory"
    success_url = reverse_lazy("cms:category_list")


class BlogCategoryUpdateView(CMSUpdateView):
    model = m.BlogCategory
    form_class = f.BlogCategoryForm
    title = "Edit category"
    permission_required = "website.change_blogcategory"
    success_url = reverse_lazy("cms:category_list")


class BlogCategoryDeleteView(CMSDeleteView):
    model = m.BlogCategory
    title = "category"
    permission_required = "website.delete_blogcategory"
    success_url = reverse_lazy("cms:category_list")


# ---------------------------------------------------------------------------
# Small "one field list" content types: statistics, leaders, beliefs,
# timeline, courses, faculty, menu items
# ---------------------------------------------------------------------------

def _simple_crud(model, form_class, title, columns, url_base, perm_base):
    """Builds (list_view, create_view, update_view, delete_view) classes for
    a small supporting model, sharing the generic CMS templates."""

    list_view = type(f"{model.__name__}ListView", (CMSListView,), {
        "model": model, "title": title, "columns": columns,
        "permission_required": f"website.view_{perm_base}",
        "add_url_name": f"cms:{url_base}_add",
        "edit_url_name": f"cms:{url_base}_edit",
        "delete_url_name": f"cms:{url_base}_delete",
    })
    create_view = type(f"{model.__name__}CreateView", (CMSCreateView,), {
        "model": model, "form_class": form_class, "title": f"Add {title[:-1].lower()}" if title.endswith("s") else f"Add {title.lower()}",
        "permission_required": f"website.add_{perm_base}",
        "success_url": reverse_lazy(f"cms:{url_base}_list"),
    })
    update_view = type(f"{model.__name__}UpdateView", (CMSUpdateView,), {
        "model": model, "form_class": form_class, "title": f"Edit {title.lower()}",
        "permission_required": f"website.change_{perm_base}",
        "success_url": reverse_lazy(f"cms:{url_base}_list"),
    })
    delete_view = type(f"{model.__name__}DeleteView", (CMSDeleteView,), {
        "model": model, "title": title.lower(),
        "permission_required": f"website.delete_{perm_base}",
        "success_url": reverse_lazy(f"cms:{url_base}_list"),
    })
    return list_view, create_view, update_view, delete_view


StatisticListView, StatisticCreateView, StatisticUpdateView, StatisticDeleteView = _simple_crud(
    m.Statistic, f.StatisticForm, "Statistics", [("Label", "label"), ("Value", "value"), ("Order", "order")],
    "statistic", "statistic")

HeroSlideListView, HeroSlideCreateView, HeroSlideUpdateView, HeroSlideDeleteView = _simple_crud(
    m.HeroSlide, f.HeroSlideForm, "Banner slides",
    [("Description", "alt_text"), ("Position", "order"), ("Shown", "is_active")],
    "heroslide", "heroslide")

LeaderListView, LeaderCreateView, LeaderUpdateView, LeaderDeleteView = _simple_crud(
    m.Leader, f.LeaderForm, "Leaders", [("Name", "name"), ("Role", "role"), ("Active", "is_active")],
    "leader", "leader")

BeliefListView, BeliefCreateView, BeliefUpdateView, BeliefDeleteView = _simple_crud(
    m.BeliefStatement, f.BeliefStatementForm, "Beliefs", [("Title", "title"), ("Order", "order")],
    "belief", "beliefstatement")

TimelineListView, TimelineCreateView, TimelineUpdateView, TimelineDeleteView = _simple_crud(
    m.TimelineEvent, f.TimelineEventForm, "Timeline", [("Year", "year"), ("Title", "title")],
    "timeline", "timelineevent")

CourseListView, CourseCreateView, CourseUpdateView, CourseDeleteView = _simple_crud(
    m.BibleSchoolCourse, f.BibleSchoolCourseForm, "Bible School Courses",
    [("Title", "title"), ("Duration", "duration")], "course", "bibleschoolcourse")

FacultyListView, FacultyCreateView, FacultyUpdateView, FacultyDeleteView = _simple_crud(
    m.Faculty, f.FacultyForm, "Faculty", [("Name", "name"), ("Role", "role")], "faculty", "faculty")

MenuItemListView, MenuItemCreateView, MenuItemUpdateView, MenuItemDeleteView = _simple_crud(
    m.MenuItem, f.MenuItemForm, "Menu Items", [("Label", "label"), ("URL", "url"), ("Order", "order"), ("Active", "is_active")],
    "menuitem", "menuitem")


GalleryVideoListView, GalleryVideoCreateView, GalleryVideoUpdateView, GalleryVideoDeleteView = _simple_crud(
    m.GalleryVideo, f.GalleryVideoForm, "Videos",
    [("Title", "title"), ("Type", "source_label"), ("Album", "album"), ("Position", "order"), ("Shown", "is_active")],
    "video", "galleryvideo")


# ---------------------------------------------------------------------------
# Page SEO (meta + social sharing details for each main page)
# ---------------------------------------------------------------------------

class PageSEOListView(CMSListView):
    model = m.PageSEO
    title = "Page SEO & sharing"
    permission_required = "website.view_pageseo"
    paginate_by = 50
    columns = [("Page", "get_page_display"), ("Web address", "path"), ("Meta title", "meta_title"),
               ("Meta description", "meta_description"), ("Hidden from Google", "noindex")]
    edit_url_name = "cms:pageseo_edit"

    def get_queryset(self):
        # Make sure every page has a row, even if new pages were added later.
        for key, _ in m.PageSEO.PAGE_CHOICES:
            m.PageSEO.objects.get_or_create(page=key)
        return m.PageSEO.objects.all()


class PageSEOUpdateView(CMSUpdateView):
    model = m.PageSEO
    form_class = f.PageSEOForm
    permission_required = "website.change_pageseo"
    success_url = reverse_lazy("cms:pageseo_list")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = f"SEO & sharing — {self.object.get_page_display()} page"
        ctx["page_link"] = self.object.path
        return ctx


# ---------------------------------------------------------------------------
# Website sign-ups: prayer list and newsletter
# ---------------------------------------------------------------------------

class SignupListView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Read-only list of people who signed up through the website, with search,
    CSV download (for Excel / Gmail) and delete."""
    template_name = "cms/signups_list.html"
    model = None
    title = ""
    intro = ""
    columns = []          # (label, attribute)
    search_fields = []
    export_fields = []    # (header, attribute)
    url_name = ""

    def get_permission_required(self):
        return [f"website.view_{self.model._meta.model_name}"]

    def get_queryset(self):
        qs = self.model.objects.order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        if q:
            cond = Q()
            for field in self.search_fields:
                cond |= Q(**{f"{field}__icontains": q})
            qs = qs.filter(cond)
        return qs, q

    def get(self, request):
        qs, q = self.get_queryset()
        if request.GET.get("export") == "csv":
            return self.export_csv(qs)
        page_obj = Paginator(qs, 50).get_page(request.GET.get("page"))
        rows = [(obj, [getattr(obj, attr) for _, attr in self.columns]) for obj in page_obj]
        can_delete = request.user.has_perm(f"website.delete_{self.model._meta.model_name}")
        return render(request, self.template_name, {
            "title": self.title, "intro": self.intro, "columns": self.columns, "rows": rows,
            "page_obj": page_obj, "query": q, "total": self.model.objects.count(),
            "can_delete": can_delete, "url_name": self.url_name,
        })

    def post(self, request):
        if not request.user.has_perm(f"website.delete_{self.model._meta.model_name}"):
            raise PermissionDenied
        ids = request.POST.getlist("ids")
        if ids:
            deleted, _ = self.model.objects.filter(pk__in=ids).delete()
            messages.success(request, f"Removed {deleted} entr{'y' if deleted == 1 else 'ies'}.")
        return redirect(self.url_name)

    def export_csv(self, qs):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        stamp = timezone.localdate().isoformat()
        response["Content-Disposition"] = f'attachment; filename="{self.model._meta.model_name}-{stamp}.csv"'
        response.write("\ufeff")  # so Excel opens names with Indian-language characters correctly
        writer = csv.writer(response)
        writer.writerow([h for h, _ in self.export_fields])
        for obj in qs:
            row = []
            for _, attr in self.export_fields:
                val = getattr(obj, attr)
                if hasattr(val, "strftime"):
                    val = timezone.localtime(val).strftime("%d-%m-%Y %H:%M")
                elif isinstance(val, bool):
                    val = "Yes" if val else "No"
                row.append(val)
            writer.writerow(row)
        return response


class PrayerListView(SignupListView):
    model = m.PrayerListSignup
    title = "Prayer list sign-ups"
    intro = "People who filled in “Join the Prayer List” on the Contact page."
    columns = [("Name", "name"), ("Email", "email"), ("Signed up", "created_at")]
    search_fields = ["name", "email"]
    export_fields = [("Name", "name"), ("Email", "email"), ("Signed up", "created_at")]
    url_name = "cms:prayer_list"


class NewsletterListView(SignupListView):
    model = m.NewsletterSubscriber
    title = "Newsletter subscribers"
    intro = "Email addresses entered in the “Stay in touch” box in the footer of every page."
    columns = [("Email", "email"), ("Subscribed", "is_active"), ("Signed up", "created_at")]
    search_fields = ["email"]
    export_fields = [("Email", "email"), ("Subscribed", "is_active"), ("Signed up", "created_at")]
    url_name = "cms:newsletter_list"


# ---------------------------------------------------------------------------
# Contact messages
# ---------------------------------------------------------------------------

class ContactMessageListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = m.ContactMessage
    template_name = "cms/messages_list.html"
    permission_required = "website.view_contactmessage"
    paginate_by = 20


class ContactMessageDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "website.view_contactmessage"

    def get(self, request, pk):
        obj = get_object_or_404(m.ContactMessage, pk=pk)
        if obj.status == "unread":
            obj.status = "read"
            obj.save(update_fields=["status"])
        return render(request, "cms/message_detail.html", {"object": obj})

    def post(self, request, pk):
        obj = get_object_or_404(m.ContactMessage, pk=pk)
        action = request.POST.get("action")
        if action == "archive":
            obj.status = "archived"
        elif action == "unread":
            obj.status = "unread"
        elif action == "delete":
            obj.delete()
            messages.success(request, "Message deleted.")
            return redirect("cms:message_list")
        obj.save()
        messages.success(request, "Updated.")
        return redirect("cms:message_detail", pk=pk)


# ---------------------------------------------------------------------------
# Singleton settings pages
# ---------------------------------------------------------------------------

class SingletonUpdateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    template_name = "cms/generic_form.html"
    model = None
    form_class = None
    title = "Settings"
    success_url_name = "cms:dashboard"

    def get_object(self):
        return self.model.load()

    def get(self, request):
        form = self.form_class(instance=self.get_object())
        return render(request, self.template_name, {"form": form, "title": self.title})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=self.get_object())
        if form.is_valid():
            form.save()
            messages.success(request, "Saved.")
            return redirect(self.success_url_name)
        return render(request, self.template_name, {"form": form, "title": self.title})


class SiteSettingsUpdateView(SingletonUpdateView):
    model = m.SiteSettings
    form_class = f.SiteSettingsForm
    title = "Website Settings"
    permission_required = "website.change_sitesettings"
    success_url_name = "cms:settings"


class HeroSectionUpdateView(SingletonUpdateView):
    model = m.HeroSection
    form_class = f.HeroSectionForm
    title = "Home Page — Hero Section"
    permission_required = "website.change_herosection"
    success_url_name = "cms:hero"


class HomeAboutUpdateView(SingletonUpdateView):
    model = m.HomeAboutSection
    form_class = f.HomeAboutSectionForm
    title = "Home Page — Welcome Section"
    permission_required = "website.change_homeaboutsection"
    success_url_name = "cms:home_about"


class CallToActionUpdateView(SingletonUpdateView):
    model = m.CallToAction

    def get_object(self):
        obj, _ = m.CallToAction.objects.get_or_create(key="home")
        return obj

    form_class = f.CallToActionForm
    title = "Home Page — Call To Action"
    permission_required = "website.change_calltoaction"
    success_url_name = "cms:cta"


class AboutPageUpdateView(SingletonUpdateView):
    model = m.AboutPage
    form_class = f.AboutPageForm
    title = "About Page"
    permission_required = "website.change_aboutpage"
    success_url_name = "cms:about_page"


class BibleSchoolUpdateView(SingletonUpdateView):
    model = m.BibleSchool
    form_class = f.BibleSchoolForm
    title = "Bible School"
    permission_required = "website.change_bibleschool"
    success_url_name = "cms:bible_school"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "cms/users_list.html"
    permission_required = "auth.view_user"
    raise_exception = False

    def has_permission(self):
        return self.request.user.is_superuser

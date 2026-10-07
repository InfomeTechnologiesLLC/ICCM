from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .forms import ContactForm, NewsletterForm, PrayerListForm
from .models import (
    AboutPage, BeliefStatement, BibleSchool, BibleSchoolCourse, BlogCategory, BlogPost,
    CallToAction, Church, Event, Faculty, FlatPage, GalleryAlbum, GalleryImage, GalleryVideo, HeroSection,
    HeroSlide, HomeAboutSection, Leader, Ministry, Statistic, TimelineEvent,
)


def home(request):
    hero = HeroSection.load()
    hero_slides = HeroSlide.objects.filter(is_active=True)
    welcome = HomeAboutSection.load()
    stats = Statistic.objects.all()
    cta = CallToAction.objects.filter(key="home").first()

    ministries = Ministry.objects.filter(status="published", is_featured=True)[:5]
    if not ministries:
        ministries = Ministry.objects.filter(status="published")[:5]

    kerala_church = Church.objects.filter(status="published", region="kerala").first()
    punjab_church = Church.objects.filter(status="published", region="punjab").first()

    bible_school = BibleSchool.load()

    upcoming_events = Event.objects.filter(
        status="published", is_completed=False, start_date__gte=timezone.localdate()
    )[:3]

    latest_posts = BlogPost.objects.filter(status="published").select_related("author", "category")[:3]

    gallery_images = GalleryImage.objects.select_related("album")[:6]

    context = {
        "hero": hero,
        "hero_slides": hero_slides,
        "welcome": welcome,
        "stats": stats,
        "cta": cta,
        "ministries": ministries,
        "kerala_church": kerala_church,
        "punjab_church": punjab_church,
        "bible_school": bible_school,
        "upcoming_events": upcoming_events,
        "latest_posts": latest_posts,
        "gallery_images": gallery_images,
    }
    return render(request, "website/home.html", context)


def about(request):
    page = AboutPage.load()
    beliefs = BeliefStatement.objects.all()
    timeline = TimelineEvent.objects.all()
    leaders = Leader.objects.filter(is_active=True)
    return render(request, "website/about.html", {
        "page": page, "beliefs": beliefs, "timeline": timeline, "leaders": leaders,
    })


def church_list(request):
    kerala = Church.objects.filter(status="published", region="kerala")
    punjab = Church.objects.filter(status="published", region="punjab")
    return render(request, "website/churches.html", {"kerala_churches": kerala, "punjab_churches": punjab})


def church_detail(request, slug):
    church = get_object_or_404(Church, slug=slug, status="published")
    return render(request, "website/church_detail.html", {"church": church})


def ministry_list(request):
    ministries = Ministry.objects.filter(status="published")
    return render(request, "website/ministries.html", {"ministries": ministries})


def ministry_detail(request, slug):
    ministry = get_object_or_404(Ministry, slug=slug, status="published")
    return render(request, "website/ministry_detail.html", {"ministry": ministry})


def bible_school(request):
    school = BibleSchool.load()
    courses = BibleSchoolCourse.objects.all()
    faculty = Faculty.objects.all()
    return render(request, "website/bible_school.html", {
        "school": school, "courses": courses, "faculty": faculty,
    })


def event_list(request):
    today = timezone.localdate()
    qs = Event.objects.filter(status="published")
    tag = request.GET.get("filter")
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(venue__icontains=q) | Q(city__icontains=q))
    if tag == "past":
        qs = qs.filter(Q(is_completed=True) | Q(start_date__lt=today))
    elif tag == "upcoming" or not tag:
        qs = qs.filter(is_completed=False, start_date__gte=today)

    featured = Event.objects.filter(status="published", is_featured=True).first()
    return render(request, "website/events.html", {
        "events": qs, "featured_event": featured, "active_filter": tag or "upcoming", "query": q,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status="published")
    return render(request, "website/event_detail.html", {"event": event})


def gallery(request):
    albums = GalleryAlbum.objects.filter(status="published")
    images = GalleryImage.objects.select_related("album")
    tag = request.GET.get("filter")
    if tag:
        images = images.filter(tag=tag)
    videos = GalleryVideo.objects.filter(is_active=True).select_related("album")
    return render(request, "website/gallery.html", {
        "albums": albums, "images": images, "videos": videos, "active_filter": tag or "all",
    })


def gallery_album(request, slug):
    album = get_object_or_404(GalleryAlbum, slug=slug, status="published")
    return render(request, "website/gallery_album.html", {
        "album": album, "images": album.images.all(), "videos": album.videos.filter(is_active=True),
    })


def blog_list(request):
    qs = BlogPost.objects.filter(status="published").select_related("author", "category")
    category_slug = request.GET.get("category")
    q = request.GET.get("q", "").strip()
    if category_slug:
        qs = qs.filter(category__slug=category_slug)
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(content__icontains=q))

    featured = qs.filter(is_featured=True).first()
    paginator = Paginator(qs, 6)
    page_obj = paginator.get_page(request.GET.get("page"))
    categories = BlogCategory.objects.all()
    return render(request, "website/blog.html", {
        "page_obj": page_obj, "featured_post": featured, "categories": categories,
        "active_category": category_slug or "", "query": q,
    })


def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status="published")
    related = BlogPost.objects.filter(status="published", category=post.category).exclude(pk=post.pk)[:3]
    return render(request, "website/blog_post.html", {"post": post, "related_posts": related})


@require_http_methods(["GET", "POST"])
def contact(request):
    form = ContactForm()
    newsletter_form = NewsletterForm()
    prayer_form = PrayerListForm()
    sent = False

    if request.method == "POST":
        form_type = request.POST.get("form_type", "contact")
        if form_type == "newsletter":
            newsletter_form = NewsletterForm(request.POST)
            if newsletter_form.is_valid():
                newsletter_form.save()
                return redirect("/contact/?subscribed=1#newsletter")
        elif form_type == "prayer":
            prayer_form = PrayerListForm(request.POST)
            if prayer_form.is_valid():
                prayer_form.save()
                return redirect("/contact/?prayed=1#pray")
        else:
            form = ContactForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("/contact/?sent=1#top")

    return render(request, "website/contact.html", {
        "form": form, "newsletter_form": newsletter_form, "prayer_form": prayer_form,
        "sent": request.GET.get("sent") == "1",
        "subscribed": request.GET.get("subscribed") == "1",
        "prayed": request.GET.get("prayed") == "1",
    })


def flatpage(request, slug):
    page = get_object_or_404(FlatPage, slug=slug, status="published")
    return render(request, "website/flatpage.html", {"page": page})

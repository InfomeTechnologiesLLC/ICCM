from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from ckeditor.fields import RichTextField


# ============================================================================
# Mixins
# ============================================================================

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditedModel(TimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name="%(class)s_created", on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name="%(class)s_updated", on_delete=models.SET_NULL,
    )

    class Meta:
        abstract = True


class SEOFieldsMixin(models.Model):
    seo_title = models.CharField(max_length=70, blank=True)
    seo_description = models.CharField(max_length=160, blank=True)
    seo_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True


STATUS_CHOICES = [
    ("draft", "Draft"),
    ("published", "Published"),
    ("archived", "Archived"),
]


def unique_slugify(instance, base_text, slug_field="slug"):
    """Generate a unique slug for `instance` based on `base_text`."""
    base_slug = slugify(base_text)[:220] or "item"
    slug = base_slug
    ModelClass = instance.__class__
    counter = 2
    while ModelClass.objects.filter(**{slug_field: slug}).exclude(pk=instance.pk).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


# ============================================================================
# Site-wide settings, navigation, footer
# ============================================================================

class SiteSettings(models.Model):
    """Singleton — administrators edit the one row from the CMS."""
    site_name = models.CharField(max_length=150, default="India Church of Christ Mission")
    tagline = models.CharField(max_length=200, blank=True, default="Mission · Kerala & Punjab")
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    favicon = models.ImageField(upload_to="site/", blank=True, null=True)
    description = models.TextField(blank=True)

    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    whatsapp_number = models.CharField(max_length=40, blank=True)
    address = models.CharField(max_length=255, blank=True)
    google_maps_url = models.URLField(blank=True)

    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    utility_bar_text = models.CharField(max_length=255, blank=True,
        default="Serving Kerala & Punjab · 7 Churches · 1 Bible School")

    footer_about = models.TextField(blank=True,
        default="Preaching Christ, planting churches, and training preachers across Kerala and Punjab.")
    footer_hours = models.TextField(blank=True,
        default="Kerala churches: 9:00 AM\nPunjab Bible classes: Wednesdays, 6:30 PM")
    footer_text = models.CharField(max_length=255, blank=True, default="India Church of Christ Mission")
    copyright_text = models.CharField(max_length=255, blank=True,
        default="All rights reserved.")

    default_seo_title = models.CharField(max_length=70, blank=True)
    default_seo_description = models.CharField(max_length=160, blank=True)
    default_seo_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class MenuItem(models.Model):
    label = models.CharField(max_length=60)
    url = models.CharField(max_length=255,
        help_text="Internal path (e.g. /churches/) or a full https:// URL for external links.")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    open_in_new_tab = models.BooleanField(default=False)
    parent = models.ForeignKey("self", null=True, blank=True, related_name="children",
                                on_delete=models.CASCADE)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.label


# ============================================================================
# Home page (all sections database-driven)
# ============================================================================

class HeroSection(models.Model):
    heading = models.CharField(max_length=255, default="Seven churches. One Bible school. One gospel.")
    subheading = models.CharField(max_length=255, blank=True,
        default="India Church of Christ Mission · Kerala & Punjab")
    description = models.TextField(blank=True,
        default="Preaching Christ, planting churches, and training preachers across South and North India.")
    background_image = models.ImageField(upload_to="home/", blank=True, null=True)
    button_text = models.CharField(max_length=60, blank=True, default="See Our Churches")
    button_url = models.CharField(max_length=255, blank=True, default="/churches/")
    button2_text = models.CharField(max_length=60, blank=True, default="Support the Mission")
    button2_url = models.CharField(max_length=255, blank=True, default="/contact/#support")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Section"

    def __str__(self):
        return self.heading

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HomeAboutSection(models.Model):
    title = models.CharField(max_length=200, default="Welcome to the Mission")
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to="home/", blank=True, null=True)
    button_text = models.CharField(max_length=60, blank=True, default="Learn More")
    button_url = models.CharField(max_length=255, blank=True, default="/about/")

    class Meta:
        verbose_name = "Home — Welcome Section"
        verbose_name_plural = "Home — Welcome Section"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Statistic(models.Model):
    label = models.CharField(max_length=80)
    value = models.CharField(max_length=20, help_text="e.g. 7, 150, 1996")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.value} — {self.label}"


class CallToAction(models.Model):
    KEY_CHOICES = [("home", "Homepage CTA")]
    key = models.CharField(max_length=20, choices=KEY_CHOICES, default="home", unique=True)
    eyebrow = models.CharField(max_length=100, blank=True, default="Partner With Us")
    heading = models.CharField(max_length=200, default="Stand With the Work in India")
    description = models.TextField(blank=True)
    background_image = models.ImageField(upload_to="home/", blank=True, null=True)
    button_text = models.CharField(max_length=60, blank=True, default="Support the Mission")
    button_url = models.CharField(max_length=255, blank=True, default="/contact/#support")

    class Meta:
        verbose_name = "Call To Action"
        verbose_name_plural = "Calls To Action"

    def __str__(self):
        return self.heading


# ============================================================================
# About page
# ============================================================================

class AboutPage(models.Model):
    title = models.CharField(max_length=200, default="About the Mission")
    hero_image = models.ImageField(upload_to="about/", blank=True, null=True)
    introduction = RichTextField(blank=True)
    mission_statement = RichTextField(blank=True)
    vision_statement = RichTextField(blank=True)
    history = RichTextField(blank=True)
    founding_image = models.ImageField(upload_to="about/", blank=True, null=True)
    today_image = models.ImageField(upload_to="about/", blank=True, null=True)

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BeliefStatement(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class TimelineEvent(models.Model):
    year = models.CharField(max_length=20)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.year} — {self.title}"


class Leader(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to="leaders/", blank=True, null=True)
    email = models.EmailField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.name


# ============================================================================
# Churches
# ============================================================================

class Church(AuditedModel, SEOFieldsMixin):
    REGION_CHOICES = [("kerala", "Kerala"), ("punjab", "Punjab"), ("other", "Other")]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default="kerala")
    short_description = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True)
    pastor = models.CharField(max_length=150, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="India")
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    google_maps_url = models.URLField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    main_image = models.ImageField(upload_to="churches/", blank=True, null=True)
    service_times = models.CharField(max_length=255, blank=True, default="Sunday 9:00 AM")
    established_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Churches"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:church_detail", kwargs={"slug": self.slug})


class ChurchImage(models.Model):
    church = models.ForeignKey(Church, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="churches/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


# ============================================================================
# Ministries
# ============================================================================

class Ministry(AuditedModel, SEOFieldsMixin):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    icon = models.CharField(max_length=60, blank=True, default="church",
        help_text="Material Symbols icon name, e.g. 'church', 'diversity_3'")
    short_description = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True)
    image = models.ImageField(upload_to="ministries/", blank=True, null=True)
    leader = models.CharField(max_length=150, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    meeting_info = models.CharField(max_length=255, blank=True)
    location = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]
        verbose_name_plural = "Ministries"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:ministry_detail", kwargs={"slug": self.slug})


class MinistryImage(models.Model):
    ministry = models.ForeignKey(Ministry, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="ministries/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


# ============================================================================
# Bible School
# ============================================================================

class BibleSchool(models.Model):
    name = models.CharField(max_length=200, default="ICCM Bible School")
    description = RichTextField(blank=True)
    campus_image = models.ImageField(upload_to="bible-school/", blank=True, null=True)
    classroom_image = models.ImageField(upload_to="bible-school/", blank=True, null=True)
    students_image = models.ImageField(upload_to="bible-school/", blank=True, null=True)
    hostel_image = models.ImageField(upload_to="bible-school/", blank=True, null=True)
    graduation_image = models.ImageField(upload_to="bible-school/", blank=True, null=True)
    admission_info = RichTextField(blank=True)
    requirements = RichTextField(blank=True)
    fees = models.CharField(max_length=100, blank=True)
    application_info = RichTextField(blank=True)
    registration_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)

    class Meta:
        verbose_name = "Bible School"
        verbose_name_plural = "Bible School"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class BibleSchoolCourse(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=100, blank=True, help_text="e.g. '2 years'")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title


class Faculty(models.Model):
    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150, blank=True)
    photo = models.ImageField(upload_to="bible-school/faculty/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name_plural = "Faculty"

    def __str__(self):
        return self.name


# ============================================================================
# Events
# ============================================================================

class Event(AuditedModel, SEOFieldsMixin):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_description = models.CharField(max_length=255, blank=True)
    description = RichTextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="India")
    organizer = models.CharField(max_length=150, blank=True)
    contact_name = models.CharField(max_length=150, blank=True)
    contact_phone = models.CharField(max_length=40, blank=True)
    contact_email = models.EmailField(blank=True)
    registration_url = models.URLField(blank=True)
    featured_image = models.ImageField(upload_to="events/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:event_detail", kwargs={"slug": self.slug})

    @property
    def is_upcoming(self):
        return not self.is_completed and self.start_date >= timezone.localdate()

    @property
    def is_past(self):
        return self.is_completed or self.start_date < timezone.localdate()


class EventImage(models.Model):
    event = models.ForeignKey(Event, related_name="gallery", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="events/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


# ============================================================================
# Gallery
# ============================================================================

class GalleryAlbum(AuditedModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="gallery/covers/", blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:gallery_album", kwargs={"slug": self.slug})


class GalleryImage(models.Model):
    TAG_CHOICES = [
        ("worship", "Worship"), ("outreach", "Outreach"), ("youth", "Youth"),
        ("school", "School"), ("kids", "Kids"), ("punjab", "Punjab"),
    ]
    album = models.ForeignKey(GalleryAlbum, related_name="images", on_delete=models.CASCADE,
                               null=True, blank=True)
    image = models.ImageField(upload_to="gallery/")
    title = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=255, blank=True)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Image #{self.pk}"


# ============================================================================
# Blog
# ============================================================================

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Blog categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class BlogTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name)
        super().save(*args, **kwargs)


class BlogPost(AuditedModel, SEOFieldsMixin):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    content = RichTextField()
    featured_image = models.ImageField(upload_to="blog/", blank=True, null=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="blog_posts",
                                null=True, blank=True, on_delete=models.SET_NULL)
    author_name = models.CharField(max_length=150, blank=True,
        help_text="Shown instead of the account name, if set.")
    author_photo = models.ImageField(upload_to="blog/authors/", blank=True, null=True)
    category = models.ForeignKey(BlogCategory, related_name="posts", null=True, blank=True,
                                  on_delete=models.SET_NULL)
    tags = models.ManyToManyField(BlogTag, related_name="posts", blank=True)
    published_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:blog_detail", kwargs={"slug": self.slug})

    @property
    def display_author(self):
        return self.author_name or (self.author.get_full_name() if self.author else "") or (
            self.author.username if self.author else "ICCM Mission")


# ============================================================================
# Contact
# ============================================================================

class ContactMessage(TimeStampedModel):
    STATUS_CHOICES = [("unread", "Unread"), ("read", "Read"), ("archived", "Archived")]
    REASON_CHOICES = [
        ("general", "General enquiry"), ("give", "Giving / Support"),
        ("pray", "Prayer request"), ("visit", "Planning a visit"),
        ("bible_school", "Bible School"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default="general")
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="unread")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.subject or self.get_reason_display()}"


class NewsletterSubscriber(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class PrayerListSignup(TimeStampedModel):
    name = models.CharField(max_length=150)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} <{self.email}>"


# ============================================================================
# Generic flat pages & media library
# ============================================================================

class FlatPage(AuditedModel, SEOFieldsMixin):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = RichTextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("website:flatpage", kwargs={"slug": self.slug})


class MediaAsset(TimeStampedModel):
    file = models.FileField(upload_to="library/%Y/%m/")
    title = models.CharField(max_length=200, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                     on_delete=models.SET_NULL)

    def __str__(self):
        return self.title or self.file.name

    @property
    def file_type(self):
        return self.file.name.rsplit(".", 1)[-1].upper() if "." in self.file.name else ""

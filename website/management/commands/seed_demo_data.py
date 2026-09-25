import datetime
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from website import models as m

IMG_DIR = Path(settings.BASE_DIR) / "static" / "img"


def img(name):
    """Returns a File wrapper for a placeholder image, or None if missing."""
    path = IMG_DIR / name
    if not path.exists():
        return None
    return File(open(path, "rb"), name=name)


def set_image(instance, field_name, filename):
    f = img(filename)
    if f:
        getattr(instance, field_name).save(filename, f, save=False)


class Command(BaseCommand):
    help = ("Populate the database with realistic DEMO / SAMPLE content so the site can be "
            "reviewed immediately after installation. Safe to re-run (uses get_or_create).")

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data (clearly marked as sample content)...")

        self.seed_settings()
        self.seed_menu()
        self.seed_home()
        self.seed_about()
        self.seed_churches()
        self.seed_ministries()
        self.seed_bible_school()
        self.seed_events()
        self.seed_gallery()
        self.seed_blog()

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    # ------------------------------------------------------------------
    def seed_settings(self):
        s = m.SiteSettings.load()
        s.site_name = "India Church of Christ Mission"
        s.tagline = "Mission · Kerala & Punjab"
        s.description = "DEMO CONTENT — Preaching Christ, planting churches, and training preachers across Kerala and Punjab."
        s.email = "office@example.org"
        s.phone = "+91 98765 43210"
        s.whatsapp_number = "919876543210"
        s.address = "Mission Compound, MC Road, Kottayam, Kerala 686001 (sample address)"
        s.utility_bar_text = "Serving Kerala & Punjab · 7 Churches · 1 Bible School"
        s.footer_hours = "Kerala churches: Sunday 9:00 AM\nPunjab Bible classes: Wednesdays, 6:30 PM"
        s.copyright_text = "All rights reserved. Demo content — replace before going live."
        if not s.logo:
            set_image(s, "logo", "logo-mark.svg")
        s.save()

    def seed_menu(self):
        items = [
            ("Home", "/", 0), ("About", "/about/", 1), ("Churches", "/churches/", 2),
            ("Ministries", "/ministries/", 3), ("Bible School", "/bible-school/", 4),
            ("Events", "/events/", 5), ("Gallery", "/gallery/", 6),
            ("Blog", "/blog/", 7), ("Contact", "/contact/", 8),
        ]
        for label, url, order in items:
            m.MenuItem.objects.get_or_create(label=label, defaults={"url": url, "order": order})

    def seed_home(self):
        hero = m.HeroSection.load()
        hero.heading = "Seven churches. One Bible school. One gospel."
        hero.subheading = "India Church of Christ Mission · Kerala & Punjab"
        hero.description = "Preaching Christ, planting churches, and training preachers across South and North India."
        set_image(hero, "background_image", "hero-worship.jpg")
        hero.save()

        welcome = m.HomeAboutSection.load()
        welcome.title = "Welcome to the Mission"
        welcome.description = ("<p>For over two decades, the India Church of Christ Mission has planted "
                                "congregations in Kerala and, more recently, in Punjab, while training a new "
                                "generation of preachers at our Bible school.</p>")
        set_image(welcome, "image", "home-welcome.jpg")
        welcome.save()

        for label, value, order in [("Churches", "7", 0), ("Bible School", "1", 1),
                                     ("Students Trained", "150+", 2), ("Years of Service", "28", 3)]:
            m.Statistic.objects.get_or_create(label=label, defaults={"value": value, "order": order})

        cta, _ = m.CallToAction.objects.get_or_create(key="home")
        cta.heading = "Stand With the Work in India"
        cta.description = "Every rupee given goes into preaching, church planting, and training preachers."
        cta.save()

    def seed_about(self):
        page = m.AboutPage.load()
        page.title = "About the Mission"
        page.introduction = "<p>The India Church of Christ Mission exists to preach the gospel, plant churches, and train preachers across South and North India.</p>"
        page.mission_statement = "<p>To make disciples of Jesus Christ by preaching the gospel, establishing New Testament churches, and training faithful preachers.</p>"
        page.vision_statement = "<p>A church of Christ within reach of every village in Kerala and Punjab.</p>"
        page.history = "<p>DEMO CONTENT — The mission began with a single congregation and has since grown to seven churches and a Bible training school.</p>"
        set_image(page, "founding_image", "about-founding.jpg")
        set_image(page, "today_image", "about-today.jpg")
        page.save()

        beliefs = [
            ("The Scriptures", "We believe the Bible is the inspired, inerrant word of God and our only rule of faith and practice."),
            ("The Church", "We believe in the New Testament church, governed locally by elders and deacons."),
            ("Salvation", "We believe salvation comes through faith, repentance, confession, and baptism into Christ."),
            ("The Lord's Supper", "We observe the Lord's Supper every first day of the week, as the early church did."),
        ]
        for i, (title, desc) in enumerate(beliefs):
            m.BeliefStatement.objects.get_or_create(title=title, defaults={"description": desc, "order": i})

        timeline = [
            ("1996", "Mission Founded", "The first congregation was established in Kottayam district."),
            ("2004", "Bible School Opened", "The mission opened its Bible training school."),
            ("2015", "Punjab Work Begins", "The mission's first congregation in Punjab was planted."),
            ("2026", "Seven Churches", "The mission now serves seven congregations across two states."),
        ]
        for i, (year, title, desc) in enumerate(timeline):
            m.TimelineEvent.objects.get_or_create(year=year, title=title, defaults={"description": desc, "order": i})

        leaders = [
            ("Thomas Varghese", "Mission Director", "leader-01.jpg"),
            ("Ranjith Kumar", "Bible School Principal", "leader-02.jpg"),
            ("Suresh Paul", "Punjab Field Coordinator", "leader-03.jpg"),
        ]
        for i, (name, role, photo) in enumerate(leaders):
            leader, _ = m.Leader.objects.get_or_create(name=name, defaults={
                "role": role, "bio": "DEMO CONTENT — replace with a real biography.", "order": i,
            })
            if not leader.photo:
                set_image(leader, "photo", photo)
                leader.save()

    def seed_churches(self):
        kerala = [
            ("Kottayam Church of Christ", "Kottayam", "church-01.jpg"),
            ("Kochi Church of Christ", "Kochi", "church-02.jpg"),
            ("Alappuzha Church of Christ", "Alappuzha", "church-03.jpg"),
            ("Thrissur Church of Christ", "Thrissur", "church-04.jpg"),
            ("Kollam Church of Christ", "Kollam", "church-05.jpg"),
        ]
        punjab = [
            ("Ludhiana Church of Christ", "Ludhiana", "church-punjab-01.jpg"),
            ("Amritsar Church of Christ", "Amritsar", "church-punjab-02.jpg"),
        ]
        order = 0
        for name, city, photo in kerala:
            self._make_church(name, city, "Kerala", "kerala", photo, order)
            order += 1
        for name, city, photo in punjab:
            self._make_church(name, city, "Punjab", "punjab", photo, order)
            order += 1

    def _make_church(self, name, city, state, region, photo, order):
        church, created = m.Church.objects.get_or_create(name=name, defaults={
            "region": region, "city": city, "state": state,
            "short_description": f"DEMO CONTENT — A congregation of the mission in {city}.",
            "description": f"<p>DEMO CONTENT — The {name} gathers every Sunday for worship and Bible study.</p>",
            "pastor": "Sample Pastor", "service_times": "Sunday 9:00 AM",
            "established_date": datetime.date(2005, 1, 1), "status": "published",
            "is_featured": order == 0, "order": order,
        })
        if created:
            set_image(church, "main_image", photo)
            church.save()

    def seed_ministries(self):
        ministries = [
            ("Youth Ministry", "diversity_3", "ministry-youth-camp.jpg"),
            ("Bible School Outreach", "campaign", "ministry-outreach.jpg"),
            ("Orphan & School Support", "backpack", "ministry-school-kits.jpg"),
            ("Church Planting", "church", "ministry-monthly-meeting.jpg"),
            ("Graduate Placement", "school", "ministry-graduation.jpg"),
        ]
        for i, (name, icon, photo) in enumerate(ministries):
            ministry, created = m.Ministry.objects.get_or_create(name=name, defaults={
                "icon": icon, "short_description": f"DEMO CONTENT — {name} description.",
                "description": f"<p>DEMO CONTENT — details about the {name} ministry.</p>",
                "leader": "Sample Leader", "status": "published", "is_featured": i < 3, "order": i,
            })
            if created:
                set_image(ministry, "image", photo)
                ministry.save()

    def seed_bible_school(self):
        school = m.BibleSchool.load()
        school.name = "ICCM Bible School"
        school.description = "<p>DEMO CONTENT — The ICCM Bible School trains men and women for gospel ministry across India.</p>"
        school.admission_info = "<p>Admissions open each January. Contact the school office for the application form.</p>"
        school.requirements = "<p>Applicants should be baptized believers with a recommendation from their home congregation.</p>"
        school.fees = "₹25,000 / year (sponsorship available)"
        school.application_info = "<p>Write to the mission office or use the contact form to request an application.</p>"
        for field, photo in [("campus_image", "school-campus.jpg"), ("classroom_image", "school-classroom.jpg"),
                              ("students_image", "school-students.jpg"), ("hostel_image", "school-hostel.jpg"),
                              ("graduation_image", "school-graduation-wide.jpg")]:
            if not getattr(school, field):
                set_image(school, field, photo)
        school.save()

        for i, (title, duration, desc) in enumerate([
            ("Certificate in Bible Studies", "1 year", "An introduction to Old and New Testament survey."),
            ("Diploma in Ministry", "2 years", "In-depth study preparing students for local church ministry."),
            ("Advanced Preaching Track", "3 years", "Advanced homiletics, languages, and church planting."),
        ]):
            m.BibleSchoolCourse.objects.get_or_create(title=title, defaults={"duration": duration, "description": desc, "order": i})

        for i, (name, role) in enumerate([("Ranjith Kumar", "Principal"), ("Anna Mathew", "New Testament")]):
            m.Faculty.objects.get_or_create(name=name, defaults={"role": role, "order": i})

    def seed_events(self):
        today = timezone.localdate()
        events = [
            ("Annual Conference 2026", today + datetime.timedelta(days=30), "event-featured.jpg", True),
            ("Youth Camp", today + datetime.timedelta(days=60), "event-01.jpg", False),
            ("Church Anniversary — Kottayam", today + datetime.timedelta(days=10), "event-02.jpg", False),
            ("Bible School Graduation", today - datetime.timedelta(days=40), "event-03.jpg", False),
        ]
        for name, date, photo, featured in events:
            event, created = m.Event.objects.get_or_create(name=name, defaults={
                "short_description": f"DEMO CONTENT — join us for the {name}.",
                "description": f"<p>DEMO CONTENT — full details about {name}.</p>",
                "start_date": date, "venue": "Mission Compound", "city": "Kottayam",
                "status": "published", "is_featured": featured, "is_completed": date < today,
            })
            if created:
                set_image(event, "featured_image", photo)
                event.save()

    def seed_gallery(self):
        album, _ = m.GalleryAlbum.objects.get_or_create(title="Annual Conference 2026", defaults={
            "description": "DEMO CONTENT — photos from the annual conference.", "status": "published", "is_featured": True,
        })
        if not album.cover_image:
            set_image(album, "cover_image", "gallery-01.jpg")
            album.save()

        tags = ["worship", "outreach", "youth", "school", "kids", "punjab"]
        for i in range(1, 19):
            filename = f"gallery-{i:02d}.jpg"
            if not (IMG_DIR / filename).exists():
                continue
            gi, created = m.GalleryImage.objects.get_or_create(title=f"Gallery photo {i}", defaults={
                "album": album if i <= 6 else None, "tag": tags[i % len(tags)], "order": i,
            })
            if created:
                set_image(gi, "image", filename)
                gi.save()

    def seed_blog(self):
        cat, _ = m.BlogCategory.objects.get_or_create(name="Field Reports")
        posts = [
            ("A New Congregation in Ludhiana", "post-01.jpg", True),
            ("Bible School Graduates Nine Students", "post-02.jpg", False),
            ("Youth Camp 2026 Recap", "post-03.jpg", False),
            ("Building Update: Kollam Church", "post-04.jpg", False),
        ]
        for i, (title, photo, featured) in enumerate(posts):
            post, created = m.BlogPost.objects.get_or_create(title=title, defaults={
                "excerpt": f"DEMO CONTENT — summary of {title}.",
                "content": f"<p>DEMO CONTENT — full article body for {title}.</p>",
                "category": cat, "status": "published", "is_featured": featured,
                "published_at": timezone.now() - datetime.timedelta(days=i * 7),
                "author_name": "Mission Office",
            })
            if created:
                set_image(post, "featured_image", photo)
                post.save()

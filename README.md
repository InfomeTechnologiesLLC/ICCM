# India Church Mission — Django CMS

A full Django + MySQL-ready rebuild of the original static site, with a custom CMS portal
so mission staff can manage the whole website without touching code. The original
Bootstrap frontend, CSS, JS, and visual identity are preserved; everything that was
static HTML is now database-driven.

## What's in here

```
config/         Django project settings, root urls
website/        Public site: models, views, templates, forms, seed data, tests
cms/            The custom CMS portal (dashboard + CRUD screens), tests
accounts/       Role setup (Content Manager / Editor groups + permissions)
templates/      base.html, partials/ (navbar, footer), website/*, cms/*
static/         Original css/js/img, copied in as-is
media/          User-uploaded files (created on first upload)
```

### Static page → template → model → CMS screen map

| Static page        | Django template                | Key model(s)                              | CMS screen                          |
|---------------------|--------------------------------|--------------------------------------------|--------------------------------------|
| index.html          | website/home.html              | HeroSection, HomeAboutSection, Statistic, CallToAction, Church, Ministry, Event, BlogPost, GalleryImage | Home Page section (sidebar) |
| about.html           | website/about.html             | AboutPage, BeliefStatement, TimelineEvent, Leader | About (sidebar)                |
| churches.html + detail| website/churches.html, church_detail.html | Church, ChurchImage                  | Churches                             |
| ministries.html + detail| website/ministries.html, ministry_detail.html | Ministry, MinistryImage         | Ministries                           |
| bible-school.html    | website/bible_school.html      | BibleSchool, BibleSchoolCourse, Faculty   | Bible School                         |
| events.html + detail | website/events.html, event_detail.html | Event, EventImage                | Events                               |
| gallery.html         | website/gallery.html, gallery_album.html | GalleryAlbum, GalleryImage       | Gallery Albums / Images              |
| blog.html + blog-post.html | website/blog.html, blog_post.html | BlogPost, BlogCategory, BlogTag     | Blog Posts / Categories              |
| contact.html         | website/contact.html           | ContactMessage, NewsletterSubscriber, PrayerListSignup | Contact Messages inbox |
| navbar/footer (every page) | partials/navbar.html, footer.html | SiteSettings, MenuItem              | Site Settings, Menu                  |

## Quick start (SQLite, zero extra services)

```bash
python -m venv venv
source venv/bin/activate            # venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.example .env                # defaults to DB_ENGINE=sqlite — no DB setup needed

python manage.py migrate
python manage.py createsuperuser
python manage.py setup_roles        # creates the Content Manager / Editor groups
python manage.py seed_demo_data     # optional: fills the site with sample content
python manage.py collectstatic --noinput   # only needed when DEBUG=False

python manage.py runserver
```

- Public site: http://127.0.0.1:8000/
- CMS portal: http://127.0.0.1:8000/cms/ (log in with the superuser you just created)
- Full Django admin (users, groups, media-library housekeeping): http://127.0.0.1:8000/django-admin/

## Switching to MySQL

1. Install a MySQL server and create a database and user for the project.
2. Install the MySQL client library: `pip install mysqlclient` (uncomment it in
   `requirements.txt`). On Linux you'll typically need the system package first,
   e.g. `apt install default-libmysqlclient-dev build-essential pkg-config`; on macOS,
   `brew install mysql-client pkg-config`.
3. In `.env`, set:
   ```
   DB_ENGINE=mysql
   DB_NAME=india_church_mission
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
4. Run `python manage.py migrate` again against the new database, then
   `createsuperuser` / `setup_roles` / `seed_demo_data` as above.

No application code changes are needed — `config/settings.py` reads `DB_ENGINE` and
builds the right `DATABASES` config automatically.

## Loading the real ICCM content

The text and photos from the "For web site" Word document are packaged with the project
(`website/management/commands/iccm_content/images/`). Load them into the CMS with:

```bash
python manage.py load_iccm_content --remove-demo
```

This fills every CMS screen: the document's text goes in word for word, and the remaining
sections that held demo text (beliefs, timeline, events, blog, Bible school admissions, footer,
call to action, SEO) are filled with content written from the document. `--remove-demo`
deletes the `seed_demo_data` samples and hides the Churches menu item, because the names and
addresses of the 10 local churches are not in the document yet. Safe to re-run.

| Section | Where it goes in the CMS |
|---|---|
| Tagline, logo, footer, SEO | Site Settings |
| Hero, welcome, statistics, call to action | Home Page |
| About us, beliefs, timeline, Thomas and Sali Thomas | About |
| ICTC text, courses, admissions | Bible School |
| 7 ministries, meeting times, photos | Ministries |
| Next 3 monthly fellowship meetings | Events |
| 3 articles (ICTC, Vacation Bible Schools, social work) | Blog |
| Baptisms, churches, ministries and ICTC photos | Gallery |
| Contact details | Not in the document: add them in Site Settings |

Page templates also had fixed demo text and stock photos (the "Preach. Plant. Train." band,
the verse band, region cards, contact and support cards). These were rewritten to match the
document and now use the document's photos from `static/img/iccm/`.

## Roles & permissions

- **Super Admin** — any Django superuser. Full access everywhere, including
  `/django-admin/` (users, groups, media library) and the `Users` screen in the CMS.
- **Content Manager** — full add/change/delete/publish rights on all content
  (churches, ministries, events, gallery, blog, Bible school, contact messages)
  and on the site-wide singletons (Site Settings, Home Page sections, About Page,
  Bible School page). Created by `python manage.py setup_roles`.
- **Editor** — can add and change content, but cannot delete it and cannot touch
  site-wide settings. Enforced with real Django permission checks on every CMS view
  (`PermissionRequiredMixin`), not just hidden buttons — try it: an Editor gets a
  clean 403 if they hit a delete URL directly.

To create a staff account: add the user in `/django-admin/auth/user/`, tick
"staff status", and put them in the **Content Manager** or **Editor** group.

## What's real vs. what's demo content

`python manage.py seed_demo_data` fills every module with sample data so the site is
immediately reviewable — churches, ministries, Bible school courses, events, a gallery
album, blog posts, menu items, and the homepage sections. **All of it is placeholder**
and is labeled "DEMO CONTENT" in descriptions so it's obvious what to replace. Delete
or edit it from the CMS before going live; the command is safe to skip entirely if you'd
rather start from an empty database (`migrate` + `createsuperuser` + `setup_roles` only).

## Design decisions worth knowing about

- **CMS portal vs. Django admin**: the CMS portal (`/cms/`) is a custom Bootstrap-styled
  dashboard + CRUD screens for everything a content editor touches day to day (Site
  Settings, Home Page sections, About, Churches, Ministries, Events, Gallery, Blog, Bible
  School, Contact inbox). User/group management and ad-hoc media-library housekeeping
  stay on the battle-tested Django admin (`/django-admin/`) rather than being
  reimplemented — both are wired to the same permission system, so what a role can do is
  identical either way.
- **Rich text**: `django-ckeditor` (CKEditor 4) powers the rich-text fields. It's stable
  and well-integrated with Django, but CKEditor 4 itself is past its community-support
  window — if that matters for your deployment, swapping in `django-ckeditor-5` is a
  contained change (it only touches `RichTextField` usages and `INSTALLED_APPS`).
- **Homepage decorative sections**: the "Preach / Plant / Train" triad, the verse band,
  and similar purely illustrative sections stayed as static template content rather than
  becoming their own CMS models — they're page furniture, not content anyone edits
  regularly. Every section an administrator would actually want to change (hero, welcome
  text, statistics, featured ministries/churches, upcoming events, latest posts, gallery
  preview, call-to-action) is fully database-driven.
- **Media library**: `MediaAsset` plus each model's own image/file fields cover uploads.
  A dedicated "used in" cross-reference (what content references a given upload) wasn't
  built — Django's media handling already prevents orphaned files from breaking pages,
  and each content type manages its own images directly (e.g. gallery images always
  belong to a `GalleryAlbum`).

## Running the tests

```bash
python manage.py test
```

37 tests cover model creation/slugs/relationships, singleton behavior, public views
(homepage with an empty database, listing pages, detail pages, draft-vs-published
visibility), the contact/newsletter forms, CMS authentication, and — importantly —
that Editor vs. Content Manager permissions are enforced on the server for every
CRUD action, not just hidden in the UI.

## Production checklist

- Set `DEBUG=False` and a real `SECRET_KEY` in `.env`.
- Set `ALLOWED_HOSTS` to your real domain(s).
- Switch to MySQL (see above) and run `collectstatic`.
- Put a real web server (gunicorn/uwsgi behind nginx, or similar) in front of
  `config.wsgi.application`; the `runserver` command is for local development only.
- Review `CSRF_COOKIE_SECURE` / `SESSION_COOKIE_SECURE` / `SECURE_SSL_REDIRECT` in
  `config/settings.py` once you're serving over HTTPS.
- Wire up a real email backend if you want contact-form/newsletter notifications sent
  anywhere (`CONTACT_NOTIFICATION_EMAIL` in `.env` is a placeholder hook for this).
#   I C C M  
 
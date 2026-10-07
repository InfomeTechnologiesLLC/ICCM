from django.urls import path

from . import views as v

app_name = "cms"

urlpatterns = [
    path("login/", v.CMSLoginView.as_view(), name="login"),
    path("logout/", v.CMSLogoutView.as_view(), name="logout"),
    path("", v.DashboardView.as_view(), name="dashboard"),

    # Settings / singletons
    path("settings/", v.SiteSettingsUpdateView.as_view(), name="settings"),
    path("home/hero/", v.HeroSectionUpdateView.as_view(), name="hero"),
    path("home/slides/", v.HeroSlideListView.as_view(), name="heroslide_list"),
    path("home/slides/add/", v.HeroSlideCreateView.as_view(), name="heroslide_add"),
    path("home/slides/<int:pk>/edit/", v.HeroSlideUpdateView.as_view(), name="heroslide_edit"),
    path("home/slides/<int:pk>/delete/", v.HeroSlideDeleteView.as_view(), name="heroslide_delete"),
    path("home/welcome/", v.HomeAboutUpdateView.as_view(), name="home_about"),
    path("home/cta/", v.CallToActionUpdateView.as_view(), name="cta"),
    path("about/", v.AboutPageUpdateView.as_view(), name="about_page"),
    path("bible-school/", v.BibleSchoolUpdateView.as_view(), name="bible_school"),

    # Churches
    path("churches/", v.ChurchListView.as_view(), name="church_list"),
    path("churches/add/", v.ChurchCreateView.as_view(), name="church_add"),
    path("churches/<int:pk>/edit/", v.ChurchUpdateView.as_view(), name="church_edit"),
    path("churches/<int:pk>/delete/", v.ChurchDeleteView.as_view(), name="church_delete"),

    # Ministries
    path("ministries/", v.MinistryListView.as_view(), name="ministry_list"),
    path("ministries/add/", v.MinistryCreateView.as_view(), name="ministry_add"),
    path("ministries/<int:pk>/edit/", v.MinistryUpdateView.as_view(), name="ministry_edit"),
    path("ministries/<int:pk>/delete/", v.MinistryDeleteView.as_view(), name="ministry_delete"),

    # Bible school courses / faculty
    path("bible-school/courses/", v.CourseListView.as_view(), name="course_list"),
    path("bible-school/courses/add/", v.CourseCreateView.as_view(), name="course_add"),
    path("bible-school/courses/<int:pk>/edit/", v.CourseUpdateView.as_view(), name="course_edit"),
    path("bible-school/courses/<int:pk>/delete/", v.CourseDeleteView.as_view(), name="course_delete"),
    path("bible-school/faculty/", v.FacultyListView.as_view(), name="faculty_list"),
    path("bible-school/faculty/add/", v.FacultyCreateView.as_view(), name="faculty_add"),
    path("bible-school/faculty/<int:pk>/edit/", v.FacultyUpdateView.as_view(), name="faculty_edit"),
    path("bible-school/faculty/<int:pk>/delete/", v.FacultyDeleteView.as_view(), name="faculty_delete"),

    # Events
    path("events/", v.EventListView.as_view(), name="event_list"),
    path("events/add/", v.EventCreateView.as_view(), name="event_add"),
    path("events/<int:pk>/edit/", v.EventUpdateView.as_view(), name="event_edit"),
    path("events/<int:pk>/delete/", v.EventDeleteView.as_view(), name="event_delete"),

    # Gallery
    path("gallery/albums/", v.GalleryAlbumListView.as_view(), name="album_list"),
    path("gallery/albums/add/", v.GalleryAlbumCreateView.as_view(), name="album_add"),
    path("gallery/albums/<int:pk>/edit/", v.GalleryAlbumUpdateView.as_view(), name="album_edit"),
    path("gallery/albums/<int:pk>/delete/", v.GalleryAlbumDeleteView.as_view(), name="album_delete"),
    path("gallery/images/", v.GalleryImageListView.as_view(), name="image_list"),
    path("gallery/images/add/", v.GalleryImageCreateView.as_view(), name="image_add"),
    path("gallery/images/<int:pk>/edit/", v.GalleryImageUpdateView.as_view(), name="image_edit"),
    path("gallery/images/<int:pk>/delete/", v.GalleryImageDeleteView.as_view(), name="image_delete"),

    path("gallery/videos/", v.GalleryVideoListView.as_view(), name="video_list"),
    path("gallery/videos/add/", v.GalleryVideoCreateView.as_view(), name="video_add"),
    path("gallery/videos/<int:pk>/edit/", v.GalleryVideoUpdateView.as_view(), name="video_edit"),
    path("gallery/videos/<int:pk>/delete/", v.GalleryVideoDeleteView.as_view(), name="video_delete"),

    # Page SEO / social sharing
    path("seo/", v.PageSEOListView.as_view(), name="pageseo_list"),
    path("seo/<int:pk>/edit/", v.PageSEOUpdateView.as_view(), name="pageseo_edit"),

    # Blog
    path("blog/posts/", v.BlogPostListView.as_view(), name="post_list"),
    path("blog/posts/add/", v.BlogPostCreateView.as_view(), name="post_add"),
    path("blog/posts/<int:pk>/edit/", v.BlogPostUpdateView.as_view(), name="post_edit"),
    path("blog/posts/<int:pk>/delete/", v.BlogPostDeleteView.as_view(), name="post_delete"),
    path("blog/categories/", v.BlogCategoryListView.as_view(), name="category_list"),
    path("blog/categories/add/", v.BlogCategoryCreateView.as_view(), name="category_add"),
    path("blog/categories/<int:pk>/edit/", v.BlogCategoryUpdateView.as_view(), name="category_edit"),
    path("blog/categories/<int:pk>/delete/", v.BlogCategoryDeleteView.as_view(), name="category_delete"),

    # Small supporting content
    path("statistics/", v.StatisticListView.as_view(), name="statistic_list"),
    path("statistics/add/", v.StatisticCreateView.as_view(), name="statistic_add"),
    path("statistics/<int:pk>/edit/", v.StatisticUpdateView.as_view(), name="statistic_edit"),
    path("statistics/<int:pk>/delete/", v.StatisticDeleteView.as_view(), name="statistic_delete"),

    path("leaders/", v.LeaderListView.as_view(), name="leader_list"),
    path("leaders/add/", v.LeaderCreateView.as_view(), name="leader_add"),
    path("leaders/<int:pk>/edit/", v.LeaderUpdateView.as_view(), name="leader_edit"),
    path("leaders/<int:pk>/delete/", v.LeaderDeleteView.as_view(), name="leader_delete"),

    path("beliefs/", v.BeliefListView.as_view(), name="belief_list"),
    path("beliefs/add/", v.BeliefCreateView.as_view(), name="belief_add"),
    path("beliefs/<int:pk>/edit/", v.BeliefUpdateView.as_view(), name="belief_edit"),
    path("beliefs/<int:pk>/delete/", v.BeliefDeleteView.as_view(), name="belief_delete"),

    path("timeline/", v.TimelineListView.as_view(), name="timeline_list"),
    path("timeline/add/", v.TimelineCreateView.as_view(), name="timeline_add"),
    path("timeline/<int:pk>/edit/", v.TimelineUpdateView.as_view(), name="timeline_edit"),
    path("timeline/<int:pk>/delete/", v.TimelineDeleteView.as_view(), name="timeline_delete"),

    path("menu/", v.MenuItemListView.as_view(), name="menuitem_list"),
    path("menu/add/", v.MenuItemCreateView.as_view(), name="menuitem_add"),
    path("menu/<int:pk>/edit/", v.MenuItemUpdateView.as_view(), name="menuitem_edit"),
    path("menu/<int:pk>/delete/", v.MenuItemDeleteView.as_view(), name="menuitem_delete"),

    # Contact messages
    path("messages/", v.ContactMessageListView.as_view(), name="message_list"),
    path("messages/<int:pk>/", v.ContactMessageDetailView.as_view(), name="message_detail"),
    path("signups/prayer/", v.PrayerListView.as_view(), name="prayer_list"),
    path("signups/newsletter/", v.NewsletterListView.as_view(), name="newsletter_list"),

    # Users (superuser only; full management stays in /django-admin/)
    path("users/", v.UserListView.as_view(), name="user_list"),
]

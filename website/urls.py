from django.urls import path

from . import views

app_name = "website"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("churches/", views.church_list, name="church_list"),
    path("churches/<slug:slug>/", views.church_detail, name="church_detail"),
    path("ministries/", views.ministry_list, name="ministry_list"),
    path("ministries/<slug:slug>/", views.ministry_detail, name="ministry_detail"),
    path("bible-school/", views.bible_school, name="bible_school"),
    path("events/", views.event_list, name="event_list"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("gallery/", views.gallery, name="gallery"),
    path("gallery/<slug:slug>/", views.gallery_album, name="gallery_album"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("contact/", views.contact, name="contact"),
    path("pages/<slug:slug>/", views.flatpage, name="flatpage"),
]

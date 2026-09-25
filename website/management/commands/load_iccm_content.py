"""
Load the real ICCM website content (from the "For web site" Word document) into the CMS.

    python manage.py load_iccm_content                # add / update the real content
    python manage.py load_iccm_content --remove-demo  # ...and delete the seed_demo_data samples

Everything this command writes is ordinary CMS data: afterwards every page, text and
photo can be edited or replaced from /cms/ like any other content. Safe to re-run —
records are matched by name/title, and photos already loaded are not uploaded twice.
"""
import datetime
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from website import models as m

IMG_DIR = Path(__file__).resolve().parent / "iccm_content" / "images"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def paras(*texts):
    return "".join(f"<p>{t}</p>" for t in texts)


def set_image(instance, field_name, filename):
    """Attach IMG_DIR/filename to an ImageField unless that photo is already there."""
    field = getattr(instance, field_name)
    stem = Path(filename).stem
    if field and Path(field.name).name.startswith(stem):
        return
    with open(IMG_DIR / filename, "rb") as fh:
        field.save(filename, File(fh), save=False)


def media_asset(filename, title):
    """Upload a photo to the CMS media library and return its public URL."""
    asset = m.MediaAsset.objects.filter(title=title).first()
    if asset is None:
        asset = m.MediaAsset(title=title)
        with open(IMG_DIR / filename, "rb") as fh:
            asset.file.save(filename, File(fh), save=False)
        asset.save()
    return asset.file.url


# ---------------------------------------------------------------------------
# Content from the Word document (text kept exactly as written)
# ---------------------------------------------------------------------------

TAGLINE = "PREACH, TEACH, BAPTISE."

ABOUT_INTRO = "<strong>India Church of Christ Mission </strong>stands for New Testament Christianity."
ABOUT_COMMISSION = (
    "We give priority to the Great Commission of Jesus. “Therefore go and make disciples of all "
    "nations, baptizing them in the name of the Father and of the Son and of the Holy Spirit, and "
    "teaching them to obey everything I have commanded you”. Mathew 28:19, 20."
)
ABOUT_STARTED = "ICCM ministry started in Kerala in 1996 by Thomas Abraham a native Christian Missionary."
ABOUT_FOCUS = (
    "ICCM’s ministry is primarily focused on two states in India: Punjab and Kerala. Our goal is to "
    "establish churches in places where there are currently no Churches of Christ in the states of "
    "Punjab and Kerala. Through this ministry, we have established 10 local churches in these two "
    "states and have constructed 7 church buildings to provide places for worship and ministry."
)
ABOUT_GOAL = (
    "Our goal is to establish churches in places where there are currently no Churches of Christ in "
    "the states of Punjab and Kerala."
)
ABOUT_PREACHERS = (
    "At present, 15 preachers and evangelists are serving with the India Church of Christ Mission "
    "(ICCM), working in different locations throughout Punjab and Kerala. Their ministry includes "
    "preaching the Gospel, establishing and strengthening local congregations, teaching new "
    "believers, and training Christians for continued service in the Lord."
)

ICTC_NAME = "India Christian Theological College (ICTC)"
ICTC_TEXT = [
    "India Christian Theological College was established in 2000. Our goal is to train young Indian "
    "men and women from different states of India so that they can go out and preach the Gospel to "
    "their own people. Because of the language barrier, we teach our students in English.",
    "India Christian Theological College is accredited by the International Association for "
    "Theological Accreditation (IATA). The college offers a five-year Master of Divinity (M.Div.), a "
    "three-year Bachelor of Theology (B.Th.), and a three-year Diploma in Theology (D.Th.) and one "
    "year preachers intensive training program.",
    "We have trained hundreds of students, and many of our graduates are now serving the Lord in "
    "different parts of India.",
]
ICTC_COURSES = [
    ("Master of Divinity (M.Div.)", "5 years"),
    ("Bachelor of Theology (B.Th.)", "3 years"),
    ("Diploma in Theology (D.Th.)", "3 years"),
    ("Preachers Intensive Training Program", "1 year"),
]

SOCIAL_VERSE = (
    "<blockquote><p>Jesus said ‘Truly I tell you, whatever you did for one of the least of these "
    "brothers and sisters of mine, you did for me.’ Matthew 25:40</p></blockquote>"
)

# (name, icon, featured, [photos: first is the main image], [paragraphs], extra_html_before)
MINISTRIES = [
    ("Monthly Fellowship Meetings of Local Churches", "groups", True,
     ["fellowship-3.jpeg", "fellowship-1.jpeg", "fellowship-2.jpeg"],
     ["On the second Saturday of every month, Christians from all our local churches come together at "
      "one of the local churches for a time of prayer, worship, Bible study, and fellowship. The meeting "
      "is hosted by a different local church each month, giving members from the various congregations "
      "an opportunity to visit and fellowship with one another.",
      "These monthly gatherings help Christians from different churches get to know one another, build "
      "stronger relationships, encourage and support each other in their faith, and grow together as "
      "the body of Christ. The meetings also provide an opportunity for the members to share their "
      "experiences, pray for one another, and encourage one another in their Christian lives and ministry."],
     ""),
    ("Preachers' Meetings", "record_voice_over", False, [],
     ["Once a month, all the preachers and evangelists serving with ICCM gather together either at the "
      "ICCM headquarters or at one of the local churches for a time of prayer, fellowship, and mutual "
      "encouragement.",
      "These monthly meetings provide an important opportunity for our ministry workers to share their "
      "experiences, including both the blessings and successes they have seen in their ministry as well "
      "as the challenges and struggles they face. They are able to discuss their experiences, learn from "
      "one another, and seek guidance and encouragement from their fellow workers.",
      "The meetings also give the preachers and evangelists an opportunity to pray for one another and "
      "for the different ministries they are involved in. By sharing their joys, concerns, and "
      "challenges, they encourage and strengthen one another to remain faithful in serving the Lord and "
      "proclaiming the Gospel. These gatherings help promote unity, cooperation, and stronger fellowship "
      "among the ICCM ministry workers."],
     ""),
    ("Outreach Program", "campaign", False, [],
     ["As part of its outreach ministry, ICCM carries out various evangelistic activities to reach "
      "people in the community with the message of the Gospel. These activities include open-air "
      "preaching, three or four days evening Gospel preaching conventions, distributing Gospel tracts "
      "and Bibles, visiting homes, and engaging in personal evangelism.",
      "Our preachers and evangelists regularly go into the communities to meet people, share the Word "
      "of God, and pray with those who are willing to receive prayer. Through personal conversations "
      "and home visits, they have opportunities to build relationships with people and share the "
      "Gospel in a more personal way.",
      "We also distribute Bibles and Gospel tracts to help people learn more about God's Word. Those "
      "who show an interest in learning more about the Gospel are invited to attend our local church "
      "services, Bible studies, and other fellowship gatherings. Through these outreach efforts, ICCM "
      "seeks to share the Gospel, encourage people to study the Bible, and help them become followers "
      "of Christ."],
     ""),
    ("Youth and Teen Camps", "diversity_3", True,
     ["camp-2.jpeg", "camp-1.jpeg", "camp-3.jpeg"],
     ["Every year, during the school summer vacation, ICCM conducts special camps for teenagers and "
      "young people. These camps provide a valuable opportunity to spend time with young people, teach "
      "them the Word of God, encourage them to develop a personal relationship with Christ, and guide "
      "them toward making wise and responsible choices in life.",
      "During the camps, the participants take part in Bible lessons, prayer, worship, fellowship, "
      "group discussions, and various activities. We address important issues that young people face "
      "today and encourage them to remain faithful to biblical values and principles.",
      "We consider these camps an important ministry for helping young people choose a positive and "
      "Christ-centered path for their lives. We encourage them to avoid harmful influences such as drug "
      "abuse and sexual immorality and to make choices that honor God. Our desire is to help them "
      "understand the Gospel, accept Jesus Christ as their personal Saviour, and grow in their faith so "
      "that they may live for Christ and become faithful Christian leaders in the future."],
     ""),
    ("Vacation Bible Schools", "child_care", True,
     ["vbs-2.jpeg", "vbs-1.jpeg", "vbs-3.jpeg"],
     ["Every year, all ICCM local churches conduct Vacation Bible Schools for children in their "
      "communities. These programs are usually held for five or six days during the school vacation and "
      "provide a wonderful opportunity for children to learn about the Bible in a joyful and engaging "
      "environment.",
      "During the Vacation Bible School, children learn Bible stories, new songs, action songs, and "
      "Bible verses. They are also given opportunities to express and develop their God-given talents "
      "through singing, recitation, Bible lessons, group activities, and other creative programs. The "
      "children enjoy fellowship with one another while learning important biblical values and teachings.",
      "The final day of the Vacation Bible School is often marked by a special outreach rally. The "
      "children, together with teachers and church members, walk through the surrounding villages or "
      "towns while singing Christian songs, reciting Bible verses, and sharing Christian messages and "
      "slogans. This provides an opportunity for the church to reach out to the wider community and "
      "share the message of Christ.",
      "Both Christian and non-Christian families participate in these programs, giving ICCM an "
      "opportunity to build relationships with families in the community and introduce children and "
      "parents to the teachings of the Bible. Through Vacation Bible Schools, ICCM seeks to encourage "
      "children in their faith and reach families with the message of the Gospel."],
     ""),
    ("Ladies' Meetings", "woman", True,
     ["ladies-1.jpeg", "ladies-2.jpeg"],
     ["Once every three months, the women from all the ICCM local churches gather together at one of "
      "the churches for a special day of prayer, fellowship, and spiritual encouragement. The meeting "
      "is hosted by a different local church from time to time, giving women from various congregations "
      "an opportunity to meet and fellowship with one another.",
      "During this one-day gathering, the women spend time in prayer, worship, singing, fellowship, and "
      "studying the Word of God. They also have opportunities to share their experiences, encourage one "
      "another, and pray for their families, churches, and ministries.",
      "These meetings help strengthen the spiritual lives of the women and build closer relationships "
      "among members from the different ICCM churches. They also encourage the women to support one "
      "another and to remain faithful in their service to the Lord, their families, and the church."],
     ""),
    ("Social Work", "volunteer_activism", True,
     ["social-2.jpeg", "social-1.jpeg", "social-3.jpeg"],
     ["In addition to meeting the spiritual needs of people, ICCM also seeks to help meet the physical "
      "and practical needs of poor and needy people in our communities. We provide assistance to "
      "individuals and families who are facing financial difficulties and other challenging circumstances.",
      "ICCM provides various forms of practical support, including food, clothing, medical assistance, "
      "and school supplies for children and young people attending schools and colleges. Through these "
      "efforts, we seek to bring encouragement and relief to families who are experiencing hardship.",
      "We consider these social ministries a valuable opportunity to demonstrate the love of Christ "
      "through practical action. By serving people and caring for their needs, we seek to reflect the "
      "compassion of our Lord and Saviour Jesus Christ. At the same time, we look for opportunities to "
      "share the Gospel and tell people about the saving grace and mercy of Jesus Christ.",
      "Through both our words and our actions, ICCM desires to serve people with love, compassion, and "
      "dignity and to be a blessing to those who are in need."],
     SOCIAL_VERSE),
]


# ---------------------------------------------------------------------------
# Supporting content written from the document, replacing the demo text
# ---------------------------------------------------------------------------

MINISTRY_DETAILS = {
    "Monthly Fellowship Meetings of Local Churches": (
        "Second Saturday of every month", "Hosted by a different local church each month"),
    "Preachers' Meetings": ("Once a month", "ICCM headquarters or one of the local churches"),
    "Outreach Program": ("Throughout the year", "Communities across Punjab and Kerala"),
    "Youth and Teen Camps": ("Every year, during the school summer vacation", "Punjab and Kerala"),
    "Vacation Bible Schools": ("Five or six days during the school vacation, every year",
                               "All ICCM local churches"),
    "Ladies' Meetings": ("Once every three months", "Hosted by one of the ICCM local churches"),
    "Social Work": ("Throughout the year", "Communities across Punjab and Kerala"),
}

TIMELINE_TEXT = {
    "1996": "Thomas Abraham, a native Christian missionary, started the ministry of ICCM in Kerala.",
    "2000": "ICTC began training young men and women from different states of India to preach the "
            "Gospel to their own people.",
    "Today": "ICCM has established 10 local churches and built 7 church buildings in Punjab and "
             "Kerala, with 15 preachers and evangelists serving.",
}

BELIEFS = [
    ("New Testament Christianity",
     "We seek to be the church we read about in the New Testament, following the teaching of "
     "Jesus Christ and His apostles."),
    ("The Great Commission",
     "We give priority to Jesus’ command to go and make disciples of all nations (Matthew 28:19–20)."),
    ("Baptism",
     "Following Jesus’ command, we baptize believers in the name of the Father and of the Son and of "
     "the Holy Spirit."),
    ("Teaching God’s Word",
     "We teach believers to obey everything Christ has commanded, through preaching, Bible study "
     "and training preachers at ICTC."),
    ("Love in Action",
     "We care for the poor and needy, because whatever we do for the least of these, we do for "
     "Christ (Matthew 25:40)."),
]

COURSE_DESCRIPTIONS = {
    "Master of Divinity (M.Div.)":
        "Our most advanced programme: five years of Bible and theological study preparing graduates "
        "to preach, teach and serve in the Lord’s church.",
    "Bachelor of Theology (B.Th.)":
        "A three-year degree programme giving students a firm foundation in the Bible and theology "
        "for Gospel ministry.",
    "Diploma in Theology (D.Th.)":
        "A three-year diploma programme for men and women preparing to serve the Lord and His church.",
    "Preachers Intensive Training Program":
        "A one-year intensive programme that equips preachers to go out and share the Gospel with "
        "their own people.",
}

ICTC_ADMISSION = paras(
    "ICTC welcomes young men and women from different states of India who want to be trained to "
    "preach the Gospel to their own people.",
    "Because our students come from many language backgrounds, all classes are taught in English.",
)
ICTC_REQUIREMENTS = (
    "<ul><li>A sincere desire to serve the Lord and preach the Gospel</li>"
    "<li>Ability to study in English</li>"
    "<li>Choose the programme that fits your calling: M.Div., B.Th., D.Th. or the one-year "
    "preachers intensive training program</li></ul>"
)
ICTC_APPLY = paras(
    "To apply, or to ask about any of our programmes, send us a message through the contact page "
    "and our team will get back to you."
)

BLOG_POSTS = [
    ("Training Preachers for Their Own People", "ictc-3.jpeg", True,
     "Since 2000, India Christian Theological College has trained young Indian men and women to take "
     "the Gospel home.",
     [
         "When India Christian Theological College (ICTC) was established in 2000, the vision was simple: "
         "train young Indian men and women from different states of India, so that they can go out and "
         "preach the Gospel to their own people.",
         "India is a country of many languages. To bring students from different states together in one "
         "classroom, ICTC teaches in English. A student from one state can study alongside students from "
         "many others, and then return home to preach in their own language.",
         "ICTC is accredited by the International Association for Theological Accreditation (IATA) and "
         "offers a five-year Master of Divinity (M.Div.), a three-year Bachelor of Theology (B.Th.), a "
         "three-year Diploma in Theology (D.Th.) and a one-year preachers intensive training program.",
         "Hundreds of students have been trained over the years, and many of our graduates are now "
         "serving the Lord in different parts of India. Please pray for our students and graduates as "
         "they carry the Gospel to their own people.",
     ]),
    ("Vacation Bible Schools: Reaching Children and Their Families", "vbs-2.jpeg", False,
     "Every year, all ICCM local churches open their doors to children for five or six joyful days "
     "of Bible learning.",
     [
         "Every year during the school vacation, all ICCM local churches hold Vacation Bible Schools for "
         "the children in their communities. For five or six days, children learn Bible stories, new "
         "songs, action songs and Bible verses in a joyful setting.",
         "Children also get the chance to use their God-given talents through singing, recitation, Bible "
         "lessons, group activities and other creative programmes.",
         "On the final day, the children walk through the nearby villages and towns with their teachers "
         "and church members, singing Christian songs, reciting Bible verses and sharing messages of "
         "Christ with the wider community.",
         "Both Christian and non-Christian families take part, which gives our churches a wonderful "
         "opportunity to build friendships with families and introduce children and parents to the "
         "teachings of the Bible.",
     ]),
    ("Serving the Least of These", "social-2.jpeg", False,
     "Alongside preaching the Gospel, ICCM helps poor and needy families with food, clothing, "
     "medical help and school supplies.",
     [
         "Jesus said, ‘Truly I tell you, whatever you did for one of the least of these brothers and "
         "sisters of mine, you did for me.’ (Matthew 25:40)",
         "ICCM cares about people’s spiritual needs and their physical needs too. We help individuals "
         "and families facing financial difficulties and other hard circumstances with food, clothing, "
         "medical assistance, and school supplies for children and young people in schools and colleges.",
         "For us, this social work is a way to show the love of Christ through practical action. As we "
         "serve people and care for their needs, we also look for opportunities to share the good news "
         "of the saving grace and mercy of Jesus Christ.",
         "Through both our words and our actions, we want to serve people with love, compassion and "
         "dignity, and to be a blessing to those who are in need.",
     ]),
]

# Records created by seed_demo_data — only removed with --remove-demo.
DEMO = {
    "churches": ["Kottayam Church of Christ", "Kochi Church of Christ", "Alappuzha Church of Christ",
                 "Thrissur Church of Christ", "Kollam Church of Christ", "Ludhiana Church of Christ",
                 "Amritsar Church of Christ"],
    "ministries": ["Youth Ministry", "Bible School Outreach", "Orphan & School Support",
                   "Church Planting", "Graduate Placement"],
    "events": ["Annual Conference 2026", "Youth Camp", "Church Anniversary — Kottayam",
               "Bible School Graduation"],
    "posts": ["A New Congregation in Ludhiana", "Bible School Graduates Nine Students",
              "Youth Camp 2026 Recap", "Building Update: Kollam Church"],
    "leaders": ["Thomas Varghese", "Ranjith Kumar", "Suresh Paul"],
    "beliefs": ["The Scriptures", "The Church", "Salvation", "The Lord's Supper"],
    "timeline": ["Mission Founded", "Bible School Opened", "Punjab Work Begins", "Seven Churches"],
    "stats": ["Churches", "Bible School", "Students Trained", "Years of Service"],
    "courses": ["Certificate in Bible Studies", "Diploma in Ministry", "Advanced Preaching Track"],
    "faculty": ["Ranjith Kumar", "Anna Mathew"],
    "albums": ["Annual Conference 2026"],
    "menu_hide": ["Churches"],
}


class Command(BaseCommand):
    help = "Load the real ICCM website content and photos (from the Word document) into the CMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--remove-demo", action="store_true",
            help="Also delete the sample records created by seed_demo_data and hide the "
                 "Churches menu item (the local church names and addresses are not in the document yet).",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if not IMG_DIR.exists():
            self.stderr.write(f"Photo folder not found: {IMG_DIR}")
            return

        if options["remove_demo"]:
            self.remove_demo()

        self.load_settings()
        self.load_home()
        self.load_about()
        self.load_bible_school()
        self.load_ministries()
        self.load_gallery()
        self.load_events()
        self.load_blog()

        self.stdout.write(self.style.SUCCESS(
            "ICCM content loaded. Review and edit it any time at /cms/."))

    # ------------------------------------------------------------------
    def remove_demo(self):
        d = DEMO
        m.Church.objects.filter(name__in=d["churches"]).delete()
        m.Ministry.objects.filter(name__in=d["ministries"]).delete()
        m.Event.objects.filter(name__in=d["events"]).delete()
        m.BlogPost.objects.filter(title__in=d["posts"]).delete()
        m.BlogCategory.objects.filter(name="Field Reports", posts__isnull=True).delete()
        m.Leader.objects.filter(name__in=d["leaders"]).delete()
        m.BeliefStatement.objects.filter(title__in=d["beliefs"]).delete()
        m.TimelineEvent.objects.filter(title__in=d["timeline"]).delete()
        m.Statistic.objects.filter(label__in=d["stats"]).delete()
        m.BibleSchoolCourse.objects.filter(title__in=d["courses"]).delete()
        m.Faculty.objects.filter(name__in=d["faculty"]).delete()
        m.GalleryImage.objects.filter(title__regex=r"^Gallery photo \d+$").delete()
        m.GalleryAlbum.objects.filter(title__in=d["albums"]).delete()
        m.MenuItem.objects.filter(label__in=d["menu_hide"]).update(is_active=False)

        s = m.SiteSettings.load()
        if s.email == "office@example.org":
            s.email = ""
        if s.phone == "+91 98765 43210":
            s.phone = ""
        if s.whatsapp_number == "919876543210":
            s.whatsapp_number = ""
        if "(sample address)" in s.address:
            s.address = ""
        if s.footer_hours.startswith("Kerala churches: Sunday 9:00 AM"):
            s.footer_hours = ""
        if "Demo content" in s.copyright_text:
            s.copyright_text = "All rights reserved."
        s.save()

        school = m.BibleSchool.load()
        for f in ("admission_info", "requirements", "application_info"):
            setattr(school, f, "")
        school.fees = ""
        for f in ("classroom_image", "hostel_image"):
            setattr(school, f, None)
        school.save()

        self.stdout.write("Removed demo / sample content.")

    # ------------------------------------------------------------------
    def load_settings(self):
        s = m.SiteSettings.load()
        s.site_name = "India Church of Christ Mission"
        s.tagline = TAGLINE
        s.description = "India Church of Christ Mission stands for New Testament Christianity."
        s.utility_bar_text = "Serving Punjab & Kerala since 1996 · 10 Local Churches · ICTC"
        s.footer_about = ("India Church of Christ Mission stands for New Testament Christianity, "
                          "preaching, teaching and baptising across Punjab and Kerala since 1996.")
        s.footer_hours = ("Monthly fellowship: second Saturday of every month\n"
                          "Ladies' meeting: once every three months")
        s.footer_text = "India Church of Christ Mission"
        s.copyright_text = "All rights reserved."
        s.default_seo_title = "India Church of Christ Mission | Punjab & Kerala"
        s.default_seo_description = (
            "ICCM stands for New Testament Christianity, with 10 local churches in Punjab and "
            "Kerala and India Christian Theological College (ICTC).")
        set_image(s, "logo", "logo.jpeg")
        set_image(s, "favicon", "logo.jpeg")
        s.save()

        for label, url, order in [("Home", "/", 0), ("About", "/about/", 1),
                                  ("Ministries", "/ministries/", 3), ("ICTC", "/bible-school/", 4),
                                  ("Events", "/events/", 5), ("Gallery", "/gallery/", 6),
                                  ("Blog", "/blog/", 7), ("Contact", "/contact/", 8)]:
            item = m.MenuItem.objects.filter(url=url).first()
            if item:
                item.label, item.is_active = label, True
                item.save()
            else:
                m.MenuItem.objects.create(label=label, url=url, order=order)

    def load_home(self):
        hero = m.HeroSection.load()
        hero.heading = "PREACH,\nTEACH,\nBAPTISE."
        hero.subheading = "India Church of Christ Mission · Punjab & Kerala"
        hero.description = ("India Church of Christ Mission stands for New Testament Christianity. "
                            "We give priority to the Great Commission of Jesus.")
        hero.button_text, hero.button_url = "About us", "/about/"
        hero.button2_text, hero.button2_url = "Our Ministries", "/ministries/"
        hero.is_active = True
        set_image(hero, "background_image", "home-1.jpeg")
        hero.save()

        welcome = m.HomeAboutSection.load()
        welcome.title = "About us"
        welcome.description = paras(ABOUT_STARTED, ABOUT_FOCUS)
        welcome.button_text, welcome.button_url = "Learn More", "/about/"
        set_image(welcome, "image", "thomas-and-sali.jpeg")
        welcome.save()

        for order, (value, label) in enumerate([
            ("1996", "Ministry started in Kerala"),
            ("10", "Local churches"),
            ("7", "Church buildings"),
            ("15", "Preachers and evangelists"),
        ]):
            m.Statistic.objects.update_or_create(label=label, defaults={"value": value, "order": order})

        cta, _ = m.CallToAction.objects.get_or_create(key="home")
        cta.eyebrow = "Partner With Us"
        cta.heading = "Stand With the Work in Punjab and Kerala"
        cta.description = ("Your prayers and support help our 15 preachers and evangelists share the "
                           "Gospel, strengthen 10 local churches, train students at ICTC and care for "
                           "families in need.")
        cta.button_text, cta.button_url = "Support the Mission", "/contact/#support"
        set_image(cta, "background_image", "fellowship-3.jpeg")
        cta.save()

    def load_about(self):
        map_url = media_asset("map-punjab-kerala.png", "ICCM map — Punjab and Kerala")

        page = m.AboutPage.load()
        page.title = "About us"
        page.introduction = paras(ABOUT_INTRO)
        page.history = (
            paras(ABOUT_STARTED, ABOUT_FOCUS, ABOUT_PREACHERS)
            + f'<p><img src="{map_url}" alt="Map of India showing Punjab and Kerala" '
              f'style="max-width:220px;width:100%;height:auto;"></p>'
        )
        page.mission_statement = paras(ABOUT_COMMISSION)
        page.vision_statement = paras(ABOUT_GOAL)
        set_image(page, "founding_image", "thomas-and-sali.jpeg")
        set_image(page, "today_image", "about-group-1.jpeg")
        page.save()

        leader, _ = m.Leader.objects.get_or_create(name="Thomas and Sali Thomas",
                                                   defaults={"order": 0})
        leader.role = leader.role or "India Church of Christ Mission"
        leader.is_active = True
        set_image(leader, "photo", "thomas-and-sali.jpeg")
        leader.save()

        for order, (year, title) in enumerate([
            ("1996", "ICCM ministry started in Kerala"),
            ("2000", "India Christian Theological College established"),
            ("Today", "10 local churches and 15 preachers"),
        ]):
            m.TimelineEvent.objects.update_or_create(year=year, title=title, defaults={
                "order": order, "description": TIMELINE_TEXT[year]})

        for order, (title, text) in enumerate(BELIEFS):
            m.BeliefStatement.objects.update_or_create(
                title=title, defaults={"description": text, "order": order})

    def load_bible_school(self):
        school = m.BibleSchool.load()
        school.name = ICTC_NAME
        school.description = paras(*ICTC_TEXT)
        set_image(school, "campus_image", "ictc-1.jpeg")
        set_image(school, "students_image", "ictc-2.jpeg")
        set_image(school, "graduation_image", "ictc-3.jpeg")
        school.admission_info = ICTC_ADMISSION
        school.requirements = ICTC_REQUIREMENTS
        school.application_info = ICTC_APPLY
        school.save()

        for order, (title, duration) in enumerate(ICTC_COURSES):
            m.BibleSchoolCourse.objects.update_or_create(
                title=title, defaults={"duration": duration, "order": order,
                                       "description": COURSE_DESCRIPTIONS[title]})

    def load_ministries(self):
        for order, (name, icon, featured, photos, texts, extra) in enumerate(MINISTRIES):
            first_sentence = texts[0].split(". ")[0].rstrip(".") + "."
            ministry, _ = m.Ministry.objects.get_or_create(name=name)
            ministry.icon = icon
            ministry.short_description = first_sentence[:255]
            ministry.description = extra + paras(*texts)
            ministry.status = "published"
            ministry.is_featured = featured
            ministry.meeting_info, ministry.location = MINISTRY_DETAILS[name]
            ministry.order = order
            if photos:
                set_image(ministry, "image", photos[0])
            ministry.save()

            if photos[1:] and not ministry.gallery.exists():
                for i, photo in enumerate(photos[1:]):
                    img = m.MinistryImage(ministry=ministry, caption=name, order=i)
                    set_image(img, "image", photo)
                    img.save()

    def load_gallery(self):
        albums = [
            ("Baptisms", "Believers baptized into Christ through the ministry of ICCM.",
             [(f"baptism-{i:02d}.jpeg", f"Baptism {i}", "worship") for i in range(1, 17)]),
            ("Our Churches", "Members of ICCM local churches in Punjab and Kerala.", [
                ("about-group-1.jpeg", "Church members in Faridkot, Punjab", "punjab"),
                ("about-group-2.jpeg", "Church members gathered together", "punjab"),
                ("about-group-3.jpeg", "Church members gathered together", "punjab"),
                ("home-1.jpeg", "ICCM church members", "worship"),
                ("home-2.jpeg", "ICCM church members", "worship"),
                ("home-3.jpeg", "Bible study", "worship"),
                ("home-4.jpeg", "Baptism", "worship"),
            ]),
            ("Ministries", "Fellowship meetings, camps, Vacation Bible Schools, ladies' meetings "
                           "and social work.", [
                ("fellowship-3.jpeg", "Monthly fellowship meeting", "worship"),
                ("fellowship-1.jpeg", "Monthly fellowship meeting", "worship"),
                ("fellowship-2.jpeg", "Monthly fellowship meeting", "worship"),
                ("camp-2.jpeg", "Youth and teen camp", "youth"),
                ("camp-1.jpeg", "Youth and teen camp", "youth"),
                ("camp-3.jpeg", "Youth and teen camp", "youth"),
                ("vbs-2.jpeg", "Vacation Bible School", "kids"),
                ("vbs-1.jpeg", "Vacation Bible School", "kids"),
                ("vbs-3.jpeg", "Vacation Bible School", "kids"),
                ("ladies-1.jpeg", "Ladies' meeting", "worship"),
                ("ladies-2.jpeg", "Ladies' meeting", "worship"),
                ("social-1.jpeg", "Food kits for families in need", "outreach"),
                ("social-2.jpeg", "Helping a family in need", "outreach"),
                ("social-3.jpeg", "Helping a family in need", "outreach"),
            ]),
            (ICTC_NAME, "India Christian Theological College students and graduates.", [
                ("ictc-1.jpeg", "ICTC students and staff", "school"),
                ("ictc-2.jpeg", "ICTC graduation", "school"),
                ("ictc-3.jpeg", "ICTC graduates", "school"),
            ]),
        ]
        order = 0
        for a_order, (title, description, photos) in enumerate(albums):
            album, _ = m.GalleryAlbum.objects.get_or_create(title=title)
            album.description = description
            album.status = "published"
            album.is_featured = a_order == 0
            album.order = a_order
            set_image(album, "cover_image", photos[0][0])
            album.save()
            for filename, caption, tag in photos:
                key = f"{title} — {Path(filename).stem}"
                img = m.GalleryImage.objects.filter(album=album, description=key).first()
                if img is None:
                    img = m.GalleryImage(album=album, description=key)
                img.title = caption
                img.tag = tag
                img.order = order
                set_image(img, "image", filename)
                img.save()
                order += 1

    def load_events(self):
        """The next three monthly fellowship meetings (second Saturday of each month)."""
        today = timezone.localdate()
        year, month = today.year, today.month
        texts = MINISTRIES[0][4]
        created = 0
        while created < 3:
            first = datetime.date(year, month, 1)
            second_saturday = first + datetime.timedelta(days=(5 - first.weekday()) % 7 + 7)
            if second_saturday >= today:
                name = f"Monthly Fellowship Meeting — {second_saturday:%B %Y}"
                event, _ = m.Event.objects.get_or_create(
                    name=name, defaults={"start_date": second_saturday})
                event.start_date = second_saturday
                event.short_description = (
                    "Christians from all our local churches come together for prayer, worship, "
                    "Bible study and fellowship.")
                event.description = paras(*texts)
                event.venue = "Hosted by one of our local churches"
                event.city = "Punjab & Kerala"
                event.organizer = "India Church of Christ Mission"
                event.status = "published"
                event.is_featured = created == 0
                event.is_completed = False
                set_image(event, "featured_image", "fellowship-3.jpeg")
                event.save()
                created += 1
            month += 1
            if month > 12:
                month, year = 1, year + 1

    def load_blog(self):
        category, _ = m.BlogCategory.objects.get_or_create(name="Ministry")
        now = timezone.now()
        for i, (title, photo, featured, excerpt, texts) in enumerate(BLOG_POSTS):
            post, created = m.BlogPost.objects.get_or_create(
                title=title, defaults={"content": "", "published_at": now - datetime.timedelta(days=i * 7)})
            post.excerpt = excerpt
            post.content = paras(*texts)
            post.category = category
            post.author_name = "India Church of Christ Mission"
            post.status = "published"
            post.is_featured = featured
            set_image(post, "featured_image", photo)
            post.save()

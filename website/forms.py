from django import forms

from .models import ContactMessage, NewsletterSubscriber, PrayerListSignup


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "reason", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Phone (optional)"}),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Subject"}),
            "reason": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Your message"}),
        }


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ["email"]
        widgets = {
            "email": forms.EmailInput(attrs={
                "class": "form-control input-newsletter", "placeholder": "Your email address"
            }),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        return email

    def validate_unique(self):
        # Signing up again with the same address is fine: save() just keeps the
        # existing row (and reactivates it), instead of showing an error.
        pass

    def save(self, commit=True):
        email = self.cleaned_data["email"]
        NewsletterSubscriber.objects.filter(email=email, is_active=False).update(is_active=True)
        obj, _ = NewsletterSubscriber.objects.get_or_create(email=email, defaults={"is_active": True})
        return obj


class PrayerListForm(forms.ModelForm):
    class Meta:
        model = PrayerListSignup
        fields = ["name", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Your email"}),
        }

from django.db import models
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings
import uuid
import os
from django.utils.text import slugify


# ============================ #
#      CAMPAIGN MODEL           #
# ============================ #
class Campaign(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('archived', 'Archived'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    email_template = models.ForeignKey('EmailTemplate', on_delete=models.SET_NULL, null=True, blank=True)
    landing_page = models.ForeignKey('LandingPage', on_delete=models.SET_NULL, null=True, blank=True)
    url = models.URLField(blank=True, null=True)
    launch_date = models.DateTimeField(blank=True, null=True)
    send_emails_by = models.DateTimeField(blank=True, null=True)
    sending_profile = models.ForeignKey('SendingProfile', on_delete=models.SET_NULL, null=True, blank=True)
    groups = models.ManyToManyField('Group', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    fake_landing_page_url = models.CharField(max_length=255, blank=True, null=True)  # Store the fake URL

    def send_emails(self):
        if self.launch_date and timezone.now() < self.launch_date:
            print(f"[SKIP] Too early for campaign '{self.name}'")
            return

        print(f"[SENDING] Campaign: {self.name}")
        group_emails = [group.email for group in self.groups.all()]
        print(f"[TO] Emails: {group_emails}")

        if not group_emails:
            print("[ABORT] No emails to send.")
            return

        subject = self.email_template.subject
        original_body = self.email_template.html_body or self.email_template.text_body

        for email in group_emails:
            try:
                # Determine the correct landing page link
                if "facebook" in self.landing_page.name.lower():
                    landing_url = "http://127.0.0.1:8003/"
                elif "linkedin" in self.landing_page.name.lower():
                    landing_url = "http://127.0.0.1:8003/linkedin"
                else:
                    fake_landing_page = FakeLandingPage.objects.filter(original_landing_page=self.landing_page).first()
                    if not fake_landing_page:
                        print(f"[ERROR] No fake landing page found for landing page: {self.landing_page.url}")
                        continue
                    landing_url = fake_landing_page.url

                # Add unique token to URL
                unique_token = uuid.uuid4().hex
                final_url = f"{landing_url}?campaign_id={self.id}&token={unique_token}"

                # Save the fake landing page URL
                self.fake_landing_page_url = final_url
                self.save()

                # Wrap existing images in <a href="...">...</a>
                modified_body = original_body.replace(
                    "<img ",
                    f'<a href="{final_url}"><img '
                ).replace(
                    "/>", "/></a>"
                )

                msg = EmailMultiAlternatives(
                    subject=subject,
                    body="This is an HTML email.",
                    from_email=self.sending_profile.smtp_user,
                    to=[email]
                )
                msg.attach_alternative(modified_body, "text/html")
                msg.send()

                print(f"Creating Result for email: {email}, campaign_id: {self.id}, unique_token: {unique_token}")
                Result.objects.create(
                    campaign=self,
                    recipient=email,
                    token=unique_token,
                    status='sent'
                )

            except Exception as e:
                print(f"[ERROR] {email}: {e}")
                Result.objects.create(
                    campaign=self,
                    recipient=email,
                    status='error',
                    timestamp=timezone.now()
                )

        if self.status != 'active':
            self.status = 'active'
            self.save(update_fields=['status'])


class FakeLandingPage(models.Model):
    url = models.URLField()
    html_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rid = models.CharField(max_length=20, unique=True)  # Unique identifier for each fake page
    campaign = models.ForeignKey('Campaign', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    original_landing_page = models.ForeignKey('LandingPage', on_delete=models.CASCADE, null=True)

    def save(self, *args, **kwargs):
        if not self.rid:
            self.rid = uuid.uuid4().hex  # Generate a unique RID if it's not already set
        super().save(*args, **kwargs)

        file_name = f"{slugify(self.original_landing_page.name)}-fake-landing-page.html"
        file_path = os.path.join(settings.BASE_DIR, 'fake_landing_pages', file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'w') as file:
            file.write(self.html_content)


class FakeLandingPageSubmission(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    fake_landing_page = models.ForeignKey(FakeLandingPage, on_delete=models.CASCADE, related_name='fake_landing_page_submission')
    user_email = models.EmailField()
    user_name = models.CharField(max_length=100)
    submitted_data = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    unique_token = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Submission by {self.user_email} for campaign {self.campaign.id}"


class EmailTemplate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    text_body = models.TextField(blank=True, null=True)
    html_body = models.TextField(blank=True, null=True)
    envelope_sender_email = models.EmailField(max_length=255, blank=True, null=True)
    envelope_sender_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class LandingPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True, null=True, blank=True)
    html_content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_fake = models.BooleanField(default=False)


class Group(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100, default="Unknown")
    last_name = models.CharField(max_length=100, default="Unknown")
    email = models.EmailField(unique=True, default="default@example.com")
    position = models.CharField(max_length=100, default="N/A")
    number_of_members = models.PositiveIntegerField(default=0)
    modified_date = models.DateTimeField(default=timezone.now)
    csv_file = models.FileField(upload_to='csv_uploads/', blank=True, null=True)

    def __str__(self):
        return self.name


class SendingProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    smtp_host = models.CharField(max_length=255, blank=True, null=True)
    smtp_port = models.PositiveIntegerField(blank=True, null=True)
    smtp_user = models.CharField(max_length=255, blank=True, null=True)
    smtp_password = models.CharField(max_length=255, blank=True, null=True)
    use_tls = models.BooleanField(default=True, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        super().save(*args, **kwargs)


class Result(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='results')
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    recipient = models.EmailField()
    email_opened = models.BooleanField(default=False)
    link_clicked = models.BooleanField(default=False)
    data_submitted = models.BooleanField(default=False)
    status = models.CharField(
        max_length=50,
        choices=[('sent', 'Sent'), ('opened', 'Opened'), ('clicked', 'Clicked')],
        default='sent'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=255, unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"{self.status} for {self.campaign.name} ({self.recipient})"

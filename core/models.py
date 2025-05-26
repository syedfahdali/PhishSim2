from django.db import models
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User
from django.conf import settings
from bs4 import BeautifulSoup
from urllib.parse import quote
import uuid
# ============================
#      CAMPAIGN MODEL
# ============================
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
        body = self.email_template.html_body or self.email_template.text_body

        # Loop through all emails and send the email with fake landing page URL
        for email in group_emails:
            try:
                # Get the selected landing page URL
                landing_page_url = self.landing_page.url

                # Fetch the corresponding fake landing page linked to the original landing page
                fake_landing_page = FakeLandingPage.objects.filter(original_landing_page=self.landing_page).first()

                if not fake_landing_page:
                    print(f"[ERROR] No fake landing page found for landing page: {landing_page_url}")
                    continue  # Skip this email if no fake landing page is found for this original landing page

                # Use the fake landing page URL (NO hardcoding of domain)
                fake_landing_page_url = fake_landing_page.url

                # Generate a unique token for tracking
                unique_token = uuid.uuid4().hex
                # Append the unique token correctly (single parameter)
                fake_landing_page_url_with_token = f"{fake_landing_page_url}?rid={fake_landing_page.rid}&campaign_id={self.id}&token={unique_token}"

                # Store the fake landing page URL in the campaign model (optional: you can also store this for each email)
                self.fake_landing_page_url = fake_landing_page_url_with_token
                self.save()

                print(f"[FAKE PAGE URL] Assigned fake URL: {fake_landing_page_url_with_token}")

                # Prepare the tracking URL for tracking and redirect (track_and_redirect view)
                tracking_url = f"/track_and_redirect/{self.id}/{unique_token}/"  # Track and redirect view URL

                # Prepare the email body with the injected fake URL for tracking
                body_with_tracking = f'Click this link to track your activity: <a href="{tracking_url}">Track Your Click</a>'
                body_with_fake_link = body_with_tracking + f"<br>Fake Landing Page: <a href='{fake_landing_page_url_with_token}'>Click Here</a>"

                # Send the email with the fake landing page URL
                msg = EmailMultiAlternatives(
                    subject=self.email_template.subject,
                    body="This is an HTML email.",
                    from_email=self.sending_profile.smtp_user,
                    to=[email]
                )
                msg.attach_alternative(body_with_fake_link, "text/html")
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

        # ✅ Mark campaign active
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
    
    # Link to the original LandingPage from which the fake page was created
    original_landing_page = models.ForeignKey('LandingPage', on_delete=models.CASCADE, null=True)

class FakeLandingPageSubmission(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, null=True, blank=True)
    fake_landing_page = models.ForeignKey(FakeLandingPage, on_delete=models.CASCADE, related_name='fake_landing_page_submission')
    user_email = models.EmailField()  # You may have other user-related fields
    user_name = models.CharField(max_length=100)
    submitted_data = models.TextField()  # Form data submitted
    submitted_at = models.DateTimeField(auto_now_add=True)
    unique_token = models.CharField(max_length=64, blank=True, null=True)  # Add this line to store the token

    def __str__(self):
        return f"Submission by {self.user_email} for campaign {self.campaign.id}"



# ============================
#     EMAIL TEMPLATE MODEL
# ============================
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

# ============================
#         LANDING PAGE
# ============================
class LandingPage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    url = models.URLField(unique=True, null=True, blank=True)
    html_content = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_fake = models.BooleanField(default=False) 
# ============================
#         GROUP MODEL
# ============================
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

# ============================
#    SENDING PROFILE MODEL
# ============================
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

# ============================
#         RESULT MODEL
# ============================
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

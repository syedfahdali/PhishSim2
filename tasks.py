# yourapp/tasks.py

from celery import shared_task
from django.utils import timezone
from core.models import Campaign

@shared_task
def send_campaign_emails_task():
    now = timezone.now()
    campaigns = Campaign.objects.filter(send_emails_by__lte=now, is_active=True)
    for campaign in campaigns:
        campaign.send_campaign_emails()
        campaign.is_active = False
        campaign.save()

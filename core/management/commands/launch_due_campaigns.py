from django.core.management.base import BaseCommand
from core.models import Campaign
from django.utils import timezone

class Command(BaseCommand):
    help = "Launch campaigns whose launch date has arrived."

    def handle(self, *args, **kwargs):
        now = timezone.now()
        due_campaigns = Campaign.objects.filter(status='draft', launch_date__lte=now)

        for campaign in due_campaigns:
            self.stdout.write(f"Launching {campaign.name}")
            campaign.send_emails()  #  Let send_emails() handle status change
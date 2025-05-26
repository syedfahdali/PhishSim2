# ============================
#         apps.py
# ============================

from django.apps import AppConfig
import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        def start_scheduler():
            from core.models import Campaign

            scheduler = BackgroundScheduler()
            if not scheduler.running:

                def launch_due_campaigns():
                    print("[SCHEDULER EXECUTION] Checking for due campaigns...")
                    now = timezone.now()
                    due_campaigns = Campaign.objects.filter(status='draft', launch_date__lte=now)
                    print(f"[FOUND] {due_campaigns.count()} draft campaigns eligible for launch")
                    for campaign in due_campaigns:
                        print(f"[LAUNCHING] {campaign.name}")
                        campaign.send_emails()

                scheduler.add_job(launch_due_campaigns, 'interval', minutes=1)
                scheduler.start()
                print("[SCHEDULER STARTED] Running every 1 minute")

        threading.Thread(target=start_scheduler).start()

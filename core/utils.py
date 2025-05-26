from django.core.mail import send_mail

#from phishsim_fyp.core.models import Result
from .models import Result
def send_campaign_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        'your_email@gmail.com',  # From email
        recipient_list,  # List of recipient emails
        fail_silently=False,
    )


def log_campaign_result(campaign, recipient, status):
    result = Result(campaign=campaign, recipient=recipient, status=status)
    result.save()

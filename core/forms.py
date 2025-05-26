from django import forms
from .models import Campaign, EmailTemplate, LandingPage,Group, SendingProfile
from django.utils import timezone
import re
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ['name', 'email_template', 'landing_page', 'url', 'launch_date', 'send_emails_by', 'sending_profile', 'groups']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Campaign name', 'class': 'form-control'}),
            'email_template': forms.Select(attrs={'class': 'form-control'}),
            'landing_page': forms.Select(attrs={'class': 'form-control'}),
            'url': forms.URLInput(attrs={'placeholder': 'http://192.168.1.1', 'class': 'form-control'}),
            'launch_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'send_emails_by': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'sending_profile': forms.Select(attrs={'class': 'form-control'}),
            'groups': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    # Adding dropdown choices for models
    email_template = forms.ModelChoiceField(queryset=EmailTemplate.objects.all(), required=True)
    landing_page = forms.ModelChoiceField(queryset=LandingPage.objects.all(), required=True)
    sending_profile = forms.ModelChoiceField(queryset=SendingProfile.objects.all(), required=True)
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), required=True)
    
class EmailTemplateForm(forms.ModelForm):
    envelope_sender_email = forms.CharField(
        max_length=255,
        required=False,  # Remove required=True to handle validation in clean
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe <john.doe@example.com>'}),
        label="Envelope Sender"
    )

    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'text_body', 'html_body', 'envelope_sender_email', 'envelope_sender_name', 'created_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'text_body': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
            'html_body': forms.Textarea(attrs={'class': 'form-control'}), 
            'envelope_sender_name': forms.TextInput(attrs={'class': 'form-control'}),
            'created_at': forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['body_type'] = forms.ChoiceField(
            choices=[('text', 'Text'), ('html', 'HTML')],
            widget=forms.RadioSelect,
            initial='html'
        )

        if self.instance.pk: 
            self.fields['created_at'].widget.attrs['readonly'] = True
            self.fields['created_at'].initial = self.instance.created_at
        else:  
            self.fields['created_at'].initial = timezone.now()

        if self.instance.pk and (self.instance.envelope_sender_name or self.instance.envelope_sender_email):
            sender_name = self.instance.envelope_sender_name or ''
            sender_email = self.instance.envelope_sender_email or ''
            self.fields['envelope_sender_email'].initial = (
                f"{sender_name} <{sender_email}>" if sender_name and sender_email else sender_email or sender_name
            )

    def clean(self):
        cleaned_data = super().clean()

        # Check for empty required fields with user-friendly messages
        if not cleaned_data.get('name'):
            self.add_error('name', 'Name is required.')
        if not cleaned_data.get('subject'):
            self.add_error('subject', 'Subject is required.')
        if not cleaned_data.get('envelope_sender_email'):
            self.add_error('envelope_sender_email', 'Envelope Sender is required.')

        # Validate body_type and ensure either text_body or html_body is provided based on body_type
        body_type = cleaned_data.get('body_type')
        text_body = cleaned_data.get('text_body')
        html_body = cleaned_data.get('html_body')

        if body_type == 'text' and not text_body:
            self.add_error('text_body', 'Email body is required.')
        elif body_type == 'html' and not html_body:
            self.add_error('html_body', 'Email body is required.')
        elif body_type == 'text' and html_body:
            self.add_error('html_body', 'Email body should be empty for Text type.')
        elif body_type == 'html' and text_body:
            self.add_error('text_body', 'Email body should be empty for HTML type.')

        envelope_sender_full = cleaned_data.get('envelope_sender_email', '').strip()

        if envelope_sender_full:
            email_pattern = re.compile(r'^(?:"?([^"<]+)"?\s+)?<([^>]+)>$|^([^<>\s@]+@[^<>\s@]+)$')
            match = email_pattern.match(envelope_sender_full)
            if match:
                name, email_in_brackets, standalone_email = match.groups()
                cleaned_data['envelope_sender_name'] = name.strip() if name and name.strip() else ''
                cleaned_data['envelope_sender_email'] = (email_in_brackets or standalone_email or '').strip()
            else:
                cleaned_data['envelope_sender_name'] = ''
                cleaned_data['envelope_sender_email'] = envelope_sender_full
        else:
            cleaned_data['envelope_sender_name'] = ''
            cleaned_data['envelope_sender_email'] = ''

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        body_type = self.cleaned_data['body_type']

        if body_type == 'text':
            instance.html_body = None
        else:  # html
            instance.text_body = None

        if not self.instance.pk:
            instance.created_at = timezone.now()

        instance.envelope_sender_name = self.cleaned_data['envelope_sender_name']
        instance.envelope_sender_email = self.cleaned_data['envelope_sender_email']

        if commit:
            instance.save()
        return instance

class LandingPageForm(forms.ModelForm):
    class Meta:
        model = LandingPage
        fields = ['name', 'url', 'html_content']
        widgets = {
            'html_content': forms.Textarea(attrs={'style': 'display: none;'}),
        }
    def save(self, commit=True):
            instance = super(LandingPageForm, self).save(commit=False)
            if not instance.pk:  # Only set created_at for new instances
                instance.created_at = timezone.now()
            if commit:
                instance.save()
            return instance
    
class GroupForm(forms.ModelForm):
    csv_file = forms.FileField(required=False, help_text="Upload CSV file for bulk import")

    class Meta:
        model = Group
        fields = ['name', 'first_name', 'last_name', 'email', 'position', 'csv_file']
       
class SendingProfileForm(forms.ModelForm):
    class Meta:
        model = SendingProfile
        fields = ['name', 'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'use_tls']

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
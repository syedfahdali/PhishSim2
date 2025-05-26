from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Campaign, EmailTemplate, LandingPage, Group,SendingProfile, Result

#admin.site.register(Campaign)
admin.site.register(EmailTemplate)
#admin.site.register(LandingPage)
admin.site.register(Group)
admin.site.register(SendingProfile)
admin.site.register(Result)

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'landing_page', 'url', 'launch_date')
    search_fields = ('name', 'user__username')

admin.site.register(Campaign, CampaignAdmin)
admin.site.register(LandingPage)
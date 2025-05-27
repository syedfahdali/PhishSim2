from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns-new/', views.new_campaign, name='new_campaign'),
    path('email-templates/', views.email_template_list, name='email_template_list'),
    path('landing-pages/', views.landing_page_list, name='landing_page_list'),
    path('User$Groups', views.group_list, name='group_list'),
    path('sending-profiles/', views.sending_profile_list, name='sending_profile_list'),
    path('results/', views.result_list, name='result_list'),

    # Campaign CRUD
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/update/<int:pk>/', views.campaign_update, name='campaign_update'),
    path('campaign/<int:campaign_id>/delete/', views.delete_campaign, name='delete_campaign'),
    path('campaign/<int:campaign_id>/archive/', views.archive_campaign, name='archive_campaign'),
    path('campaign/<int:campaign_id>/edit/', views.edit_campaign, name='edit_campaign'),
    path('campaign/<int:campaign_id>/activate/', views.activate_campaign, name='activate_campaign'),
    path('campaign/<int:campaign_id>/export/', views.export_campaign_csv, name='export_campaign_csv'),
    path('campaign/results/', views.campaign_results, name='campaign_results'),
    path('track/<int:campaign_id>/<str:recipient_email>/', views.track_email_open, name='track_email_open'),
    path('track_and_redirect/<int:campaign_id>/<str:unique_token>/', views.track_and_redirect, name='track_and_redirect'),
    path('fake/<int:campaign_id>/<str:unique_token>/', views.handle_fake_landing_page_submission, name='handle_fake_landing_page_submission'),


    # EmailTemplate CRUD
    path('email-templates/', views.email_template_list, name='emailtemplate_list'), 
    path('email-templates/new/', views.create_email_template, name='create_email_template'),
    path('emailtemplates/update/<int:pk>/', views.emailtemplate_update, name='emailtemplate_update'),
    path('emailtemplates/delete/<int:id>/', views.emailtemplate_delete, name='emailtemplate_delete'),    
    path('emailtemplates/copy/<int:pk>/', views.copy_email_template, name='copy_email_template'), 
    path('parse-email/', views.parse_email, name='parse_email'),
    path('parse-raw-email/', views.parse_raw_email, name='parse_raw_email'),
    path('upload-image/', views.upload_image, name='upload_image'),

    # LandingPage CRUD
    path('landing-pages/', views.landing_page_list, name='landingpage_list'),  # Add this line
    path('landing-pages/new/', views.create_landing_page, name='create_landing_page'),
    path('import-website/', views.import_website, name='import_website'),
    path('landingpages/update/<int:pk>/', views.landingpage_update, name='landingpage_update'),
    path('landingpages/delete/<int:pk>/', views.landingpage_delete, name='landingpage_delete'),
    path('parse-website/', views.parse_website, name='parse_website'),
    path('landing_page/<int:id>/', views.landing_page_view, name='landing_page_view'),


    # SendingProfile CRUD
    path('sending-profiles/', views.sending_profile_list, name='sendingprofile_list'),
    path('sending-profiles/new/', views.create_sending_profile, name='create_sending_profile'),
    path('sendingprofiles/update/<int:pk>/', views.sendingprofile_update, name='sendingprofile_update'),
    path('sendingprofiles/delete/<int:pk>/', views.sendingprofile_delete, name='sendingprofile_delete'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),
    
    # Group CRUD
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/update/<int:pk>/', views.update_group, name='update_group'),
    path('groups/delete/<int:pk>/', views.delete_group, name='delete_group'),

    #urls for login , logout and registration
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_register, name='register'),
    #path('activate/<uid>/<token>/', views.activate, name='activate'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('resend-activation/', views.resend_activation_email, name='resend_activation'),

    path('dashboard/results/', views.result_dashboard, name='Index'),
    path('campaign/launch/<int:campaign_id>/', views.launch_campaign, name='launch_campaign'),

]



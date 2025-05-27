from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from core import views as core_views  # Replace 'core' with your app name
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve
from django.urls import re_path

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Protected core views
    path('campaigns/', login_required(core_views.campaign_list), name='campaign_list'),
    path('campaigns/create/', login_required(core_views.create_campaign), name='campaign_create'),
    path('campaigns/update/<int:pk>/', login_required(core_views.campaign_update), name='campaign_update'),
    path('campaigns/delete/<int:pk>/', login_required(core_views.delete_campaign), name='delete_campaign'),

    # Auth
    path('login/', core_views.user_login, name='login'),
    path('logout/', core_views.user_logout, name='logout'),
    path('register/', core_views.user_register, name='register'),

    path('', include('core.urls')),  # Core app URLs
]

# ✅ Serve static files in production mode (DEBUG=False)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATICFILES_DIRS[0],
        }),
    ]
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

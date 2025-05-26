"""
URL configuration for phishsim_fyp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required

# Import all app views to apply login_required globally
from core import views as core_views  # Replace 'core' with your app name
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Protect views from core app
    path('campaigns/', login_required(core_views.campaign_list), name='campaign_list'),
    path('campaigns/create/', login_required(core_views.create_campaign), name='campaign_create'),
    path('campaigns/update/<int:pk>/', login_required(core_views.campaign_update), name='campaign_update'),
    path('campaigns/delete/<int:pk>/', login_required(core_views.delete_campaign), name='delete_campaign'),

    
    # Authentication-related views
    path('login/', core_views.user_login, name='login'),
    path('logout/', core_views.user_logout, name='logout'),
    path('register/', core_views.user_register, name='register'),

    # Include other app-specific URLs
    path('', include('core.urls')),  # Include core app URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)







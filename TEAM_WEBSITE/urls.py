
from django.contrib import admin
from django.urls import path, include
# To use the media declared in the settings.py file
from . import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('team.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
    path('store/', include('store.urls')),
    path('cart/', include('cart.urls')),
    path('payment/', include('payment.urls')),
    path('teamAPI/', include('teamAPI.urls')),
    path('services/', include('services.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Include the media files and Urls here.


# Configure admin titles
admin.site.site_header = "Team Administrative Section"
admin.site.site_title = "StatsHub"
admin.site.index_title = "Welcome To The StatsHub Admin Area..."


# At the very bottom of your urls.py file
from django.contrib.auth import get_user_model

try:
    User = get_user_model()
    # Check if our new temporary master admin already exists
    if not User.objects.filter(username='masteradmin').exists():
        # This creates a brand new administrator from scratch
        User.objects.create_superuser('masteradmin', 'admin@statshub.com', 'SolomonStats2026!')
except Exception as e:
    pass
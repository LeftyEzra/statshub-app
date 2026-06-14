
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
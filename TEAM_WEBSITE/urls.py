
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
    # This automatically grabs the first superuser account it finds in your database
    user = User.objects.filter(is_superuser=True).first()
    
    if user:
        user.set_password('YourNewSecretPasswordHere!')  # <-- Keep the quotes and put your password here
        user.save()
        print(f"PASSWORD RESET SUCCESSFUL! Your username is: {user.username}")
    else:
        print("No superuser account found in the database.")
except Exception as e:
    print("Password reset error:", e)
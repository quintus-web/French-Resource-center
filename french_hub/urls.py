from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView  # <--- Make sure this line is present
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Redirect root '/' straight to circulation desk
    path('', RedirectView.as_view(url='/lending/dashboard/', permanent=False)),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('lending/', include('lending.urls')),
    path('resources/', include('resources.urls')),
    path('club/', include('club.urls')),
]

# Serve media files during local development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
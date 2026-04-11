from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import frontend

urlpatterns = [
    path('', frontend, name='frontend'),
    # API endpoints
    path('api/auth/', include('accounts.urls')),
    path('api/doctors/', include('doctors.urls')),
    path('api/appointments/', include('appointments.urls')),
    path('api/leaves/', include('leaves.urls')),
    # Superadmin dashboard (template-based)
    path('superadmin/', include('accounts.superadmin_urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

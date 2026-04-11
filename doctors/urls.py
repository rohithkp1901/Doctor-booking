from django.urls import path
from .views import DoctorListView, DoctorDetailView, DoctorSlotsView

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor-list'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),
    path('<int:pk>/slots/', DoctorSlotsView.as_view(), name='doctor-slots'),
]

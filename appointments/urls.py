from django.urls import path
from .views import (
    BookAppointmentView,
    CustomerAppointmentListView,
    CustomerAppointmentDetailView,
    DoctorAppointmentListView,
)

urlpatterns = [
    path('book/', BookAppointmentView.as_view(), name='appointment-book'),
    path('my/', CustomerAppointmentListView.as_view(), name='customer-appointments'),
    path('my/<int:pk>/', CustomerAppointmentDetailView.as_view(), name='customer-appointment-detail'),
    path('doctor/', DoctorAppointmentListView.as_view(), name='doctor-appointments'),
]

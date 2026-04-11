from django.urls import path
from .superadmin_views import (
    SuperAdminLoginView, SuperAdminLogoutView, DashboardView,
    DoctorListView, DoctorCreateView, DoctorUpdateView, DoctorDeleteView,
    DoctorSlotsView, LeaveRequestListView, LeaveRequestActionView,
)

app_name = 'superadmin'

urlpatterns = [
    path('login/', SuperAdminLoginView.as_view(), name='login'),
    path('logout/', SuperAdminLogoutView.as_view(), name='logout'),
    path('', DashboardView.as_view(), name='dashboard'),
    path('doctors/', DoctorListView.as_view(), name='doctor_list'),
    path('doctors/create/', DoctorCreateView.as_view(), name='doctor_create'),
    path('doctors/<int:pk>/update/', DoctorUpdateView.as_view(), name='doctor_update'),
    path('doctors/<int:pk>/delete/', DoctorDeleteView.as_view(), name='doctor_delete'),
    path('doctors/<int:pk>/slots/', DoctorSlotsView.as_view(), name='doctor_slots'),
    path('leaves/', LeaveRequestListView.as_view(), name='leave_list'),
    path('leaves/<int:pk>/action/', LeaveRequestActionView.as_view(), name='leave_action'),
]

from django.urls import path
from .views import LeaveRequestListCreateView, LeaveRequestDetailView

urlpatterns = [
    path('', LeaveRequestListCreateView.as_view(), name='leave-list-create'),
    path('<int:pk>/', LeaveRequestDetailView.as_view(), name='leave-detail'),
]

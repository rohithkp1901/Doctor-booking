from datetime import date as date_type, datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Doctor
from .serializers import DoctorListSerializer, DoctorDetailSerializer
from .utils import generate_slots_for_doctor


class DoctorListView(APIView):
    """List all active doctors. Public endpoint."""
    permission_classes = [AllowAny]

    def get(self, request):
        doctors = Doctor.objects.filter(is_active=True).select_related('user').prefetch_related('availabilities')
        serializer = DoctorListSerializer(doctors, many=True)
        return Response({
            'success': True,
            'data': serializer.data,
            'count': doctors.count(),
        })


class DoctorDetailView(APIView):
    """Get a single doctor's details."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
        serializer = DoctorDetailSerializer(doctor)
        return Response({'success': True, 'data': serializer.data})


class DoctorSlotsView(APIView):
    """Get available slots for a doctor on a specific date."""
    permission_classes = [AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk, is_active=True)
        date_str = request.query_params.get('date')

        if not date_str:
            return Response({
                'success': False,
                'message': 'date query parameter is required (YYYY-MM-DD).'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD.'
            }, status=status.HTTP_400_BAD_REQUEST)

        if target_date < date_type.today():
            return Response({
                'success': False,
                'message': 'Cannot view slots for past dates.'
            }, status=status.HTTP_400_BAD_REQUEST)

        slots = generate_slots_for_doctor(doctor, target_date)

        return Response({
            'success': True,
            'data': {
                'doctor_id': doctor.id,
                'doctor_name': f"Dr. {doctor.user.get_full_name()}",
                'date': date_str,
                'slots': slots,
                'available_count': sum(1 for s in slots if s['is_available']),
            }
        })

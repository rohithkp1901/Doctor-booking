from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction, IntegrityError
from django.db.models import Q

from accounts.permissions import IsCustomer, IsDoctor
from .models import Appointment
from .serializers import AppointmentBookSerializer, AppointmentSerializer


class BookAppointmentView(APIView):
    """Customer: book an appointment."""
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = AppointmentBookSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        doctor = data['doctor']
        appointment_date = data['appointment_date']
        start_time = data['start_time']
        end_time = data['end_time']

        try:
            with transaction.atomic():
                # Lock existing appointments for this doctor/date/time to prevent race conditions
                existing = Appointment.objects.select_for_update().filter(
                    doctor=doctor,
                    appointment_date=appointment_date,
                    start_time=start_time,
                    status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
                )

                if existing.exists():
                    return Response({
                        'success': False,
                        'message': 'This slot was just booked. Please choose another time.',
                    }, status=status.HTTP_409_CONFLICT)

                appointment = Appointment.objects.create(
                    customer=request.user,
                    doctor=doctor,
                    appointment_date=appointment_date,
                    start_time=start_time,
                    end_time=end_time,
                    status=Appointment.Status.CONFIRMED,
                    notes=data.get('notes', ''),
                )

        except IntegrityError:
            return Response({
                'success': False,
                'message': 'This slot was just booked. Please choose another time.',
            }, status=status.HTTP_409_CONFLICT)

        return Response({
            'success': True,
            'message': 'Appointment booked successfully.',
            'data': AppointmentSerializer(appointment).data,
        }, status=status.HTTP_201_CREATED)


class CustomerAppointmentListView(APIView):
    """Customer: list own appointments."""
    permission_classes = [IsCustomer]

    def get(self, request):
        appointments = Appointment.objects.filter(
            customer=request.user
        ).select_related('doctor__user')
        status_filter = request.query_params.get('status')
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({'success': True, 'data': serializer.data})


class CustomerAppointmentDetailView(APIView):
    """Customer: view or cancel a single appointment."""
    permission_classes = [IsCustomer]

    def get(self, request, pk):
        appt = get_object_or_404(Appointment, pk=pk, customer=request.user)
        return Response({'success': True, 'data': AppointmentSerializer(appt).data})

    def patch(self, request, pk):
        """Cancel appointment."""
        appt = get_object_or_404(Appointment, pk=pk, customer=request.user)
        if appt.status not in [Appointment.Status.PENDING, Appointment.Status.CONFIRMED]:
            return Response({
                'success': False,
                'message': 'This appointment cannot be cancelled.',
            }, status=status.HTTP_400_BAD_REQUEST)
        appt.status = Appointment.Status.CANCELLED
        appt.save()
        return Response({'success': True, 'message': 'Appointment cancelled.', 'data': AppointmentSerializer(appt).data})


class DoctorAppointmentListView(APIView):
    """Doctor: view own appointments."""
    permission_classes = [IsDoctor]

    def get(self, request):
        appointments = Appointment.objects.filter(
            doctor=request.user.doctor_profile
        ).select_related('customer')
        date_filter = request.query_params.get('date')
        status_filter = request.query_params.get('status')
        if date_filter:
            appointments = appointments.filter(appointment_date=date_filter)
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response({'success': True, 'data': serializer.data})

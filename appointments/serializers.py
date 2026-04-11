from rest_framework import serializers
from datetime import date, datetime, time
from .models import Appointment
from doctors.models import Doctor


class AppointmentBookSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    appointment_date = serializers.DateField()
    start_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M', '%H:%M:%S'])
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_appointment_date(self, value):
        if value < date.today():
            raise serializers.ValidationError('Appointment date cannot be in the past.')
        return value

    def validate(self, data):
        from doctors.utils import generate_slots_for_doctor
        from leaves.models import LeaveRequest

        try:
            doctor = Doctor.objects.get(pk=data['doctor_id'], is_active=True)
        except Doctor.DoesNotExist:
            raise serializers.ValidationError({'doctor_id': 'Doctor not found or inactive.'})

        target_date = data['appointment_date']
        start_time = data['start_time']

        # Check if doctor is on leave
        on_leave = LeaveRequest.objects.filter(
            doctor=doctor,
            status=LeaveRequest.Status.APPROVED,
            start_date__lte=target_date,
            end_date__gte=target_date,
        ).exists()
        if on_leave:
            raise serializers.ValidationError('Doctor is on approved leave on this date.')

        # Generate valid slots and verify the requested slot exists
        slots = generate_slots_for_doctor(doctor, target_date)
        if not slots:
            raise serializers.ValidationError('Doctor has no availability on this date.')

        valid_slot = None
        for slot in slots:
            slot_time = datetime.strptime(slot['start_time'], '%H:%M').time()
            if slot_time == start_time:
                valid_slot = slot
                break

        if valid_slot is None:
            raise serializers.ValidationError({'start_time': 'This time slot is not valid for this doctor.'})

        if not valid_slot['is_available']:
            if valid_slot['is_booked']:
                raise serializers.ValidationError({'start_time': 'This slot is already booked.'})
            if valid_slot['is_past']:
                raise serializers.ValidationError({'start_time': 'This slot has already passed.'})

        data['doctor'] = doctor
        data['end_time'] = datetime.strptime(valid_slot['end_time'], '%H:%M').time()
        return data


class AppointmentSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.get_full_name', read_only=True)
    customer_email = serializers.EmailField(source='customer.email', read_only=True)
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'customer_name', 'customer_email',
            'doctor_name', 'doctor_specialization',
            'appointment_date', 'start_time', 'end_time',
            'status', 'status_display', 'notes', 'created_at',
        ]

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name()}"

from rest_framework import serializers
from datetime import date
from .models import LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'doctor', 'doctor_name', 'start_date', 'end_date',
            'reason', 'status', 'status_display', 'admin_reason',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['doctor', 'status', 'admin_reason']


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']

    def validate(self, data):
        if data['start_date'] < date.today():
            raise serializers.ValidationError({'start_date': 'Leave start date cannot be in the past.'})
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError({'end_date': 'End date must be on or after start date.'})
        return data

    def validate_start_date(self, value):
        request = self.context['request']
        doctor = request.user.doctor_profile
        # Check for overlapping approved/pending leaves
        overlapping = LeaveRequest.objects.filter(
            doctor=doctor,
            status__in=[LeaveRequest.Status.PENDING, LeaveRequest.Status.APPROVED],
            start_date__lte=self.initial_data.get('end_date', value),
            end_date__gte=value,
        )
        if overlapping.exists():
            raise serializers.ValidationError('A leave request already exists for this date range.')
        return value

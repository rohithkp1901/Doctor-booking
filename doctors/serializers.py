from rest_framework import serializers
from .models import Doctor, DoctorAvailability


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    weekday_display = serializers.CharField(source='get_weekday_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'weekday', 'weekday_display', 'start_time', 'end_time', 'slot_duration', 'is_active']


class DoctorListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Doctor
        fields = [
            'id', 'full_name', 'email', 'specialization', 'qualification',
            'experience_years', 'consultation_fee', 'bio', 'phone',
            'is_active', 'availabilities',
        ]


class DoctorDetailSerializer(DoctorListSerializer):
    pass

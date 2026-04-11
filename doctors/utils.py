from datetime import datetime, timedelta, date, time
from typing import List, Dict


def generate_slots_for_doctor(doctor, target_date: date) -> List[Dict]:
    """
    Dynamically generate available time slots for a doctor on a given date.
    Slots are NOT stored in the database — generated on the fly.
    Excludes slots during approved leaves and already-booked slots.
    """
    from leaves.models import LeaveRequest
    from appointments.models import Appointment

    weekday = target_date.weekday()  # 0=Monday, 6=Sunday

    # Check if doctor has availability for this weekday
    try:
        availability = doctor.availabilities.get(weekday=weekday, is_active=True)
    except doctor.availabilities.model.DoesNotExist:
        return []

    # Check if doctor is on approved leave for this date
    on_leave = LeaveRequest.objects.filter(
        doctor=doctor,
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=target_date,
        end_date__gte=target_date,
    ).exists()

    if on_leave:
        return []

    # Get already booked slot times for this doctor on this date
    booked_slots = set(
        Appointment.objects.filter(
            doctor=doctor,
            appointment_date=target_date,
            status__in=['confirmed', 'pending'],
        ).values_list('start_time', flat=True)
    )

    # Generate all slots
    slots = []
    current_time = datetime.combine(target_date, availability.start_time)
    end_time = datetime.combine(target_date, availability.end_time)
    slot_delta = timedelta(minutes=availability.slot_duration)

    now = datetime.now()

    while current_time + slot_delta <= end_time:
        slot_start = current_time.time()
        slot_end = (current_time + slot_delta).time()
        is_booked = slot_start in booked_slots
        is_past = (target_date == date.today() and current_time <= now)

        slots.append({
            'start_time': slot_start.strftime('%H:%M'),
            'end_time': slot_end.strftime('%H:%M'),
            'is_available': not is_booked and not is_past,
            'is_booked': is_booked,
            'is_past': is_past,
        })
        current_time += slot_delta

    return slots

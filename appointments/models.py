from django.db import models
from accounts.models import User
from doctors.models import Doctor


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-appointment_date', '-start_time']
        # Prevent duplicate bookings at the DB level
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'start_time'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_doctor_slot_booking',
            )
        ]

    def __str__(self):
        return (
            f"{self.customer.get_full_name()} with Dr. {self.doctor.user.get_full_name()} "
            f"on {self.appointment_date} at {self.start_time}"
        )

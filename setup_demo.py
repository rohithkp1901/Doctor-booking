#!/usr/bin/env python
"""
Quick setup script — run after migrations to create superadmin + demo data.
Usage:  python setup_demo.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_booking.settings')
django.setup()

from accounts.models import User
from doctors.models import Doctor, DoctorAvailability
from datetime import time

print("=== Doctor Booking System — Demo Setup ===\n")

# ── Superadmin ───────────────────────────────────────────────────────────────
if not User.objects.filter(email='admin@yopmail.com').exists():
    admin = User.objects.create_superuser(
        email='admin@yopmail.com',
        password='admin123',
        first_name='Super',
        last_name='Admin',
    )
    print(f"✅ Superadmin created: admin@yopmail.com / admin123")
else:
    print("ℹ️  Superadmin already exists.")

# ── Sample Doctors ───────────────────────────────────────────────────────────
doctors_data = [
    {
        'email': 'dr.sharma@yopmail.com',
        'first_name': 'Rohit', 'last_name': 'Sharma',
        'specialization': 'Cardiologist',
        'qualification': 'MBBS, MD (Cardiology)',
        'experience_years': 12,
        'consultation_fee': 800,
        'bio': 'Specialist in interventional cardiology with 12 years of experience.',
        'phone': '+91 98765 43210',
        'weekdays': [0, 1, 2, 3, 4],  # Mon–Fri
        'start_time': time(9, 0), 'end_time': time(17, 0), 'slot_duration': 30,
    },
    {
        'email': 'dr.dhoni@yopmail.com',
        'first_name': 'Mahendra Singh', 'last_name': 'Dhoni',
        'specialization': 'Orthopedic Surgeon',
        'qualification': 'MBBS, MS (Ortho)',
        'experience_years': 8,
        'consultation_fee': 600,
        'bio': 'Expert in joint replacement and sports injury management.',
        'phone': '+91 87654 32109',
        'weekdays': [0, 2, 4],  # Mon, Wed, Fri
        'start_time': time(10, 0), 'end_time': time(16, 0), 'slot_duration': 45,
    },
    {
        'email': 'dr.patel@yopmail.com',
        'first_name': 'Axar', 'last_name': 'Patel',
        'specialization': 'Dermatologist',
        'qualification': 'MBBS, DVD',
        'experience_years': 5,
        'consultation_fee': 500,
        'bio': 'Skin care specialist focusing on medical and cosmetic dermatology.',
        'phone': '+91 76543 21098',
        'weekdays': [1, 3, 5],  # Tue, Thu, Sat
        'start_time': time(9, 0), 'end_time': time(14, 0), 'slot_duration': 20,
    },
]

for d_data in doctors_data:
    if User.objects.filter(email=d_data['email']).exists():
        print(f"ℹ️  Doctor {d_data['email']} already exists.")
        continue

    user = User.objects.create_user(
        email=d_data['email'],
        password='doctor123',
        first_name=d_data['first_name'],
        last_name=d_data['last_name'],
        role=User.Role.DOCTOR,
    )
    doctor = Doctor.objects.create(
        user=user,
        specialization=d_data['specialization'],
        qualification=d_data['qualification'],
        experience_years=d_data['experience_years'],
        consultation_fee=d_data['consultation_fee'],
        bio=d_data['bio'],
        phone=d_data['phone'],
    )
    for day in d_data['weekdays']:
        DoctorAvailability.objects.create(
            doctor=doctor,
            weekday=day,
            start_time=d_data['start_time'],
            end_time=d_data['end_time'],
            slot_duration=d_data['slot_duration'],
        )
    print(f"✅ Doctor created: Dr. {user.get_full_name()} ({d_data['email']} / doctor123)")

# ── Sample Customer ──────────────────────────────────────────────────────────
if not User.objects.filter(email='patient@yopmail.com').exists():
    User.objects.create_user(
        email='patient@yopmail.com',
        password='patient123',
        first_name='Arjun',
        last_name='Kumar',
        role=User.Role.CUSTOMER,
    )
    print(f"✅ Customer created: patient@yopmail.com / patient123")
else:
    print("ℹ️  Sample customer already exists.")

print("\n=== Setup complete! ===")
print("\nURLs:")
print("  Frontend (Customer/Doctor portal): http://127.0.0.1:8000/")
print("  Superadmin Dashboard:              http://127.0.0.1:8000/superadmin/")
print("\nTest Credentials:")
print("  Superadmin : admin@yopmail.com     / admin123")
print("  Doctor 1   : dr.sharma@yopmail.com / doctor123")
print("  Doctor 2   : dr.dhoni@yopmail.com  / doctor123")
print("  Doctor 3   : dr.patel@yopmail.com  / doctor123")
print("  Customer   : patient@yopmail.com   / patient123")

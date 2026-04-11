from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db import transaction
from django.contrib.auth import authenticate

from accounts.models import User
from doctors.models import Doctor, DoctorAvailability
from leaves.models import LeaveRequest
from appointments.models import Appointment


def superadmin_required(view_func):
    """Decorator to require superadmin session."""
    def wrapper(request, *args, **kwargs):
        if not request.session.get('superadmin_id'):
            return redirect('superadmin:login')
        try:
            user = User.objects.get(id=request.session['superadmin_id'], role=User.Role.SUPERADMIN)
            request.superadmin = user
        except User.DoesNotExist:
            request.session.flush()
            return redirect('superadmin:login')
        return view_func(request, *args, **kwargs)
    return wrapper


class SuperAdminLoginView(View):
    template_name = 'superadmin/login.html'

    def get(self, request):
        if request.session.get('superadmin_id'):
            return redirect('superadmin:dashboard')
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user and user.is_superadmin:
            request.session['superadmin_id'] = user.id
            return redirect('superadmin:dashboard')
        messages.error(request, 'Invalid credentials or insufficient permissions.')
        return render(request, self.template_name, {'email': email})


class SuperAdminLogoutView(View):
    def post(self, request):
        request.session.flush()
        return redirect('superadmin:login')


@method_decorator(superadmin_required, name='dispatch')
class DashboardView(View):
    template_name = 'superadmin/dashboard.html'

    def get(self, request):
        context = {
            'superadmin': request.superadmin,
            'total_doctors': Doctor.objects.count(),
            'total_customers': User.objects.filter(role=User.Role.CUSTOMER).count(),
            'total_appointments': Appointment.objects.count(),
            'pending_leaves': LeaveRequest.objects.filter(status=LeaveRequest.Status.PENDING).count(),
            'recent_appointments': Appointment.objects.select_related(
                'customer', 'doctor__user'
            ).order_by('-created_at')[:5],
            'pending_leave_requests': LeaveRequest.objects.filter(
                status=LeaveRequest.Status.PENDING
            ).select_related('doctor__user').order_by('-created_at')[:5],
        }
        return render(request, self.template_name, context)


@method_decorator(superadmin_required, name='dispatch')
class DoctorListView(View):
    template_name = 'superadmin/doctors/list.html'

    def get(self, request):
        doctors = Doctor.objects.select_related('user').all()
        return render(request, self.template_name, {
            'doctors': doctors,
            'superadmin': request.superadmin,
        })


@method_decorator(superadmin_required, name='dispatch')
class DoctorCreateView(View):
    template_name = 'superadmin/doctors/form.html'

    def get(self, request):
        return render(request, self.template_name, {
            'superadmin': request.superadmin,
            'action': 'Create',
            'weekdays': DoctorAvailability.Weekday.choices,
        })

    def post(self, request):
        try:
            with transaction.atomic():
                # Create user account
                user = User.objects.create_user(
                    email=request.POST['email'],
                    password=request.POST['password'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    role=User.Role.DOCTOR,
                )
                # Create doctor profile
                doctor = Doctor.objects.create(
                    user=user,
                    specialization=request.POST['specialization'],
                    qualification=request.POST['qualification'],
                    experience_years=int(request.POST.get('experience_years', 0)),
                    consultation_fee=request.POST.get('consultation_fee', 0),
                    bio=request.POST.get('bio', ''),
                    phone=request.POST.get('phone', ''),
                )
                # Create availability
                weekdays = request.POST.getlist('weekdays')
                start_time = request.POST.get('start_time', '09:00')
                end_time = request.POST.get('end_time', '17:00')
                slot_duration = int(request.POST.get('slot_duration', 30))
                for day in weekdays:
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        weekday=int(day),
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration=slot_duration,
                    )
                messages.success(request, f'Doctor {user.get_full_name()} created successfully.')
                return redirect('superadmin:doctor_list')
        except Exception as e:
            messages.error(request, f'Error creating doctor: {str(e)}')
            return render(request, self.template_name, {
                'superadmin': request.superadmin,
                'action': 'Create',
                'weekdays': DoctorAvailability.Weekday.choices,
                'form_data': request.POST,
            })


@method_decorator(superadmin_required, name='dispatch')
class DoctorUpdateView(View):
    template_name = 'superadmin/doctors/form.html'

    def get(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        availability = doctor.availabilities.all()
        return render(request, self.template_name, {
            'superadmin': request.superadmin,
            'doctor': doctor,
            'availability': availability,
            'action': 'Update',
            'weekdays': DoctorAvailability.Weekday.choices,
        })

    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        try:
            with transaction.atomic():
                doctor.user.first_name = request.POST['first_name']
                doctor.user.last_name = request.POST['last_name']
                doctor.user.save()
                doctor.specialization = request.POST['specialization']
                doctor.qualification = request.POST['qualification']
                doctor.experience_years = int(request.POST.get('experience_years', 0))
                doctor.consultation_fee = request.POST.get('consultation_fee', 0)
                doctor.bio = request.POST.get('bio', '')
                doctor.phone = request.POST.get('phone', '')
                doctor.save()
                # Update availability
                doctor.availabilities.all().delete()
                weekdays = request.POST.getlist('weekdays')
                start_time = request.POST.get('start_time', '09:00')
                end_time = request.POST.get('end_time', '17:00')
                slot_duration = int(request.POST.get('slot_duration', 30))
                for day in weekdays:
                    DoctorAvailability.objects.create(
                        doctor=doctor,
                        weekday=int(day),
                        start_time=start_time,
                        end_time=end_time,
                        slot_duration=slot_duration,
                    )
                messages.success(request, 'Doctor updated successfully.')
                return redirect('superadmin:doctor_list')
        except Exception as e:
            messages.error(request, f'Error updating doctor: {str(e)}')
            return redirect('superadmin:doctor_update', pk=pk)


@method_decorator(superadmin_required, name='dispatch')
class DoctorDeleteView(View):
    def post(self, request, pk):
        doctor = get_object_or_404(Doctor, pk=pk)
        doctor.user.delete()
        messages.success(request, 'Doctor deleted successfully.')
        return redirect('superadmin:doctor_list')


@method_decorator(superadmin_required, name='dispatch')
class DoctorSlotsView(View):
    template_name = 'superadmin/doctors/slots.html'

    def get(self, request, pk):
        from datetime import date, timedelta
        doctor = get_object_or_404(Doctor, pk=pk)
        selected_date_str = request.GET.get('date', str(date.today()))
        try:
            from datetime import datetime
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = date.today()

        from doctors.utils import generate_slots_for_doctor
        slots = generate_slots_for_doctor(doctor, selected_date)

        return render(request, self.template_name, {
            'superadmin': request.superadmin,
            'doctor': doctor,
            'slots': slots,
            'selected_date': selected_date,
        })


@method_decorator(superadmin_required, name='dispatch')
class LeaveRequestListView(View):
    template_name = 'superadmin/leaves/list.html'

    def get(self, request):
        status_filter = request.GET.get('status', 'pending')
        leave_requests = LeaveRequest.objects.select_related('doctor__user').order_by('-created_at')
        if status_filter != 'all':
            leave_requests = leave_requests.filter(status=status_filter)
        return render(request, self.template_name, {
            'superadmin': request.superadmin,
            'leave_requests': leave_requests,
            'status_filter': status_filter,
        })


@method_decorator(superadmin_required, name='dispatch')
class LeaveRequestActionView(View):
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        if action == 'approve':
            leave.status = LeaveRequest.Status.APPROVED
            leave.admin_reason = reason
            leave.save()
            messages.success(request, 'Leave request approved.')
        elif action == 'reject':
            leave.status = LeaveRequest.Status.REJECTED
            leave.admin_reason = reason
            leave.save()
            messages.success(request, 'Leave request rejected.')
        return redirect('superadmin:leave_list')

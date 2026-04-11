# 🏥 Doctor Booking System

A full-stack Doctor Booking System built with **Django + Django REST Framework** for the backend and a **vanilla JS SPA** for the frontend. Includes a custom Superadmin dashboard built with Django templates (no Django Admin).

\---

## 📋 Features

### Roles

|Role|Interface|Key Capabilities|
|-|-|-|
|**Superadmin**|Template-based dashboard (`/superadmin/`)|Create/Update/Delete doctors, Approve/Reject leaves, View slots (read-only)|
|**Doctor**|REST API + Frontend SPA|Create/view leave requests, View own appointments|
|**Customer**|REST API + Frontend SPA|List doctors, View available slots, Book appointments, Cancel bookings|

### Core Functionality

* **JWT Authentication** — Access + Refresh tokens with rotation and blacklisting
* **Dynamic Slot Generation** — Slots generated on-the-fly per doctor per date; **NOT stored in DB**
* **Concurrency Safety** — `select\_for\_update()` + DB-level `UniqueConstraint` prevents double-booking
* **Leave Management** — Approved leaves automatically block all slots for that date range
* **Class-Based Views** — All views use CBVs (APIView for API, View for templates)

\---

## 🚀 Setup Instructions

### 1\. Clone and create virtual environment

```bash
git clone <your-repo-url>
cd doctor\_booking
python -m venv venv
source venv/bin/activate      # Windows: venv\\Scripts\\activate
```

### 2\. Install dependencies

```bash
pip install -r requirements.txt
```

### 3\. Run migrations

```bash
python manage.py migrate
```

### 4\. Seed demo data (optional but recommended)

```bash
python setup\_demo.py
```

### 5\. Start the development server

```bash
python manage.py runserver
```

### 6\. Open in browser

* **Frontend Portal**: http://127.0.0.1:8000/
* **Superadmin Dashboard**: http://127.0.0.1:8000/superadmin/

\---

## 🔐 Demo Credentials

|Role|Email|Password|
|-|-|-|
|Superadmin|admin@yopmail.com|admin123|
|Doctor 1|dr.sharma@yopmail.com|doctor123|
|Doctor 2|dr.dhoni@yopmail.com|doctor123|
|Doctor 3|dr.patel@yopmail.com|doctor123|
|Customer|patient@yopmail.com|patient123|

\---

## 📡 API Endpoints

### Authentication

|Method|URL|Description|Auth|
|-|-|-|-|
|POST|`/api/auth/register/`|Register as customer|Public|
|POST|`/api/auth/login/`|Login (returns JWT)|Public|
|POST|`/api/auth/logout/`|Logout (blacklists refresh)|Required|
|POST|`/api/auth/token/refresh/`|Refresh access token|Public|
|GET|`/api/auth/profile/`|Get current user info|Required|

### Doctors (Public)

|Method|URL|Description|Auth|
|-|-|-|-|
|GET|`/api/doctors/`|List all active doctors|Public|
|GET|`/api/doctors/<id>/`|Get doctor details|Public|
|GET|`/api/doctors/<id>/slots/?date=YYYY-MM-DD`|Get available slots|Public|

### Appointments

|Method|URL|Description|Auth|
|-|-|-|-|
|POST|`/api/appointments/book/`|Book an appointment|Customer|
|GET|`/api/appointments/my/`|List own appointments|Customer|
|GET|`/api/appointments/my/<id>/`|Get appointment detail|Customer|
|PATCH|`/api/appointments/my/<id>/`|Cancel appointment|Customer|
|GET|`/api/appointments/doctor/`|List doctor's appointments|Doctor|

### Leave Requests

|Method|URL|Description|Auth|
|-|-|-|-|
|GET|`/api/leaves/`|List own leave requests|Doctor|
|POST|`/api/leaves/`|Create leave request|Doctor|
|GET|`/api/leaves/<id>/`|Get leave detail|Doctor|
|DELETE|`/api/leaves/<id>/`|Cancel pending leave|Doctor|

### Superadmin Dashboard (Template URLs)

|URL|Description|
|-|-|
|`/superadmin/`|Dashboard|
|`/superadmin/doctors/`|Doctor list|
|`/superadmin/doctors/create/`|Create doctor|
|`/superadmin/doctors/<id>/update/`|Edit doctor|
|`/superadmin/doctors/<id>/delete/`|Delete doctor|
|`/superadmin/doctors/<id>/slots/`|View doctor slots|
|`/superadmin/leaves/`|Leave requests|
|`/superadmin/leaves/<id>/action/`|Approve/Reject leave|

\---

## 🏗️ Project Structure

```
doctor\_booking/
├── doctor\_booking/         # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── views.py            # Serves frontend SPA
│   ├── wsgi.py
│   └── exceptions.py       # Custom exception handler
│
├── accounts/               # Custom User model + Auth
│   ├── models.py           # User (superadmin/doctor/customer)
│   ├── serializers.py
│   ├── views.py            # Register, Login, Logout, Profile
│   ├── permissions.py      # IsSuperAdmin, IsDoctor, IsCustomer
│   ├── superadmin\_views.py # Template-based dashboard views
│   ├── urls.py
│   └── superadmin\_urls.py
│
├── doctors/                # Doctor profiles + availability
│   ├── models.py           # Doctor, DoctorAvailability
│   ├── serializers.py
│   ├── views.py            # List, Detail, Slots API
│   ├── utils.py            # generate\_slots\_for\_doctor()
│   └── urls.py
│
├── appointments/           # Booking system
│   ├── models.py           # Appointment (with UniqueConstraint)
│   ├── serializers.py      # Validation + booking logic
│   ├── views.py            # Book, List, Cancel (with select\_for\_update)
│   └── urls.py
│
├── leaves/                 # Leave management
│   ├── models.py           # LeaveRequest
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── templates/
│   ├── index.html          # Frontend SPA (Customer + Doctor portal)
│   └── superadmin/
│       ├── base.html       # Sidebar layout
│       ├── login.html
│       ├── dashboard.html
│       ├── doctors/
│       │   ├── list.html
│       │   ├── form.html   # Create \& Update
│       │   └── slots.html
│       └── leaves/
│           └── list.html
│
├── setup\_demo.py           # Seed script
├── manage.py
└── requirements.txt
```

\---

## ⚙️ Key Technical Decisions

### Concurrency Handling

Double booking is prevented at two levels:

1. **Application level** — `select\_for\_update()` acquires a row-level DB lock before checking slot availability
2. **Database level** — `UniqueConstraint` on `(doctor, appointment\_date, start\_time)` filtered by active statuses

### Slot Generation

Slots are generated dynamically in `doctors/utils.py:generate\_slots\_for\_doctor()`. The algorithm:

1. Fetches the doctor's `DoctorAvailability` for the requested weekday
2. Checks for approved `LeaveRequest` on that date — returns empty list if on leave
3. Queries `Appointment` table for booked slots on that date
4. Iterates from `start\_time` to `end\_time` in `slot\_duration` increments
5. Marks each slot as `available`, `booked`, or `past`

### No Django Admin

The Superadmin interface is a fully custom dashboard using Django template views with session-based authentication, styled with a dark medical theme.


# Healthcare Backend API

A clean, beginner-friendly Healthcare Backend REST API built with **Python**, **Django**, **Django REST Framework (DRF)**, **PostgreSQL**, and **JWT Authentication** (`djangorestframework-simplejwt`).

This project was built for the **WhatBytes Full-stack Developer Internship Assignment**.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [API Endpoints Summary](#api-endpoints-summary)
5. [Prerequisites](#prerequisites)
6. [Setup & Installation Guide (Windows PowerShell)](#setup--installation-guide-windows-powershell)
   - [Step 1: Clone or Open Project Folder](#step-1-open-project-folder)
   - [Step 2: Create and Activate Virtual Environment](#step-2-create-and-activate-virtual-environment)
   - [Step 3: Install Dependencies](#step-3-install-dependencies)
   - [Step 4: Configure PostgreSQL Database](#step-4-configure-postgresql-database)
   - [Step 5: Configure Environment Variables (.env)](#step-5-configure-environment-variables-env)
   - [Step 6: Run Migrations](#step-6-run-migrations)
   - [Step 7: Run Automated Tests](#step-7-run-automated-tests)
   - [Step 8: Start Development Server](#step-8-start-development-server)
7. [API Documentation & Testing with Postman](#api-documentation--testing-with-postman)
8. [Common Errors and Solutions](#common-errors-and-solutions)
9. [Architecture & Design Decisions](#architecture--design-decisions)

---

## Project Overview

The Healthcare Backend API allows authenticated medical clinic staff and admins to:
- **Register & Log In**: Secure email-based authentication with JSON Web Tokens (JWT).
- **Manage Patients**: Create, view, update, and delete patients. Each user can **only** access and manage patients they personally created.
- **Manage Doctors**: Create, view, update, and delete doctors with their specialization, contact details, and availability.
- **Assign Doctors to Patients**: Map doctors to patients owned by the logged-in user, prevent duplicate assignments, and view assigned doctors.

---

## Technologies Used

- **Python 3.11+**
- **Django 5.x** — High-level Python web framework.
- **Django REST Framework (DRF)** — Toolkit for building robust REST APIs.
- **PostgreSQL** — Production-grade relational database.
- **psycopg2-binary** — PostgreSQL database adapter for Python.
- **djangorestframework-simplejwt** — JSON Web Token (JWT) authentication.
- **python-dotenv** — Reads environment variables from `.env`.
- **Postman** — API testing and documentation.

---

## Project Structure

```text
Healtcare/
│
├── manage.py                              # Django command-line runner
│
├── config/                                # Main project configuration package
│   ├── __init__.py
│   ├── settings.py                       # Project settings (DB, JWT, Apps, Middleware)
│   ├── urls.py                           # Root URL routing (includes /api/)
│   └── wsgi.py                           # WSGI server entrypoint
│
├── api/                                   # Core healthcare application
│   ├── __init__.py
│   ├── admin.py                          # Django Admin registrations
│   ├── apps.py                           # App configuration
│   ├── models.py                         # User, Patient, Doctor, PatientDoctor models
│   ├── serializers.py                    # DRF serializers (input validation & JSON formatting)
│   ├── views.py                          # API views (Auth, Patients, Doctors, Mappings)
│   ├── urls.py                           # API route definitions
│   ├── tests.py                          # Comprehensive test suite (30 unit & integration tests)
│   └── migrations/                       # Database migration files
│       ├── __init__.py
│       └── 0001_initial.py
│
├── requirements.txt                       # Project dependencies
├── .env.example                           # Example environment variable template
├── .env                                   # Secret environment configuration (git-ignored)
├── .gitignore                             # Files excluded from git
├── healthcare_api_postman_collection.json # Direct importable Postman test collection
└── README.md                              # This complete documentation
```

---

## API Endpoints Summary

| Module | Method | Endpoint | Description | Auth Required? |
|---|---|---|---|---|
| **Auth** | `POST` | `/api/auth/register/` | Register new user (name, email, password) | No |
| **Auth** | `POST` | `/api/auth/login/` | Log in and obtain JWT access & refresh tokens | No |
| **Patients** | `POST` | `/api/patients/` | Create a patient (`created_by` set automatically) | **Yes** (Bearer Token) |
| **Patients** | `GET` | `/api/patients/` | List only patients created by logged-in user | **Yes** (Bearer Token) |
| **Patients** | `GET` | `/api/patients/<id>/` | Retrieve specific patient owned by logged-in user | **Yes** (Bearer Token) |
| **Patients** | `PUT` | `/api/patients/<id>/` | Update specific patient owned by logged-in user | **Yes** (Bearer Token) |
| **Patients** | `DELETE`| `/api/patients/<id>/` | Delete specific patient owned by logged-in user | **Yes** (Bearer Token) |
| **Doctors** | `POST` | `/api/doctors/` | Create a new doctor | **Yes** (Bearer Token) |
| **Doctors** | `GET` | `/api/doctors/` | List all doctors | **Yes** (Bearer Token) |
| **Doctors** | `GET` | `/api/doctors/<id>/` | Retrieve doctor details | **Yes** (Bearer Token) |
| **Doctors** | `PUT` | `/api/doctors/<id>/` | Update doctor details | **Yes** (Bearer Token) |
| **Doctors** | `DELETE`| `/api/doctors/<id>/` | Delete a doctor record | **Yes** (Bearer Token) |
| **Mappings**| `POST` | `/api/mappings/` | Assign a doctor to user's patient | **Yes** (Bearer Token) |
| **Mappings**| `GET` | `/api/mappings/` | List mappings for all patients owned by user | **Yes** (Bearer Token) |
| **Mappings**| `GET` | `/api/mappings/<patient_id>/` | List all doctors assigned to a particular patient | **Yes** (Bearer Token) |
| **Mappings**| `DELETE`| `/api/mappings/<id>/` | Remove doctor assignment by mapping ID | **Yes** (Bearer Token) |

---

## Prerequisites

Make sure the following are installed on your Windows system:
1. **Python 3.10+** (verify in PowerShell: `python --version`)
2. **PostgreSQL 14+** (with pgAdmin or `psql` command-line tool)
3. **Postman** (for API testing)

---

## Setup & Installation Guide (Windows PowerShell)

Open **Windows PowerShell** in the project directory:

### Step 1: Open Project Folder
```powershell
cd "c:\Users\acer\Desktop\WhatBytes Assignment\Healtcare"
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment named 'venv'
python -m venv venv

# Activate virtual environment in PowerShell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell shows an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and then run the activate command again).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL Database

1. Open your PostgreSQL command line (`SQL Shell (psql)`) or **pgAdmin 4**.
2. Run the SQL commands below to create the database:
```sql
CREATE DATABASE healthcare_db;
```
3. Ensure your default `postgres` user password matches what you put in `.env`.

### Step 5: Configure Environment Variables (.env)

Copy `.env.example` to `.env` (or update `.env` directly):
```powershell
Copy-Item .env.example .env
```

Open `.env` and verify your credentials:
```ini
# Django Security Settings
SECRET_KEY=django-insecure-healthcare-backend-dev-key-739281!@#$
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=healthcare_db
DB_USER=postgres
DB_PASSWORD=your_actual_postgres_password
DB_HOST=localhost
DB_PORT=5432
```

> **Note on Offline / Testing Mode**:
> If you haven't set up PostgreSQL yet and want to test immediately, you can temporarily change `DB_ENGINE=django.db.backends.sqlite3` in `.env`. Once PostgreSQL is set up, set it back to `DB_ENGINE=django.db.backends.postgresql`.

### Step 6: Run Migrations
Apply migrations to create all database tables:
```powershell
python manage.py migrate
```

### Step 7: Run Automated Tests
Execute the 30 automated unit and integration tests directly against PostgreSQL:
```powershell
python manage.py test api
```
Expected output:
```text
Creating test database for alias 'default'...
..............................
----------------------------------------------------------------------
Ran 30 tests in 25.953s

OK
Destroying test database for alias 'default'...
```

### Step 8: Start Development Server
```powershell
python manage.py runserver
```
The server will start at: `http://127.0.0.1:8000/`

---

## API Documentation & Testing with Postman

### Direct Postman Import (Recommended)

1. Open **Postman**.
2. Click **Import** in the top-left corner.
3. Select the file: `healthcare_api_postman_collection.json` located in the root of this project.
4. The collection is already pre-configured with:
   - Base URL variable: `http://127.0.0.1:8000`
   - Automatic JWT token extraction on Login (saves `access_token` into collection variables).
   - Bearer token authentication configured on all protected endpoints.

---

### Step-by-Step API Testing Walkthrough

#### 1. Register a User
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/auth/register/`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "name": "Alice Smith",
  "email": "alice@example.com",
  "password": "password123"
}
```
- **Response** (`201 Created`):
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com"
  }
}
```

#### 2. Log In & Obtain JWT Tokens
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/auth/login/`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "email": "alice@example.com",
  "password": "password123"
}
```
- **Response** (`200 OK`):
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsIn...",
  "access": "eyJhbGciOiJIUzI1NiIsIn...",
  "user": {
    "id": 1,
    "name": "Alice Smith",
    "email": "alice@example.com"
  }
}
```

#### 3. How to Authenticate Requests in Postman
For all subsequent requests, pass the JWT access token in the headers:
- **Authorization**: `Bearer <your_access_token>`
*(In Postman, select the **Auth** tab -> Type **Bearer Token** -> paste the token).*

#### 4. Create a Patient
- **Method**: `POST`
- **URL**: `http://127.0.0.1:8000/api/patients/`
- **Headers**:
  - `Authorization: Bearer <access_token>`
  - `Content-Type: application/json`
- **Request Body**:
```json
{
  "name": "Charlie Brown",
  "age": 32,
  "gender": "Male",
  "address": "123 Maple Street, Springfield",
  "phone": "+1-555-0199"
}
```
- **Response** (`201 Created`):
```json
{
  "id": 1,
  "name": "Charlie Brown",
  "age": 32,
  "gender": "Male",
  "address": "123 Maple Street, Springfield",
  "phone": "+1-555-0199",
  "created_by": "alice@example.com",
  "created_at": "2026-10-23T18:30:00Z"
}
```

#### 5. List Only My Patients
- **Method**: `GET`
- **URL**: `http://127.0.0.1:8000/api/patients/`
- **Headers**: `Authorization: Bearer <access_token>`
- **Response** (`200 OK`):
```json
[
  {
    "id": 1,
    "name": "Charlie Brown",
    "age": 32,
    "gender": "Male",
    "address": "123 Maple Street, Springfield",
    "phone": "+1-555-0199",
    "created_by": "alice@example.com",
    "created_at": "2026-10-23T18:30:00Z"
  }
]
```

#### 6. Retrieve, Update, and Delete a Patient
- **GET** `http://127.0.0.1:8000/api/patients/1/` — Returns patient 1.
- **PUT** `http://127.0.0.1:8000/api/patients/1/` — Updates patient 1.
- **DELETE** `http://127.0.0.1:8000/api/patients/1/` — Deletes patient 1.
*(If another user attempts to retrieve, update, or delete Patient 1, the API returns `404 Not Found`, completely isolating records).*

#### 7. Doctor Management
- **POST** `http://127.0.0.1:8000/api/doctors/` — Create doctor:
```json
{
  "name": "Gregory House",
  "specialization": "Diagnostic Medicine",
  "email": "house@hospital.org",
  "phone": "+1-555-0144",
  "available_days": "Monday, Wednesday, Friday"
}
```
- **GET** `http://127.0.0.1:8000/api/doctors/` — List all doctors.
- **GET** `http://127.0.0.1:8000/api/doctors/1/` — Retrieve doctor 1.
- **PUT** `http://127.0.0.1:8000/api/doctors/1/` — Update doctor 1.
- **DELETE** `http://127.0.0.1:8000/api/doctors/1/` — Delete doctor 1.

#### 8. Patient-Doctor Mapping
- **Assign Doctor**: `POST http://127.0.0.1:8000/api/mappings/`
```json
{
  "patient": 1,
  "doctor": 1
}
```
- **List All Mappings for My Patients**: `GET http://127.0.0.1:8000/api/mappings/`
- **List Doctors for a Particular Patient**: `GET http://127.0.0.1:8000/api/mappings/1/`
*(Where `1` is the patient ID)*
- **Remove Doctor Assignment**: `DELETE http://127.0.0.1:8000/api/mappings/1/`
*(Where `1` is the mapping ID)*

---

## Common Errors and Solutions

1. **`Connection refused (0x0000274D/10061)` when running `migrate`**
   - **Cause**: PostgreSQL service is not running on your computer, or credentials in `.env` are incorrect.
   - **Fix**: Open Windows Services (`services.msc`), check that the `postgresql-x64-XX` service is running. If not installed yet, you can test with `DB_ENGINE=django.db.backends.sqlite3` in `.env`.

2. **`401 Unauthorized: Authentication credentials were not provided.`**
   - **Cause**: You forgot to include the JWT access token in the request header.
   - **Fix**: In Postman, go to the **Authorization** tab, select **Bearer Token**, and paste the token from the login response.

3. **`400 Bad Request: {"email": ["A user with this email already exists."]}`**
   - **Cause**: Attempting to register with an email that is already in the database.
   - **Fix**: Use a new email address or log in using your existing credentials.

4. **`404 Not Found` when accessing patient or mapping**
   - **Cause**: Either the record doesn't exist, or it was created by another user.
   - **Security Reason**: The system ensures users cannot see or modify other users' patients.

---

## Architecture & Design Decisions

1. **Custom User Model**:
   - Uses `AbstractBaseUser` + `PermissionsMixin` with `USERNAME_FIELD = 'email'`.
   - Simplifies authentication: users register and log in with email and password without needing a redundant `username` field.

2. **DRF Generic Views (`ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`)**:
   - Clean, standard, and easy to explain during interviews.
   - Security is implemented by overriding `get_queryset()`:
     ```python
     def get_queryset(self):
         return Patient.objects.filter(created_by=self.request.user)
     ```
   - Automatically scopes database queries to the current logged-in user.

3. **Unique Database Constraints**:
   - In `PatientDoctor`, `unique_together = ('patient', 'doctor')` ensures that even under concurrent requests, duplicate assignments cannot occur.

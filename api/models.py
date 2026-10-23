"""Database models for Healthcare Backend API."""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    """
    Custom user manager to handle creating users and superusers using email
    as the primary identifier instead of a username.
    """
    def create_user(self, email, name, password=None):
        """Create and return a regular user with email, name, and hashed password."""
        if not email:
            raise ValueError('Email address is required')
        if not name:
            raise ValueError('Name is required')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        # set_password hashes the password before saving
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """Create and return a superuser with staff and admin permissions."""
        user = self.create_user(email=email, name=name, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email for authentication.
    Stores name, email, active status, staff status, and registration timestamp.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    # Use email instead of username for login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email})"


class Patient(models.Model):
    """
    Patient model representing patient records in the healthcare system.
    Each patient is created by and belongs to a specific user.
    """
    name = models.CharField(max_length=255)
    age = models.IntegerField()
    gender = models.CharField(max_length=20)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    # Link patient to the user who registered them
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Age: {self.age})"


class Doctor(models.Model):
    """
    Doctor model representing doctors in the healthcare system.
    """
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    available_days = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="e.g. Monday, Wednesday, Friday"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"


class PatientDoctor(models.Model):
    """
    Patient-Doctor mapping model representing the assignment of a doctor to a patient.
    Enforces a unique constraint so the same doctor cannot be assigned multiple times to the same patient.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='doctor_mappings'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='patient_mappings'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent assigning the same doctor to the same patient more than once
        unique_together = ('patient', 'doctor')

    def __str__(self):
        return f"{self.patient.name} -> Dr. {self.doctor.name}"

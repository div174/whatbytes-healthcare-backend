"""Django admin registration for Healthcare models."""

from django.contrib import admin
from .models import User, Patient, Doctor, PatientDoctor


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_staff', 'is_active', 'created_at')
    search_fields = ('name', 'email')
    ordering = ('id',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'age', 'gender', 'phone', 'created_by', 'created_at')
    list_filter = ('gender', 'created_at')
    search_fields = ('name', 'phone', 'created_by__email')
    ordering = ('-created_at',)


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'specialization', 'email', 'phone', 'available_days', 'created_at')
    list_filter = ('specialization', 'created_at')
    search_fields = ('name', 'email', 'specialization')
    ordering = ('id',)


@admin.register(PatientDoctor)
class PatientDoctorAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'doctor', 'assigned_at')
    search_fields = ('patient__name', 'doctor__name')
    ordering = ('-assigned_at',)

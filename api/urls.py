"""URL mappings for api app."""

from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    PatientListCreateView,
    PatientDetailView,
    DoctorListCreateView,
    DoctorDetailView,
    MappingListCreateView,
    MappingDetailView,
)

urlpatterns = [
    # ---------------------------------------------------------
    # A. User Authentication Endpoints
    # ---------------------------------------------------------
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),

    # ---------------------------------------------------------
    # B. Patient Management Endpoints
    # ---------------------------------------------------------
    path('patients/', PatientListCreateView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    # ---------------------------------------------------------
    # C. Doctor Management Endpoints
    # ---------------------------------------------------------
    path('doctors/', DoctorListCreateView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', DoctorDetailView.as_view(), name='doctor-detail'),

    # ---------------------------------------------------------
    # D. Patient-Doctor Mapping Endpoints
    # ---------------------------------------------------------
    # POST /api/mappings/       -> Assign a doctor to a patient
    # GET  /api/mappings/       -> List all mappings for logged-in user's patients
    path('mappings/', MappingListCreateView.as_view(), name='mapping-list-create'),

    # GET    /api/mappings/<patient_id>/ -> List all doctors assigned to a patient
    # DELETE /api/mappings/<id>/         -> Remove a doctor assignment
    path('mappings/<int:pk>/', MappingDetailView.as_view(), name='mapping-detail'),
]

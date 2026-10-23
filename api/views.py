"""Views for Healthcare Backend API."""

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import User, Patient, Doctor, PatientDoctor
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PatientSerializer,
    DoctorSerializer,
    PatientDoctorSerializer
)


# ==============================================================================
# A. USER AUTHENTICATION VIEWS
# ==============================================================================

class RegisterView(APIView):
    """
    POST /api/auth/register/
    Registers a new user with name, email, and password.
    Publicly accessible (does not require authentication).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    "message": "User registered successfully.",
                    "user": {
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    }
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticates user using email and password.
    Returns JWT access and refresh tokens.
    Publicly accessible (does not require authentication).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# B. PATIENT MANAGEMENT VIEWS
# ==============================================================================

class PatientListCreateView(generics.ListCreateAPIView):
    """
    GET /api/patients/  — List all patients created by the logged-in user.
    POST /api/patients/ — Create a new patient record.
    Requires JWT authentication.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Crucial security check: return ONLY patients created by the logged-in user
        return Patient.objects.filter(created_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # Automatically assign the logged-in user as the creator
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/    — Retrieve a specific patient owned by logged-in user.
    PUT /api/patients/<id>/    — Update that patient's information.
    DELETE /api/patients/<id>/ — Delete that patient's record.
    Requires JWT authentication.
    """
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Crucial security check: only allow operations on patients created by the logged-in user.
        # If another user's patient ID is requested, DRF returns 404 Not Found.
        return Patient.objects.filter(created_by=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Patient record deleted successfully."},
            status=status.HTTP_200_OK
        )


# ==============================================================================
# C. DOCTOR MANAGEMENT VIEWS
# ==============================================================================

class DoctorListCreateView(generics.ListCreateAPIView):
    """
    GET /api/doctors/  — List all doctors.
    POST /api/doctors/ — Create a new doctor.
    Requires JWT authentication.
    """
    queryset = Doctor.objects.all().order_by('id')
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/    — Retrieve a specific doctor.
    PUT /api/doctors/<id>/    — Update a doctor.
    DELETE /api/doctors/<id>/ — Delete a doctor.
    Requires JWT authentication.
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Doctor record deleted successfully."},
            status=status.HTTP_200_OK
        )


# ==============================================================================
# D. PATIENT-DOCTOR MAPPING VIEWS
# ==============================================================================

class MappingListCreateView(APIView):
    """
    POST /api/mappings/ — Assign a doctor to a patient.
    GET /api/mappings/  — List mappings for all patients owned by the logged-in user.
    Requires JWT authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Only return mappings for patients created by the logged-in user
        mappings = PatientDoctor.objects.filter(patient__created_by=request.user).order_by('-assigned_at')
        serializer = PatientDoctorSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PatientDoctorSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MappingDetailView(APIView):
    """
    Handles operations with an ID parameter:
    - GET /api/mappings/<patient_id>/ — List all doctors assigned to a particular patient.
    - DELETE /api/mappings/<id>/      — Remove a specific doctor assignment.
    Requires JWT authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        List all doctors assigned to a particular patient (<patient_id>).
        Ensures the patient exists and belongs to the logged-in user.
        """
        try:
            patient = Patient.objects.get(id=pk, created_by=request.user)
        except Patient.DoesNotExist:
            return Response(
                {"detail": "Patient not found or you do not have permission to view their mappings."},
                status=status.HTTP_404_NOT_FOUND
            )

        mappings = PatientDoctor.objects.filter(patient=patient).order_by('-assigned_at')
        serializer = PatientDoctorSerializer(mappings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """
        Remove a doctor assignment by mapping ID (<id>).
        Ensures the mapping exists and belongs to a patient owned by the logged-in user.
        """
        try:
            mapping = PatientDoctor.objects.get(id=pk, patient__created_by=request.user)
        except PatientDoctor.DoesNotExist:
            return Response(
                {"detail": "Mapping not found or you do not have permission to delete it."},
                status=status.HTTP_404_NOT_FOUND
            )

        mapping.delete()
        return Response(
            {"message": "Doctor assignment removed successfully."},
            status=status.HTTP_200_OK
        )

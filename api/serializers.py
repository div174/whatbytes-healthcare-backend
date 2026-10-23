"""Serializers for Healthcare Backend API."""

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Patient, Doctor, PatientDoctor


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer to handle user registration.
    Validates name, email, and password. Stores password securely using create_user.
    """
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text="Password must be at least 6 characters long."
    )

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_email(self, value):
        """Ensure email is unique across all users."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        """Create and return a new user with hashed password."""
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password']
        )


class LoginSerializer(serializers.Serializer):
    """
    Serializer to handle user login with email and password.
    Returns JWT access and refresh tokens upon successful authentication.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').lower()
        password = attrs.get('password', '')

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        # Authenticate user using Django's authenticate function
        # Since our custom user model has USERNAME_FIELD = 'email', we pass email as username
        user = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password
        )

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("User account is inactive.")

        # Generate JWT tokens using Simple JWT
        refresh = RefreshToken.for_user(user)

        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }


class PatientSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient CRUD operations.
    created_by is read-only and automatically set to the logged-in user in the view.
    """
    created_by = serializers.ReadOnlyField(source='created_by.email')

    class Meta:
        model = Patient
        fields = [
            'id',
            'name',
            'age',
            'gender',
            'address',
            'phone',
            'created_by',
            'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def validate_name(self, value):
        """Ensure patient name is not blank."""
        if not value or not value.strip():
            raise serializers.ValidationError("Patient name cannot be blank.")
        return value.strip()

    def validate_age(self, value):
        """Validate that patient age is a positive integer."""
        if value <= 0 or value > 130:
            raise serializers.ValidationError("Please provide a valid age between 1 and 130.")
        return value

    def validate_phone(self, value):
        """Ensure phone number is provided."""
        if not value or not value.strip():
            raise serializers.ValidationError("Phone number cannot be blank.")
        return value.strip()


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor CRUD operations.
    """
    class Meta:
        model = Doctor
        fields = [
            'id',
            'name',
            'specialization',
            'email',
            'phone',
            'available_days',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """Ensure doctor name is not blank."""
        if not value or not value.strip():
            raise serializers.ValidationError("Doctor name cannot be blank.")
        return value.strip()

    def validate_email(self, value):
        """Ensure doctor email is unique."""
        # For updates, exclude current doctor instance
        doctor_id = self.instance.id if self.instance else None
        if Doctor.objects.filter(email__iexact=value).exclude(id=doctor_id).exists():
            raise serializers.ValidationError("A doctor with this email already exists.")
        return value.lower()


class PatientDoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient-Doctor mapping operations.
    Provides nested/read-only info for responses while accepting patient and doctor IDs for input.
    """
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        error_messages={'does_not_exist': 'Patient with this ID does not exist.'}
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        error_messages={'does_not_exist': 'Doctor with this ID does not exist.'}
    )
    patient_name = serializers.ReadOnlyField(source='patient.name')
    doctor_name = serializers.ReadOnlyField(source='doctor.name')
    doctor_specialization = serializers.ReadOnlyField(source='doctor.specialization')
    doctor_email = serializers.ReadOnlyField(source='doctor.email')
    doctor_phone = serializers.ReadOnlyField(source='doctor.phone')

    class Meta:
        model = PatientDoctor
        fields = [
            'id',
            'patient',
            'patient_name',
            'doctor',
            'doctor_name',
            'doctor_specialization',
            'doctor_email',
            'doctor_phone',
            'assigned_at'
        ]
        read_only_fields = ['id', 'assigned_at']

    def validate(self, attrs):
        """
        Validate:
        1. The patient belongs to the logged-in user.
        2. The doctor is not already assigned to this patient.
        """
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # Ensure patient belongs to the currently authenticated user
        if patient and request and patient.created_by != request.user:
            raise serializers.ValidationError({
                "patient": "You can only assign doctors to your own patient records."
            })

        # Ensure no duplicate mapping exists
        if patient and doctor and PatientDoctor.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                "non_field_errors": ["This doctor is already assigned to this patient."]
            })

        return attrs

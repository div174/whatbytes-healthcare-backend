"""Unit and Integration tests for Healthcare Backend API."""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import User, Patient, Doctor, PatientDoctor


class HealthcareAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create two test users to verify security & data isolation
        self.user1 = User.objects.create_user(
            email='alice@example.com',
            name='Alice Smith',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            email='bob@example.com',
            name='Bob Jones',
            password='password123'
        )

        # Pre-create a doctor
        self.doctor1 = Doctor.objects.create(
            name='Dr. Gregory House',
            specialization='Diagnostic Medicine',
            email='house@ppth.org',
            phone='555-0101',
            available_days='Monday, Tuesday'
        )
        self.doctor2 = Doctor.objects.create(
            name='Dr. Allison Cameron',
            specialization='Immunology',
            email='cameron@ppth.org',
            phone='555-0102',
            available_days='Wednesday, Friday'
        )

        # Pre-create patients for user1 and user2
        self.patient1 = Patient.objects.create(
            name='Charlie Brown',
            age=30,
            gender='Male',
            address='123 Maple St',
            phone='555-1111',
            created_by=self.user1
        )
        self.patient2 = Patient.objects.create(
            name='Dana Scully',
            age=35,
            gender='Female',
            address='456 Oak Ave',
            phone='555-2222',
            created_by=self.user2
        )

    # ---------------------------------------------------------
    # A. User Authentication Tests
    # ---------------------------------------------------------

    def test_user_registration_success(self):
        """Test registering a new user with valid details."""
        url = reverse('auth-register')
        data = {
            'name': 'Eve Adams',
            'email': 'eve@example.com',
            'password': 'securepassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'eve@example.com')
        self.assertTrue(User.objects.filter(email='eve@example.com').exists())

    def test_user_registration_duplicate_email(self):
        """Test registration fails when email is already registered."""
        url = reverse('auth-register')
        data = {
            'name': 'Duplicate Alice',
            'email': 'alice@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_user_registration_missing_fields(self):
        """Test registration fails when required fields are missing."""
        url = reverse('auth-register')
        data = {'email': 'incomplete@example.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login_success(self):
        """Test login with valid email and password returns JWT tokens."""
        url = reverse('auth-login')
        data = {
            'email': 'alice@example.com',
            'password': 'password123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['email'], 'alice@example.com')

    def test_user_login_invalid_password(self):
        """Test login fails with incorrect password."""
        url = reverse('auth-login')
        data = {
            'email': 'alice@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ---------------------------------------------------------
    # B. Patient Management Tests
    # ---------------------------------------------------------

    def test_patients_unauthenticated_denied(self):
        """Test that unauthenticated requests to patient endpoints are rejected."""
        url = reverse('patient-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_patient(self):
        """Test creating a patient sets created_by to logged-in user."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('patient-list-create')
        data = {
            'name': 'George Clark',
            'age': 45,
            'gender': 'Male',
            'address': '789 Pine Rd',
            'phone': '555-3333'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'George Clark')
        self.assertEqual(response.data['created_by'], self.user1.email)

    def test_list_patients_only_shows_owned_records(self):
        """Test that user1 only sees patient1 and NOT patient2."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('patient-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patient_ids = [p['id'] for p in response.data]
        self.assertIn(self.patient1.id, patient_ids)
        self.assertNotIn(self.patient2.id, patient_ids)

    def test_retrieve_patient_isolation(self):
        """Test user1 can retrieve own patient but gets 404 for user2's patient."""
        self.client.force_authenticate(user=self.user1)

        # Retrieve own patient -> 200 OK
        url_own = reverse('patient-detail', kwargs={'pk': self.patient1.id})
        res_own = self.client.get(url_own)
        self.assertEqual(res_own.status_code, status.HTTP_200_OK)

        # Retrieve other user's patient -> 404 Not Found
        url_other = reverse('patient-detail', kwargs={'pk': self.patient2.id})
        res_other = self.client.get(url_other)
        self.assertEqual(res_other.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_patient(self):
        """Test updating own patient succeeds; updating another user's patient fails."""
        self.client.force_authenticate(user=self.user1)

        # Update own patient
        url = reverse('patient-detail', kwargs={'pk': self.patient1.id})
        data = {
            'name': 'Charlie Brown Updated',
            'age': 31,
            'gender': 'Male',
            'address': '123 New Address',
            'phone': '555-1111'
        }
        res = self.client.put(url, data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['name'], 'Charlie Brown Updated')

        # Attempt to update user2's patient -> 404 Not Found
        url_other = reverse('patient-detail', kwargs={'pk': self.patient2.id})
        res_other = self.client.put(url_other, data, format='json')
        self.assertEqual(res_other.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_patient(self):
        """Test deleting own patient succeeds; deleting another user's patient fails."""
        self.client.force_authenticate(user=self.user1)

        # Attempt to delete user2's patient -> 404 Not Found
        url_other = reverse('patient-detail', kwargs={'pk': self.patient2.id})
        res_other = self.client.delete(url_other)
        self.assertEqual(res_other.status_code, status.HTTP_404_NOT_FOUND)

        # Delete own patient -> 200 OK
        url_own = reverse('patient-detail', kwargs={'pk': self.patient1.id})
        res_own = self.client.delete(url_own)
        self.assertEqual(res_own.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=self.patient1.id).exists())

    # ---------------------------------------------------------
    # C. Doctor Management Tests
    # ---------------------------------------------------------

    def test_doctors_unauthenticated_denied(self):
        """Test that unauthenticated requests to doctor endpoints are rejected."""
        url = reverse('doctor-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_and_list_doctors(self):
        """Test creating and listing doctors when authenticated."""
        self.client.force_authenticate(user=self.user1)

        # Create doctor
        url = reverse('doctor-list-create')
        data = {
            'name': 'Dr. Eric Foreman',
            'specialization': 'Neurology',
            'email': 'foreman@ppth.org',
            'phone': '555-0103',
            'available_days': 'Tuesday, Thursday'
        }
        res_create = self.client.post(url, data, format='json')
        self.assertEqual(res_create.status_code, status.HTTP_201_CREATED)

        # List doctors
        res_list = self.client.get(url)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res_list.data), 3)

    def test_retrieve_update_delete_doctor(self):
        """Test retrieve, update, and delete for doctor."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('doctor-detail', kwargs={'pk': self.doctor1.id})

        # Retrieve
        res_get = self.client.get(url)
        self.assertEqual(res_get.status_code, status.HTTP_200_OK)
        self.assertEqual(res_get.data['name'], 'Dr. Gregory House')

        # Update
        update_data = {
            'name': 'Dr. Gregory House, M.D.',
            'specialization': 'Diagnostic Medicine & Nephrology',
            'email': 'house@ppth.org',
            'phone': '555-0101',
            'available_days': 'Monday'
        }
        res_put = self.client.put(url, update_data, format='json')
        self.assertEqual(res_put.status_code, status.HTTP_200_OK)
        self.assertEqual(res_put.data['name'], 'Dr. Gregory House, M.D.')

        # Delete
        res_del = self.client.delete(url)
        self.assertEqual(res_del.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=self.doctor1.id).exists())

    # ---------------------------------------------------------
    # D. Patient-Doctor Mapping Tests
    # ---------------------------------------------------------

    def test_mapping_unauthenticated_denied(self):
        """Test that unauthenticated requests to mapping endpoints are rejected."""
        url = reverse('mapping-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_assign_doctor_to_own_patient(self):
        """Test assigning a doctor to a patient owned by user1."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-list-create')
        data = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient'], self.patient1.id)
        self.assertEqual(response.data['doctor'], self.doctor1.id)

    def test_assign_doctor_to_other_users_patient_denied(self):
        """Test user1 cannot assign a doctor to user2's patient."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-list-create')
        data = {
            'patient': self.patient2.id,  # Owned by user2
            'doctor': self.doctor1.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', response.data)

    def test_prevent_duplicate_mapping(self):
        """Test that assigning the same doctor to the same patient twice is prevented."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-list-create')
        data = {
            'patient': self.patient1.id,
            'doctor': self.doctor1.id
        }
        # First assignment succeeds
        res1 = self.client.post(url, data, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)

        # Second duplicate assignment fails
        res2 = self.client.post(url, data, format='json')
        self.assertEqual(res2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_mappings_for_logged_in_user(self):
        """Test listing mappings only returns mappings for logged-in user's patients."""
        # Create mapping for user1's patient and user2's patient
        PatientDoctor.objects.create(patient=self.patient1, doctor=self.doctor1)
        PatientDoctor.objects.create(patient=self.patient2, doctor=self.doctor2)

        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['patient'], self.patient1.id)

    def test_get_mappings_by_patient_id(self):
        """Test GET /api/mappings/<patient_id>/ returns all doctors assigned to that patient."""
        # Assign both doctors to patient1
        PatientDoctor.objects.create(patient=self.patient1, doctor=self.doctor1)
        PatientDoctor.objects.create(patient=self.patient1, doctor=self.doctor2)

        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-detail', kwargs={'pk': self.patient1.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_get_mappings_for_other_users_patient_denied(self):
        """Test user1 cannot view mappings for user2's patient."""
        PatientDoctor.objects.create(patient=self.patient2, doctor=self.doctor2)

        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-detail', kwargs={'pk': self.patient2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_mapping(self):
        """Test removing a doctor assignment."""
        mapping = PatientDoctor.objects.create(patient=self.patient1, doctor=self.doctor1)

        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-detail', kwargs={'pk': mapping.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctor.objects.filter(id=mapping.id).exists())

    def test_delete_other_users_mapping_denied(self):
        """Test user1 cannot delete a mapping belonging to user2's patient."""
        mapping = PatientDoctor.objects.create(patient=self.patient2, doctor=self.doctor2)

        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-detail', kwargs={'pk': mapping.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(PatientDoctor.objects.filter(id=mapping.id).exists())

    # ---------------------------------------------------------
    # E. Edge Cases, Password Hashing & Real JWT Bearer Header Tests
    # ---------------------------------------------------------

    def test_password_is_hashed_and_not_plaintext(self):
        """Test that user password in database is hashed using Django's hasher."""
        user = User.objects.get(email='alice@example.com')
        self.assertNotEqual(user.password, 'password123')
        self.assertTrue(user.password.startswith('pbkdf2_sha256$') or user.password.startswith('argon2'))
        self.assertTrue(user.check_password('password123'))

    def test_access_protected_endpoint_with_valid_jwt_header(self):
        """Test accessing protected endpoint using actual Authorization: Bearer <token> header."""
        # 1. Login to get token
        login_res = self.client.post(reverse('auth-login'), {
            'email': 'alice@example.com',
            'password': 'password123'
        }, format='json')
        access_token = login_res.data['access']

        # 2. Make request using raw Bearer header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        res = self.client.get(reverse('patient-list-create'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # 3. Clear credentials
        self.client.credentials()

    def test_patient_invalid_field_values(self):
        """Test patient creation fails with invalid age and blank name."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('patient-list-create')

        # Invalid age (negative or zero)
        res_age = self.client.post(url, {
            'name': 'Test Patient',
            'age': -5,
            'gender': 'Male',
            'address': 'Address',
            'phone': '1234567890'
        }, format='json')
        self.assertEqual(res_age.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', res_age.data)

        # Blank name
        res_name = self.client.post(url, {
            'name': '   ',
            'age': 25,
            'gender': 'Male',
            'address': 'Address',
            'phone': '1234567890'
        }, format='json')
        self.assertEqual(res_name.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', res_name.data)

    def test_patient_nonexistent_id_returns_404(self):
        """Test retrieving nonexistent patient ID returns 404."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('patient-detail', kwargs={'pk': 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_doctor_nonexistent_id_returns_404(self):
        """Test retrieving nonexistent doctor ID returns 404."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('doctor-detail', kwargs={'pk': 99999})
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_doctor_duplicate_email_fails(self):
        """Test creating doctor with duplicate email fails."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('doctor-list-create')
        res = self.client.post(url, {
            'name': 'Dr. Duplicate',
            'specialization': 'General',
            'email': self.doctor1.email,
            'phone': '555-9999'
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

    def test_mapping_nonexistent_patient_or_doctor_fails(self):
        """Test mapping fails with clear error if patient or doctor does not exist."""
        self.client.force_authenticate(user=self.user1)
        url = reverse('mapping-list-create')

        # Nonexistent patient
        res_p = self.client.post(url, {'patient': 99999, 'doctor': self.doctor1.id}, format='json')
        self.assertEqual(res_p.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('patient', res_p.data)

        # Nonexistent doctor
        res_d = self.client.post(url, {'patient': self.patient1.id, 'doctor': 99999}, format='json')
        self.assertEqual(res_d.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('doctor', res_d.data)


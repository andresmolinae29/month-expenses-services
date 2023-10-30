"""
Test for expensetype API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import ExpenseType

from expense.serializers import (
    ExpenseTypeSerializer,
    ExpenseTypeDetailSerializer,
)


EXPENSE_URL = reverse('expense:expensetype-list')


def detail_url(expensetype_id):
    """Create and return an expensetype detail URL"""
    return reverse('expense:expensetype-detail', args=[expensetype_id])


def create_expensetype(user, **params):
    """Create and return a sample expensetype"""
    defaults = {
        'name': 'food'
    }

    defaults.update(**params)

    expensetype = ExpenseType.objects.create(user=user, **defaults)

    return expensetype


class PublicExpenseTypeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""

        res = self.client.get(EXPENSE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def create_user(**params):
    """Creates and return a new user"""
    return get_user_model().objects.create_user(**params)


class PrivateExpenseTypeAPITest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email='example@example.com',
            password='test123'
            )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_expense_types(self):
        """Test retrieving a lot of expensetypes"""
        create_expensetype(user=self.user)
        create_expensetype(user=self.user)

        res = self.client.get(EXPENSE_URL)

        expensetypes = ExpenseType.objects.all().order_by('-id')
        serializer = ExpenseTypeSerializer(expensetypes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_expensetype_list_limited_to_user(self):
        """Test list of expenses is limited to authenticated user"""
        other_user = create_user(email='user2@example.com', password='pass123')
        create_expensetype(user=self.user)
        create_expensetype(user=other_user)

        res = self.client.get(EXPENSE_URL)

        expenses = ExpenseType.objects.filter(user=self.user)
        serializer = ExpenseTypeSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_expense_type_detail(self):
        """Test get expensetype detail"""
        expensetype = create_expensetype(user=self.user)

        url = detail_url(expensetype.id)
        res = self.client.get(url)

        serializer = ExpenseTypeDetailSerializer(expensetype)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_expense_type(self):
        """Test creating an expensetype"""
        payload = {
            'name': 'food'
        }
        res = self.client.post(EXPENSE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        expensetype = ExpenseType.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(expensetype, k), v)
        self.assertEqual(expensetype.user, self.user)

    def test_partial_update(self):
        """Test partial update of a expensetype"""
        original_name = 'food'
        expensetype = create_expensetype(
            user=self.user,
            name=original_name
        )

        payload = {'name': 'volleyball'}
        url = detail_url(expensetype.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expensetype.refresh_from_db()
        self.assertEqual(expensetype.name, payload.get('name'))
        self.assertEqual(expensetype.user, self.user)

    def test_full_update(self):
        """Test full update of a expensetype"""
        original_name = 'food'
        expensetype = create_expensetype(
            user=self.user,
            name=original_name
        )

        payload = {'name': 'volleyball'}
        url = detail_url(expensetype.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expensetype.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(expensetype, k), v)
        self.assertEqual(expensetype.user, self.user)

    def test_delete_expense_type(self):
        """Test deleting expensetype successful"""
        expensetype = create_expensetype(user=self.user)

        url = detail_url(expensetype.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            ExpenseType.objects.filter(id=expensetype.id).exists()
            )

    def test_delete_other_users_expense_error(self):
        """Test tring to delete another user expensetype"""
        other_user = create_user(email='user2@example.com', password='pass123')
        expensetype = create_expensetype(user=other_user)

        url = detail_url(expensetype.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(ExpenseType.objects.filter(id=expensetype.id).exists())

"""
Test for expense API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Expense

from expense.serializers import (
    ExpenseSerializer,
    ExpenseDetailSerializer,
)


EXPENSE_URL = reverse('expense:expense-list')


def detail_url(expense_id):
    """Create and return an expense detail URL"""
    return reverse('expense:expense-detail', args=[expense_id])


def create_expense(user, **params):
    """Create and return a sample expense"""
    defaults = {
        'name': 'food'
    }

    defaults.update(params)

    expense = Expense.objects.create(user=user, **defaults)
    return expense


class PublicExpenseAPITests(TestCase):
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


class PrivateExpenseAPITest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email='example@example.com',
            password='test123'
            )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_expenses(self):
        """Test retrieving a lot of expenses"""
        create_expense(user=self.user)
        create_expense(user=self.user)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.all().order_by('-id')
        serializer = ExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_expense_list_limited_to_user(self):
        """Test list of expenses is limited to authenticated user"""
        other_user = create_user(
            email='other@example.com',
            password='password123'
            )
        create_expense(user=other_user)
        create_expense(user=self.user)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.filter(user=self.user)
        serializer = ExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_expense_detail(self):
        """Test get expense detail"""
        expense = create_expense(user=self.user)

        url = detail_url(expense.id)
        res = self.client.get(url)

        serializer = ExpenseDetailSerializer(expense)
        self.assertEqual(res.data, serializer.data)

    def test_create_expense(self):
        """Test creating an expense"""
        payload = {
            'name': 'food'
        }
        res = self.client.post(EXPENSE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)

    def test_partial_update(self):
        """Test partial update of a expense"""
        original_name = 'food'
        expense = create_expense(
            user=self.user,
            name=original_name
        )

        payload = {'name': 'volleyball'}
        url = detail_url(expense.id)

        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.name, payload.get('name'))
        self.assertEqual(expense.user, self.user)

    def test_full_update(self):
        """Test full update of a expense"""
        original_name = 'food'
        expense = create_expense(
            user=self.user,
            name=original_name
        )

        payload = {'name': 'volleyball'}
        url = detail_url(expense.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the expense user results in an error"""
        new_user = create_user(email='user2@example.com', password='pass123')
        expense = create_expense(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(expense.id)
        self.client.patch(url, payload)

        expense.refresh_from_db()
        self.assertEqual(expense.user, self.user)

    def test_delete_expense(self):
        """Test deleting expense successful"""
        expense = create_expense(user=self.user)

        url = detail_url(expense.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Expense.objects.filter(id=expense.id).exists())

    def test_delete_expense_other_users_expense_error(self):
        """Test trying to delete another user expense"""
        new_user = create_user(email='user2@example.com', password='pass123')
        expense = create_expense(user=new_user)

        url = detail_url(expense.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Expense.objects.filter(id=expense.id).exists())

"""
Terst cases for Expenses API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Expense, ExpenseType

from expense.serializers import (
    ExpenseSerializer,
    ExpenseDetailSerializer
)

from datetime import datetime


EXPENSE_URL = reverse('expense:expense-list')


def detail_url(expense_id):
    """Create and return an expense detail url"""
    return reverse('expense:expense-detail', args=[expense_id])


def create_expense(user, expensetype, **params):
    """Create test expense"""

    defaults = {
        'amount': 1011.1,
        'effective_date': datetime.now().date()
    }

    defaults.update(**params)

    expense = Expense.objects.create(
        user=user,
        expensetype=expensetype,
        **defaults
    )

    return expense


class PublicExpenseAPITests(TestCase):
    """Test unathenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""

        res = self.client.get(EXPENSE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_expensetype(**params):
    """Create and return a new expensetype"""
    return ExpenseType.objects.create(**params)


class PrivateExpenseAPITest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:

        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='pass123'
        )
        self.client.force_authenticate(user=self.user)

        self.expensetype = create_expensetype(
            user=self.user,
            name='food'
        )

    def test_retrieve_expenses(self):
        """Test retrieving a lot of expenses"""
        create_expense(user=self.user, expensetype=self.expensetype)
        create_expense(user=self.user, expensetype=self.expensetype)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.all().order_by('-id')
        serializer = ExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_expense_limited_to_user(self):
        """Test list of expenses is limited to authenticated user"""
        other_user = create_user(
            email='other2@example.com',
            password='pass123'
        )

        create_expense(user=self.user, expensetype=self.expensetype)
        create_expense(user=other_user, expensetype=self.expensetype)

        res = self.client.get(EXPENSE_URL)

        expenses = Expense.objects.filter(user=self.user)
        serializer = ExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_expense_detail(self):
        """Test get expense detail"""

        expense = create_expense(user=self.user, expensetype=self.expensetype)

        url = detail_url(expense.id)
        res = self.client.get(url)

        serializer = ExpenseDetailSerializer(expense)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_expense(self):
        """Test create expense with API request"""
        payload = {
            'amount': 10001.1,
            'effective_date': datetime.now().date(),
            'expensetype': {
                'name': 'food'
                }
            }

        res = self.client.post(EXPENSE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        expense = Expense.objects.get(user=self.user)
        for k, v in payload.items():
            if isinstance(getattr(expense, k), ExpenseType):
                pass
            else:
                self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)

    def test_partial_update(self):
        """Test update partial an expense"""
        original_amount = 10000
        expense = create_expense(
            user=self.user,
            expensetype=self.expensetype,
            amount=original_amount
        )
        payload = {
            'amount': 1500
        }

        url = detail_url(expense.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        self.assertEqual(expense.amount, payload.get('amount'))
        self.assertEqual(expense.user, self.user)

    def test_full_update(self):
        """Test full expense update"""

        expense = create_expense(
            user=self.user,
            expensetype=self.expensetype,
        )

        payload = {
            'amount': 10001,
            'effective_date': datetime.now().date(),
            'expensetype': {
                'name': 'volleyball'
            }
        }

        url = detail_url(expense.id)
        res = self.client.put(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expense.refresh_from_db()
        for k, v in payload.items():
            if isinstance(getattr(expense, k), ExpenseType):
                pass
            else:
                self.assertEqual(getattr(expense, k), v)
        self.assertEqual(expense.user, self.user)

    def test_delete_expense(self):
        """Test deletes an expense"""

        expense = create_expense(
            user=self.user,
            expensetype=self.expensetype,
        )

        url = detail_url(expense.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Expense.objects.filter(id=expense.id).exists()
        )

    def test_delete_other_users_expense_error(self):
        """Test trying to delete another user expensetype"""
        other_user = create_user(
            email='other@example.com',
            password='pass123'
        )

        expense = create_expense(
            user=other_user,
            expensetype=self.expensetype
        )

        url = detail_url(expense.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Expense.objects.filter(id=expense.id).exists())

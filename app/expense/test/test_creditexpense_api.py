"""
Test cases for Credit Expenses API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import CreditExpense, ExpenseType, CreditCard

from expense.serializers import (
    CreditExpenseSerializer,
    CreditExpenseDetailSerializer
)

from datetime import datetime


CREDIT_EXPENSE_URL = reverse('expense:creditexpense-list')


def detail_url(expense_id):
    """Create and return an credit expense detail url"""
    return reverse('expense:creditexpense-detail', args=[expense_id])


def create_credit_expense(user, expensetype, **params):
    """Create test credit expense"""

    defaults = {
        'amount': 1011.1,
        'effective_date': datetime.now().date(),
        'cut_off_date': datetime.now().date(),
        'payment_date': datetime.now().date(),
    }

    defaults.update(**params)

    credit_expense = CreditExpense.objects.create(
        user=user,
        expensetype=expensetype,
        **defaults
    )

    return credit_expense


class PublicCreditExpenseAPITests(TestCase):
    """Test unathenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""

        res = self.client.get(CREDIT_EXPENSE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


def create_expensetype(**params):
    """Create and return a new expensetype"""
    return ExpenseType.objects.create(**params)


def create_creditcard(**params):
    """Create and return a new creditcard"""
    return CreditCard.objects.create(**params)


class PrivateCreditExpenseAPITest(TestCase):
    """Test authenticated API request"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email='example@examplce.com',
            password='test123'
        )

        self.client.force_authenticate(user=self.user)

        self.expense_type = create_expensetype(
            user=self.user,
            name='food'
        )

        self.creditcard = create_creditcard(
            user=self.user,
            name='rappi',
            cut_off_day=28,
            payment_due_day=12
        )

    def test_retrieve_credit_expenses(self):
        """Test to retrieving a lot of credit expenses"""
        create_credit_expense(
            user=self.user,
            expensetype=self.expense_type,
            creditcard=self.creditcard
        )

        create_credit_expense(
            user=self.user,
            expensetype=self.expense_type,
            creditcard=self.creditcard
        )

        res = self.client.get(CREDIT_EXPENSE_URL)

        expenses = CreditExpense.objects.all().order_by('-id')
        serializer = CreditExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_credit_expense_limited_to_user(self):
        """Test retrieving credit for user limited only to current user"""
        other_user = create_user(
            email='other2@example.com',
            password='pass123'
            )
        create_credit_expense(
            user=self.user,
            expensetype=self.expense_type,
            creditcard=self.creditcard
        )

        create_credit_expense(
            user=other_user,
            expensetype=self.expense_type,
            creditcard=self.creditcard
        )

        res = self.client.get(CREDIT_EXPENSE_URL)

        expenses = CreditExpense.objects.filter(user=self.user)
        serializer = CreditExpenseSerializer(expenses, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_credit_expense_type_detail(self):
        """Test to get credit expense with detail"""
        credit_expense = create_credit_expense(
            user=self.user,
            expensetype=self.expense_type,
            creditcard=self.creditcard
            )

        url = detail_url(credit_expense.id)
        res = self.client.get(url)

        serializer = CreditExpenseDetailSerializer(credit_expense)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

"""
Test for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

from datetime import datetime


class ModelTests(TestCase):
    """Test models"""

    def test_create_user_with_email_succesful(self):
        """Test creating a user with an email is succesful"""
        email = 'test@example.com'
        password = ' testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test1@Example.com', 'Test1@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_Without_email_raises_error(self):
        """Test that creating an user without email raises a ValueError"""

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_expense_type(self):
        """Testing creating a expense type is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        expensetype = models.ExpenseType.objects.create(
            user=user,
            name='Clothes'
        )

        self.assertEqual(str(expensetype), expensetype.name)

    def test_create_creditcard(self):
        """Testing creating a credit card is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )

        creditcard = models.CreditCard.objects.create(
            user=user,
            name='Cencosud',
            cut_off_day=15,
            payment_due_day=29
        )

        self.assertEqual(str(creditcard), creditcard.name)

    def test_create_expense(self):
        """Testing creating an expense is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        expensetype = models.ExpenseType.objects.create(
            user=user,
            name='food'
        )

        expense = models.Expense.objects.create(
            user=user,
            expensetype=expensetype,
            amount=10000,
            effective_date=datetime.now().date()
        )

        self.assertEqual(str(expense), str(expense.amount))

    def test_create_credit_expense(self):
        """Test creatin a credit expense is successful"""
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        expensetype = models.ExpenseType.objects.create(
            user=user,
            name='food'
        )

        creditcard = models.CreditCard.objects.create(
            user=user,
            name='Cencosud',
            cut_off_day=15,
            payment_due_day=29
        )

        credit_expense = models.CreditExpense.objects.create(
            user=user,
            expensetype=expensetype,
            creditcard=creditcard,
            amount=1000,
            effective_date=datetime.now().date(),
            cut_off_date=datetime.now().date(),
            payment_date=datetime.now().date()
        )

        self.assertEqual(str(credit_expense), str(credit_expense.amount))

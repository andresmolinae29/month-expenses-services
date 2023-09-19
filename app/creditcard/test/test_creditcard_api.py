"""
Terst cases for Credit Card API
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import CreditCard

from creditcard.serializers import (
    CreditCardSerializer,
)


CREDITCARD_URL = reverse('creditcard:creditcard-list')


def create_creditcard(user, **params):
    """Create test credit card"""
    defaults = {
        'name': 'Cencosud',
        'cut_off_day': 15,
        'payment_due_day': 28
    }

    defaults.update(**params)

    creditcard = CreditCard.objects.create(user=user, **defaults)

    return creditcard


class PublicCreditCardAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API"""

        res = self.client.get(CREDITCARD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PrivateCreditCardAPITest(TestCase):
    """Test authenticated API requests"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(
            email='example@example.com',
            password='test123'
            )
        self.client.force_authenticate(user=self.user)

    def test_retrieve_creditcards(self):
        """Test retrieving a lot of creditcards"""
        create_creditcard(user=self.user)
        create_creditcard(user=self.user)

        res = self.client.get(CREDITCARD_URL)

        creditcards = CreditCard.objects.all().order_by('-id')
        serializer = CreditCardSerializer(creditcards, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_creditcard_list_limited_to_user(self):
        """Test list of credit cards is limited to authenticated user"""
        other_user = create_user(email='user2@example.com', password='pass123')
        create_creditcard(user=other_user)
        create_creditcard(user=self.user)

        res = self.client.get(CREDITCARD_URL)

        creditcards = CreditCard.objects.filter(user=self.user)
        serializer = CreditCardSerializer(creditcards, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

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
    CreditCardDetailSerializer
)


CREDITCARD_URL = reverse('creditcard:creditcard-list')


def detail_url(creditcard_id):
    """Create and return an expense detail URL"""
    return reverse('creditcard:creditcard-detail', args=[creditcard_id])


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

    def test_get_credit_card_detail(self):
        """Test get the credit card detail"""
        creditcard = create_creditcard(user=self.user)

        url = detail_url(creditcard.id)
        res = self.client.get(url)

        serializer = CreditCardDetailSerializer(creditcard)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_creditcard(self):
        """Test to create a credit card with the endpoint"""
        payload = {
            'name': 'Cencosud',
            'cut_off_day': 15,
            'payment_due_day': 28
        }

        res = self.client.post(CREDITCARD_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        creditcard = CreditCard.objects.get(id=res.data.get('id'))
        for k, v in payload.items():
            self.assertEqual(getattr(creditcard, k), v)
        self.assertEqual(creditcard.user, self.user)

    def test_partial_update(self):
        """Test partial update for creditcard"""
        original_name = 'Cencosud'
        creditcard = create_creditcard(
            user=self.user,
            name=original_name
        )

        payload = {
            'name': 'Rappi'
        }
        url = detail_url(creditcard.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        creditcard.refresh_from_db()
        self.assertEqual(creditcard.name, payload.get('name'))
        self.assertEqual(creditcard.user, self.user)

    def test_full_update(self):
        """Test full update of a creditcard"""
        creditcard = create_creditcard(
            user=self.user,
        )

        payload = {
            'name': 'Rappi',
            'cut_off_day': 28,
            'payment_due_day': 10
        }

        url = detail_url(creditcard.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        creditcard.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(creditcard, k), v)
        self.assertEqual(creditcard.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the creditcard user results in an error"""
        new_user = create_user(email='user2@example.com', password='pass123')
        creditcard = create_creditcard(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(creditcard.id)
        self.client.patch(url, payload)

        creditcard.refresh_from_db()
        self.assertEqual(creditcard.user, self.user)

    def test_delete_creditcard(self):
        """Test deleting creditcard successful"""
        creditcard = create_creditcard(user=self.user)

        url = detail_url(creditcard.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CreditCard.objects.filter(id=creditcard.id).exists())

    def test_delete_expense_other_users_creditcard_error(self):
        """Test trying to delete another user creditcard"""
        new_user = create_user(email='user2@example.com', password='pass123')
        creditcard = create_creditcard(user=new_user)

        url = detail_url(creditcard.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(CreditCard.objects.filter(id=creditcard.id).exists())

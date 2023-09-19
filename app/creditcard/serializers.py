"""
Serializer for the credit card API view
"""
from rest_framework import serializers

from core.models import CreditCard


class CreditCardSerializer(serializers.ModelSerializer):
    """Serializer for credit card"""

    class Meta:
        model = CreditCard
        fields = ['id', 'name', 'cut_off_day', 'payment_due_day']
        read_only_fields = ['id']

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


class CreditCardDetailSerializer(CreditCardSerializer):
    """Serializer extended for credit card"""

    class Meta(CreditCardSerializer.Meta):
        fields = CreditCardSerializer.Meta.fields + \
            ['created_on', 'created_on']
        read_only_fields = CreditCardSerializer.Meta.read_only_fields + \
            ['created_on', 'created_on']

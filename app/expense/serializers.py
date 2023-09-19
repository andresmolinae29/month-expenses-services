"""
Serializers for the expense API view
"""
from rest_framework import serializers

from core.models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expense"""

    class Meta:
        model = Expense
        fields = ['id', 'name']
        read_only_fields = ['id']


class ExpenseDetailSerializer(ExpenseSerializer):
    """Serializer for detail expense"""

    class Meta(ExpenseSerializer.Meta):
        fields = ExpenseSerializer.Meta.fields + ['created_on', 'updated_on']

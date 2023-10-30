"""
Serializers for the expense API view
"""
from rest_framework import serializers

from datetime import datetime

from core.models import (
    ExpenseType,
    CreditCard,
    Expense,
    CreditExpense
)


class ExpenseTypeSerializer(serializers.ModelSerializer):
    """Serializer for expense"""

    class Meta:
        model = ExpenseType
        fields = ['id', 'name']
        read_only_fields = ['id']


class ExpenseTypeDetailSerializer(ExpenseTypeSerializer):
    """Serializer for detail expense"""

    class Meta(ExpenseTypeSerializer.Meta):
        fields = ExpenseTypeSerializer.Meta.fields + \
              ['created_on', 'updated_on']


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
            ['created_on', 'updated_on']
        read_only_fields = CreditCardSerializer.Meta.read_only_fields + \
            ['created_on', 'updated_on']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for expenses"""
    expensetype = ExpenseTypeSerializer(many=False, required=True)

    class Meta:
        model = Expense
        fields = ['id', 'amount', 'effective_date', 'expensetype']
        read_only_fields = ['id']

    def _get_or_create_expensetype(self, expensetype):
        """Handle getting or creating expenses types as needed"""
        auth_user = self.context['request'].user
        expensetype_obj, created = ExpenseType.objects.get_or_create(
            user=auth_user,
            **expensetype
        )
        return expensetype_obj

    def create(self, validated_data: dict):
        """Create an expense"""
        expensetype = validated_data.pop('expensetype')
        expensetype_obj = self._get_or_create_expensetype(expensetype)
        expense = Expense.objects.create(
            **validated_data,
            expensetype=expensetype_obj
            )

        return expense

    def update(self, instance, validated_data: dict):
        """Update an expense"""
        expensetype = validated_data.pop('expensetype', None)

        if expensetype:
            # instance.expensetype.clear()
            expensetype_obj = self._get_or_create_expensetype(expensetype)
            setattr(instance, 'expensetype', expensetype_obj)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ExpenseDetailSerializer(ExpenseSerializer):
    """Serializer extended for credit card"""

    class Meta(ExpenseSerializer.Meta):
        fields = ExpenseSerializer.Meta.fields + \
            ['created_on', 'updated_on']
        read_only_fields = ExpenseSerializer.Meta.read_only_fields + \
            ['created_on', 'updated_on']


class CreditExpenseSerializer(serializers.ModelSerializer):
    """Serializer for credit expenses"""
    expensetype = ExpenseTypeSerializer(many=False, required=True)
    creditcard = CreditCardSerializer(many=False, required=True)

    class Meta:
        model = CreditExpense
        fields = [
            'id',
            'amount',
            'effective_date',
            'expensetype',
            'creditcard',
            'is_paid',
            'cut_off_date',
            'payment_date'
            ]

        read_only_fields = ['id']

    def _get_or_create_expensetype(self, expensetype):
        """Handle getting or creating expenses types as needed"""
        auth_user = self.context['request'].user
        expensetype_obj, created = ExpenseType.objects.get_or_create(
            user=auth_user,
            **expensetype
        )
        return expensetype_obj

    def _get_creditcard(self, creditcard):
        """Handle getting a creditcard"""
        auth_user = self.context['request'].user
        creditdard_obj = CreditCard.objects.get(
            user=auth_user,
            **creditcard
        )

        return creditdard_obj

    def _get_dates(
            self,
            validated_data: CreditExpense,
            creditcardobject: CreditCard) -> datetime:
        """Gets the most close date for payment and cutoff"""
        pass

    def create(self, validated_data: dict):
        "Create credit expense"
        expensetype = validated_data.pop('expensetype')
        expensetype_obj = self._get_or_create_expensetype(expensetype)

        creditcard = validated_data.pop('creditcard')
        creditcard_obj = self._get_creditcard(creditcard)

        cut_off_date = datetime.now().date()
        payment_date = datetime.now().date()

        creditexpense = CreditExpense.objects.create(
            **validated_data,
            expensetype=expensetype_obj,
            creditcard=creditcard_obj,
            cut_off_date=cut_off_date,
            payment_date=payment_date
        )

        return creditexpense

    def update(sefl, instance, validated_data: dict):
        """Update creditexpense"""


class CreditExpenseDetailSerializer(CreditCardSerializer):

    class Meta(CreditExpenseSerializer.Meta):
        fields = CreditExpenseSerializer.Meta.fields + \
            ['created_on', 'updated_on']
        read_only_fields = CreditExpenseSerializer.Meta.read_only_fields + \
            ['created_on', 'updated_on']

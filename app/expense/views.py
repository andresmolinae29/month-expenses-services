"""
Views for expense API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    ExpenseType,
    CreditCard,
    Expense,
    CreditExpense
)
from expense import serializers


class ExpenseTypeViewSet(viewsets.ModelViewSet):
    """View for manage expenses APIs"""
    serializer_class = serializers.ExpenseTypeDetailSerializer
    queryset = ExpenseType.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve expenses for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ExpenseTypeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new creditcard"""
        serializer.save(user=self.request.user)


class CreditCardViewSet(viewsets.ModelViewSet):
    """view for manage credit card API"""
    serializer_class = serializers.CreditCardDetailSerializer
    queryset = CreditCard.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve creditcards for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CreditCardSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new creditcard"""
        serializer.save(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    """view for manage expense API"""
    serializer_class = serializers.ExpenseDetailSerializer
    queryset = Expense.objects.all()
    authentication_clasess = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve expense for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ExpenseSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new expense"""
        serializer.save(
            user=self.request.user
            )


class CreditExpenseViewSet(viewsets.ModelViewSet):
    """View for manage credit expense API"""
    serializer_class = serializers.CreditExpenseDetailSerializer
    queryset = CreditExpense.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve credit expense for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CreditExpenseSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new credit expense"""
        serializer.save(
            user=self.request.user
        )

"""
Views for expense API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Expense
from expense import serializers


class ExpenseViewSet(viewsets.ModelViewSet):
    """View for manage expenses APIs"""
    serializer_class = serializers.ExpenseDetailSerializer
    queryset = Expense.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve expenses for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ExpenseSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new expense"""
        serializer.save(user=self.request.user)

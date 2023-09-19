"""
Views for credit card API
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import CreditCard
from creditcard import serializers


class CreditCardViewSet(viewsets.ModelViewSet):
    """view for manage credit card API"""
    serializer_class = serializers.CreditCardSerializer
    queryset = CreditCard.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve creditcards for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')

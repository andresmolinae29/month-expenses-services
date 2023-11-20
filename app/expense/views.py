"""
Views for expense API
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta

from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request

from core.models import (
    ExpenseType,
    CreditCard,
    Expense,
    CreditExpense
)
from expense import serializers


class BasicExpenseAttrViewSet(viewsets.ModelViewSet):
    """Base viewset for expense attributes"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve expenses for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id')


class ExpenseTypeViewSet(BasicExpenseAttrViewSet):
    """View for manage expenses APIs"""
    serializer_class = serializers.ExpenseTypeDetailSerializer
    queryset = ExpenseType.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ExpenseTypeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new creditcard"""
        serializer.save(user=self.request.user)


class CreditCardViewSet(BasicExpenseAttrViewSet):
    """view for manage credit card API"""
    serializer_class = serializers.CreditCardDetailSerializer
    queryset = CreditCard.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CreditCardSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new creditcard"""
        serializer.save(user=self.request.user)


class ExpenseViewSet(BasicExpenseAttrViewSet):
    """view for manage expense API"""
    serializer_class = serializers.ExpenseDetailSerializer
    queryset = Expense.objects.all()

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


class CreditExpenseViewSet(BasicExpenseAttrViewSet):
    """View for manage credit expense API"""
    serializer_class = serializers.CreditExpenseDetailSerializer
    queryset = CreditExpense.objects.all()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CreditExpenseSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        """Creates a new expense"""
        serializer.save(
            user=self.request.user
            )

    def _get_dates(self, effective_date: str, max_day: int) -> datetime:
        """Gets the most close date for payment and cutoff"""
        try:
            date: datetime = datetime.strptime(effective_date, '%Y-%m-%d')
        except TypeError:
            date: datetime = effective_date
        if date.day > max_day:
            delta = relativedelta(months=+1)

        else:
            delta = relativedelta(0)

        date = datetime(date.year, date.month, max_day) + delta
        return date.date()

    def _get_or_create_expensetype(self, expensetype):
        """Handle getting or creating expenses types as needed"""
        expensetype_obj, created = ExpenseType.objects.get_or_create(
            user=self.request.user,
            **expensetype,
        )
        return expensetype_obj

    def _get_creditcard(self, creditcard):
        """Handle getting a creditcard"""
        creditdard_obj = CreditCard.objects.get(
            user=self.request.user,
            **creditcard,
        )

        return creditdard_obj

    def create(self, request: Request, *args, **kwars) -> Response:
        """Create credit expense"""
        credit_expense_data: dict = request.data

        expensetype = credit_expense_data.pop('expensetype')
        expensetype_obj = self._get_or_create_expensetype(expensetype)

        creditcard = credit_expense_data.pop('creditcard')
        creditcard_obj = self._get_creditcard(creditcard)

        cut_off_date = self._get_dates(
                credit_expense_data.get('effective_date'),
                creditcard_obj.cut_off_day
                )

        payment_date = self._get_dates(
                cut_off_date,
                creditcard_obj.payment_due_day
                )

        new_credit_expense = CreditExpense.objects.create(
            **credit_expense_data,
            cut_off_date=cut_off_date,
            payment_date=payment_date,
            expensetype=expensetype_obj,
            creditcard=creditcard_obj,
            user=self.request.user
        )

        serializer = serializers.CreditExpenseSerializer(new_credit_expense)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

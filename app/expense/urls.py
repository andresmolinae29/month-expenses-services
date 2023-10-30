"""
URLs mapping for the expense app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from expense import views


router = DefaultRouter()
router.register('expensetypes', views.ExpenseTypeViewSet)
router.register('creditcards', views.CreditCardViewSet)
router.register('expenses', views.ExpenseViewSet)
router.register('creditexpenses', views.CreditExpenseViewSet)

app_name = 'expense'

urlpatterns = [
    path('', include(router.urls))
]

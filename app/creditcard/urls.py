"""
URLs mapping for the credit card app
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from creditcard import views


router = DefaultRouter()
router.register('creditcards', views.CreditCardViewSet)

app_name = 'creditcard'

urlpatterns = [
    path('', include(router.urls))
]

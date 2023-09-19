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
router.register('expenses', views.ExpenseViewSet)

app_name = 'expense'

urlpatterns = [
    path('', include(router.urls))
]

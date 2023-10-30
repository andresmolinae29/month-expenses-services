"""
Database models
"""

from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_day(value):
    if value < 1 or value > 30:
        raise ValidationError(
            _("%(value) is not a permitted value"),
            params={"value": value}
        )


class UserManager(BaseUserManager):
    """Manager for users"""

    def create_user(self, email, password=None, **kwargs):
        """Create, save and return a new user"""
        if not email:
            raise ValueError('User must have and email address')
        user = self.model(
            email=self.normalize_email(email),
            **kwargs
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **kwargs):
        """Create, save and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class ExpenseType(models.Model):
    """Expense object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    constraints = models.UniqueConstraint(
        fields=[user, name],
        name='user_type_unique_expense_type'
        )

    def __str__(self) -> str:
        return self.name


class CreditCard(models.Model):
    """Credit card object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=50)
    cut_off_day = models.IntegerField(
        validators=[validate_day]
        )
    payment_due_day = models.IntegerField(
        validators=[validate_day]
        )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name


class Expense(models.Model):
    """Expense object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    expensetype = models.ForeignKey(
        ExpenseType,
        on_delete=models.CASCADE
    )

    amount = models.FloatField()
    effective_date = models.DateField()

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> int:
        return str(self.amount)


class CreditExpense(models.Model):
    """Credit expense object"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    expensetype = models.ForeignKey(
        ExpenseType,
        on_delete=models.CASCADE
    )

    creditcard = models.ForeignKey(
        CreditCard,
        on_delete=models.CASCADE
    )

    amount = models.FloatField()
    effective_date = models.DateField(null=False)
    is_paid = models.BooleanField(default=False)
    cut_off_date = models.DateField(null=False)
    payment_date = models.DateField(null=False)

    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(self.amount)

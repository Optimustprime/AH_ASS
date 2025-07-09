from django.utils.timezone import now
import uuid
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, request, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email Address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_super_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError('User must have an email Address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_super_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    username = models.CharField(max_length=255)
    advertiser = models.ForeignKey(
        'Advertiser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    is_active = models.BooleanField(default=False, null=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()
    USERNAME_FIELD = "email"

    def __str__(self):
        return self.email

class BaseFactModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class BaseDimensionModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Advertiser(BaseDimensionModel):
    advertiser_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Ad(BaseDimensionModel):
    ad_id = models.AutoField(primary_key=True)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    ad_title = models.CharField(max_length=255)
    ad_format = models.CharField(max_length=50)
    product_link = models.URLField()

    def __str__(self):
        return self.ad_title

class TimeHierarchy(BaseDimensionModel):
    time_key = models.DateField(primary_key=True)
    hour = models.IntegerField()
    day = models.IntegerField()
    week = models.IntegerField()
    month = models.IntegerField()
    weekday_name = models.CharField(max_length=10)

    class Meta:
        verbose_name_plural = "Time hierarchies"

class ClickEvent(BaseFactModel):
    click_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    click_time = models.DateTimeField(default=now)
    amount = models.FloatField()
    is_valid = models.BooleanField(default=True)

class SpendSummary(BaseFactModel):
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    window_start = models.DateTimeField()
    window_end = models.DateTimeField()
    gross_spend = models.FloatField()
    net_spend = models.FloatField()
    budget_at_time = models.FloatField()
    can_serve = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Spend summaries"

class BudgetEvent(BaseFactModel):
    event_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    advertiser = models.ForeignKey(Advertiser, on_delete=models.CASCADE)
    new_budget_value = models.FloatField()
    event_time = models.DateTimeField(default=now)
    source = models.CharField(max_length=50)
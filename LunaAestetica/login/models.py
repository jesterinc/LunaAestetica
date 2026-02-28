from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsersManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'email è obbligatoria')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=30)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsersManager() # Colleghiamo il manager!

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'



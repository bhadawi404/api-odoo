from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser

#  Custom User Manager
class UserManager(BaseUserManager):
  def create_user(self, username, db, url, key, password=None):
      """
      Creates and saves a User with the given username, db, url, key and password.
      """
      if not username:
          raise ValueError('User must have an username address')

      user = self.model(
          username=self.normalize_email(username),
          db=db,
          url=url,
          key=key
      )

      user.set_password(password)
      user.save(using=self._db)
      return user

  def create_superuser(self, username, db, url, key,location_name,company_name, password=None):
      """
      Creates and saves a superuser with the given email, name, tc and password.
      """
      user = self.create_user(
          username,
          password=password,
          db=db,
          url=url,
          key=key,
          location_name=location_name,
          company_name=company_name,
      )
      user.is_admin = True
      user.save(using=self._db)
      return user
  
#  Custom User Model
class User(AbstractBaseUser):
  username = models.EmailField(
      verbose_name='Email',
      max_length=255,
      unique=True,
  )
  db = models.CharField(max_length=200)
  url = models.CharField(max_length=200)
  key = models.CharField(max_length=200)
  location_name = models.CharField(max_length=200)
  company_name =  models.CharField(max_length=200)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)
  updated_at = models.DateTimeField(auto_now=True)

  objects = UserManager()

  USERNAME_FIELD = 'username'
  REQUIRED_FIELDS = ['db', 'url','key']

  def __str__(self):
      return self.username

  def has_perm(self, perm, obj=None):
      "Does the user have a specific permission?"
      # Simplest possible answer: Yes, always
      return self.is_admin

  def has_module_perms(self, app_label):
      "Does the user have permissions to view the app `app_label`?"
      # Simplest possible answer: Yes, always
      return True

  @property
  def is_staff(self):
      "Is the user a member of staff?"
      # Simplest possible answer: All admins are staff
      return self.is_admin
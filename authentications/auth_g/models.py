from django.db import models

from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from allauth.socialaccount.models import SocialAccount

class UserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError('the Email filed must be set')
        if not password:
            raise ValueError('set password')
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    

    def create_superuser(self,email,password=None,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("speruser must have is_staff=true.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("superuser must have is_superuser=True")
        

        return self.create_user(email,password,**extra_fields)
    


class User(AbstractBaseUser):
    leader_name=models.CharField(max_length=100)
    leader_email=models.EmailField(unique=True)
    profile_photo_url=models.URLField()
    payment_amount=models.DecimalField(max_digits=5,decimal_places=2,default=0)
    objects=UserManager
    google_oauth_account = models.OneToOneField(SocialAccount, on_delete=models.SET_NULL, null=True, blank=True,related_name='custom_user')

    USERNAME_FIELD='leader_email'
    REQUIRED_FIELDS=[]

    def __str__(self):
        return self.email
    

class team_members(models.Model):
    ROLE_CHOICES = [
    ('Bid', 'Bid'),
    ('Code', 'Code'),
    ]
    teammember1_name=models.CharField(max_length=100)
    teammember1_email=models.EmailField(unique=True)
    role1=models.CharField(max_length=10,choices=ROLE_CHOICES,default='Bid')
    teammember2_name=models.CharField(max_length=100)
    teammember2_email=models.EmailField(unique=True)
    role2=models.CharField(max_length=10,choices=ROLE_CHOICES,default='Bid')
    teammember3_name=models.CharField(max_length=100)
    teammember3_email=models.EmailField(unique=True)
    role3=models.CharField(max_length=10,choices=ROLE_CHOICES,default='Bid')
    leader=models.AutoField(primary_key=True)    


class PaymentTransaction(models.Model):
    user = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    receipt = models.CharField(max_length=255,default=None)
    razorpay_order_id = models.CharField(max_length=255)
    razorpay_payment_id = models.CharField(max_length=255)
    razorpay_signature = models.CharField(max_length=255)
    payment_status = models.CharField(max_length=20) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.user} - Amount: {self.amount} {self.currency}"


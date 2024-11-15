from django.db import models
from django.contrib.auth.models import User
# Create your models here.
from .constants import ACCOUNT_TYPE,GENDER_TYPE
#django amader buildin user provide kore

class UserBankAccount(models.Model):
    user = models.OneToOneField(User,related_name='account',on_delete=models.CASCADE)
    account_type = models.CharField(max_length=10,choices=ACCOUNT_TYPE)
    account_no = models.IntegerField(unique=True) # account no 2 jon user er same hobe nah
    birth_date = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=10,choices=GENDER_TYPE)
    initial_deposite_date = models.DateField(auto_now_add=True)
    balance = models.DecimalField(default=0,max_digits=12,decimal_places=2)
    #ekjon user 12 digit obdi taka rakhte parbe,dui doshomik ghor obdi rakhte parben , mane 100.20
    
    def __str__(self):
        return str(self.account_no)

# class UserBankAccount(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='account')
#     account_type =models.CharField(max_length=100,choices=ACCOUNT_TYPE)
#     account_no =models.IntegerField(unique=True)
#     birth_date = models.DateField(null=True,blank=True)
#     gender = models.CharField(max_length=10,choices=GENDER_TYPE)
#     initial_deposite_date = models.DateField(auto_now_add=True)
#     balance = models.DecimalField(max_length=12,default=0,decimal_places=2)

#     def __str__(self):
#         return str(self.account_no)

class UserAddress(models.Model):
    user = models.OneToOneField(User,related_name='address',on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    postal_code = models.IntegerField()
    country = models.CharField(max_length=100)

    def __str__(self):
        return str(self.user.email)
    


# class UserAddress(models.Model):
#     user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='address')
#     street_address = models.CharField(max_length=100)
#     city= models.CharField(max_length=100)
#     postal_code = models.IntegerField()
#     country = models.CharField(max_length=100)

#     def __str__(self):
#         return str(self.user.email)
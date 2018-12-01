from django.db import models
from django.urls import reverse
import uuid
from django.contrib.auth.models import User

from django import forms
from django.contrib.auth.models import User
import re

class ParentCate(models.Model):
    parentid = models.CharField(max_length=50,primary_key = True)
    parentname = models.CharField(max_length = 100)

class SubCate(models.Model):
    subid = models.CharField(max_length = 100, primary_key = True)
    subname = models.CharField(max_length = 100)
    parentid = models.ForeignKey(ParentCate,
    on_delete = models.CASCADE)

class Admin(models.Model):
    adminid = models.CharField(max_length = 100, primary_key = True)
    adminname = models.CharField(max_length = 100)
    email = models.CharField(max_length = 100)
    password = models.CharField(max_length = 100)



class UserProfile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    userid = models.UUIDField(default = uuid.uuid4(), primary_key = True)

    username = models.CharField(max_length = 100,default = "user")
    password = models.CharField(max_length = 100,default = "password1")
    phonenumber = models.CharField(max_length =20)
    address = models.CharField(max_length = 100)
    email = models.EmailField(max_length = 100)
    create_time = models.DateTimeField(auto_now_add = False, auto_now = True)
    has_confirmed = models.BooleanField(default=False)
    #adminid = models.ForeignKey(Admin,
    #    on_delete = models.CASCADE, default = "1")
    # useritemid = models.ManyToManyField('Item', blank = True)
    class Meta:
        ordering = ["-create_time"]
        verbose_name = 'User Profile'
        verbose_name_plural = "User Profiles"
    def __str__(self):
        return self.username
    def  user_id(self):
        return self.userid.__str__()

class ConfirmString(models.Model):
    code = models.CharField(max_length=256)
    user = models.OneToOneField('UserProfile',on_delete=models.CASCADE)
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + ":   " + self.code

    class Meta:
        ordering = ["-c_time"]
        verbose_name = "Confirmation Code"
        verbose_name_plural = "Confirmation Code"

class Item(models.Model):
    itemid = models.UUIDField(default=uuid.uuid4(), primary_key = True)
    name = models.CharField(max_length = 50)
    description = models.TextField()
    picture = models.ImageField(upload_to='item_image', blank = True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    condition = models.CharField(max_length = 50)
    #subcateid = models.ForeignKey(SubCate, related_name = 'sub_id',
    #on_delete = models.CASCADE)
    category = models.CharField(max_length = 50, default='Not Selected')
    userid = models.CharField(max_length = 50, blank = True)
    def  __str__(self):
        return self.name
    #adminid = models.ForeignKey(Admin,
    #on_delete = models.CASCADE)
# related_name = 'adminid',
# related_name = 'subname',
# related_name = 'userid',
 # related_name = 'adminid',
 # related_name = 'parentid',
# , primary_key = True

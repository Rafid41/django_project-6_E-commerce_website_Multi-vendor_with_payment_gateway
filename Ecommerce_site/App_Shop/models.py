# run migrations after completing models.py
# 1. py models.py makemigrations "App_Shop"
# py manage.py migrate
from django.db import models
from App_Login.models import User

# Create your models here.

# product categories
class Category(models.Model):
    title = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
    class Meta:
        # normally admin panel theke dekhle class er por "s" jog kore dey: means=> Category + s =Categorys
        # verbose_name_plural dle admin panel theke oi name tai show korbe
        verbose_name_plural = "Categories"



class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='related_name_product_seller')
    mainimage = models.ImageField(upload_to="Products")
    name = models.CharField(max_length=264)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category')
    preview_text = models.TextField(max_length=200, verbose_name='Preview Text') # short description of product
    detail_text = models.TextField(max_length=1000, verbose_name='Description')
    price = models.FloatField()
    old_price = models.FloatField(default= 0.0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created',]

                                    

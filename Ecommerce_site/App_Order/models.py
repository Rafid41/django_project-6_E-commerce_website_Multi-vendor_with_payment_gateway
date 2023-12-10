# run migrations after completing full models.py
# 1. py manage.py makemigrations App_Order
# 2. py manage.py migrate
# add to admin.py to register

from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
# Model
from App_Shop.models import Product


# Create your models here.

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart")
    item = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    purchased =models.BooleanField(default=False)  # NOTE: cart e oi product thake ja purchase kora hyny, purchase hole ta r cart e thakena
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.quantity} X {self.item}'
    

    # calculate total price of a particular item
    # self.item.price ==> ekhane item inherit korse "Product" class k , Product class er "price" field
    def get_total(self):
        total = self.item.price * self.quantity
        float_total = format(total, '0.2f')     # 2 decimal places
        return float_total
    



# cart er shob item --> 1 order
# ManyToMany relation, cz, 
# (i) 1 cart er 1 item onekgulo order e thakte pare
# (ii) 1 order e onekgulo cart er item thakte pare
class Order(models.Model):
    orderitems = models.ManyToManyField(Cart)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)  # order kora hoye gese kina
    created = models.DateTimeField(auto_now_add=True)
    paymentId = models.CharField(max_length=264, blank=True, null=True)     # payment korar por ei id ashbe, tar age null
    orderId = models.CharField(max_length=200, blank=True)
    #coupon_code = models.CharField(max_length=100, blank=True)


    # return all product cost, calls get_total() for individual product and sum all results
    def get_totals(self):
        total = 0
        for order_item in self.orderitems.all():
            total += float(order_item.get_total())
        return total
    

class Coupon(models.Model):
    coupon_code=models.CharField(max_length=100, unique=True)
    coupon_percent = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(100),    # set max Value
            MinValueValidator(1)       # set min Value
        ]
    )

    def __str__(self):
        return self.coupon_code


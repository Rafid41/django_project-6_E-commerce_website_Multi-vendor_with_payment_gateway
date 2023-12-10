from django.contrib import admin
from App_Order.models import Order, Cart, Coupon

# Register your models here.
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Coupon)

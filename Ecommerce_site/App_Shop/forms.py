from django import forms
from App_Shop.models import Product


# modify model structure
class AddProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ['name','category','mainimage','preview_text','detail_text','price','old_price']
        
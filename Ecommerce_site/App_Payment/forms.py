from django import forms
from App_Payment.models import BillingAddress




class BillingForm(forms.ModelForm):
    class Meta:
        model = BillingAddress
        fields = ['address','zipcode','city','country',]


class CollectCouponForm(forms.Form):
    collect = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(attrs={'placeholder':'Enter Coupon'})
    )
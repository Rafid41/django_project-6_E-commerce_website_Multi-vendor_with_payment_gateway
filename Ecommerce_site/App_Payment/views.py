from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib import messages
from django.urls import reverse

#models and forms
from App_Order.models import Order, Cart, Coupon
from App_Payment.forms import BillingAddress, BillingForm, CollectCouponForm

from django.contrib.auth.decorators import login_required

# payment sslcommerz
# documentation to use in project: https://pypi.org/project/sslcommerz-python/#:~:text=install%20sslcommerz%2Dpython-,Projected%20use,-from%20sslcommerz_python.payment
import requests
import socket
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal

# avoid csrf verification
from django.views.decorators.csrf import csrf_exempt

# views

coupon_percentise = 0



@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user= request.user)
    saved_address = saved_address[0]        # touple to object

    form = BillingForm(instance= saved_address)  # already save kora adds er upor form generate hbe, save na thakle blank form

    coupon_form = CollectCouponForm()
    global coupon_percentise
    coupon_percentise = 0

    
    if request.method == 'POST':
        form_name = request.POST.get('form_name')


        if form_name == 'address_form':
            form = BillingForm(request.POST, instance=saved_address)

            if form.is_valid():
                form.save()
                form = BillingForm(instance=saved_address)
                messages.success(request, f"Shipping Address Saved!")


        
        
        elif form_name == 'coupon_form':
            coupon_form = CollectCouponForm(request.POST)

            if coupon_form.is_valid():      
                collect_code = coupon_form.cleaned_data['collect']  #or, collect_code = coupon_form.cleaned_data.get('collect')
                
                try:
                    
                    coupon = Coupon.objects.get(coupon_code=collect_code)
                    coupon_percentise = coupon.coupon_percent
                    messages.success(request, f"Coupon Applied")

                except Coupon.DoesNotExist:
                    coupon_percentise = 0
                    messages.warning(request, f"Invalid coupon code")


    # show ordered items in checkout page
    order_qs = Order.objects.filter(user = request.user, ordered = False)
    order_items = order_qs[0].orderitems.all()          # 'orderitems' models.py er ekta field(App_Order)
    order_total = order_qs[0].get_totals()              # 'get_totals' models.y er ekta fn

    order_total_after_coupon_applied = 0

    if coupon_percentise > 0:
        order_total_after_coupon_applied = order_total-((order_total * coupon_percentise)/100)
    

    return render(request, 'App_Payment/checkout.html', 
                  context={
                      'form': form,
                      'order_items': order_items,
                      'order_total': order_total,
                      'saved_address': saved_address,
                      'coupon_form': coupon_form,
                      'order_total_after_coupon_applied' : order_total_after_coupon_applied,
                    })







'''
real one
'''   

# @login_required
# def checkout(request):
#     saved_address = BillingAddress.objects.get_or_create(user= request.user)
#     saved_address = saved_address[0]        # touple to object

#     form = BillingForm(instance= saved_address)  # already save kora adds er upor form generate hbe, save na thakle blank form
    
#     if request.method == 'POST':
#         form = BillingForm(request.POST, instance=saved_address)

#         if form.is_valid():
#             form.save()
#             form = BillingForm(instance=saved_address)
#             messages.success(request, f"Shipping Address Saved!")

#     # show ordered items in checkout page
#     order_qs = Order.objects.filter(user = request.user, ordered = False)
#     order_items = order_qs[0].orderitems.all()          # 'orderitems' models.py er ekta field(App_Order)
#     order_total = order_qs[0].get_totals()              # 'get_totals' models.y er ekta fn
    

#     return render(request, 'App_Payment/checkout.html', 
#                   context={
#                       'form': form,
#                       'order_items': order_items,
#                       'order_total': order_total,
#                       'saved_address': saved_address,
#                     })







# view for payment
@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user = request.user)
    saved_address = saved_address[0]

    # check all fields are filled //models.py
    if not saved_address.is_fully_filled():
        messages.info(request, f"Please complete shipping address!")
        return redirect("App_Payment:checkout")
    
    # App_login er modles.py er fn, "profile"==related_name
    if not request.user.profile.is_fully_filled():
        messages.info(request, f"Please complete profile detail")
        return redirect('App_Login:profile')
    
    # https://pypi.org/project/sslcommerz-python/

    #---------------------------- info-1:  mypayment ------------------------#
    #  sandbox na hoye real payment hole "sslc_is_sandbox=False", "sslc_store_id" & "sslc_store_pass" check from reply email from sslcoomerz, 
    mypayment = SSLCSession(sslc_is_sandbox=True, sslc_store_id='abcco656cf6297a654', sslc_store_pass='abcco656cf6297a654@ssl')
    

    #---------------------------- info-2: mypayment.set_urls() ------------------------#

    '''
    status_url = request.build_absolute_uri()
    # eta current view er url k call kore
    print(status_url)   #o/p: http://127.0.0.1:8000/payment/pay/
    '''
    status_url = request.build_absolute_uri(reverse("App_Payment:complete"))

    # print(status_url)   #http://127.0.0.1:8000/payment/status/

    #'success_url' payment success hole kon page e jabe, fail/cancel hole kon page, 'ipn_url'= special kono notification thakle kon page
    # we'll use a template here
    mypayment.set_urls(success_url=status_url, fail_url= status_url, cancel_url= status_url, ipn_url = status_url)



    #---------------------------- info-3:  mypayment.set_product_integration() ------------------------#
    # product info

    order_qs = Order.objects.filter(user = request.user, ordered= False)
    order_items = order_qs[0].orderitems.all()
    order_items_count = order_qs[0].orderitems.count()
    order_total = order_qs[0].get_totals()  # get_totals() is a fn from models.py

    if coupon_percentise > 0:
        order_total = order_total-((order_total * coupon_percentise)/100)
    
    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed', product_name= order_items, num_of_item=order_items_count, shipping_method='Courier', product_profile='None')



    #---------------------------- info-3:  mypayment.set_customer_info() ------------------------#
    # kono ekta field blank thakle error dekhabe, ejnno upore egula chk kora hoise

    current_user = request.user
    # 'profile' == related_name
    mypayment.set_customer_info(name= current_user.profile.full_name, email= current_user.email, address1= current_user.profile.address_1, address2= current_user.profile.address_1, city= current_user.profile.city, postcode= current_user.profile.zipcode, country= current_user.profile.country, phone= current_user.profile.phone)

 

    #---------------------------- info-3:  mypayment.set_shipping_info() ------------------------#
    # Billing info
    mypayment.set_shipping_info(shipping_to= current_user.profile.full_name, address= saved_address.address, city= saved_address.city, postcode= saved_address.zipcode, country= saved_address.country)


    # If you want to post some additional values
    # mypayment.set_additional_values(value_a='cusotmer@email.com', value_b='portalcustomerid', value_c='1234', value_d='uuid')


    response_data = mypayment.init_payment()
    #print(response_data)    #{'status': 'SUCCESS', 'sessionkey': '86A9ED514AFD61A49124ED056FBBD665', 'GatewayPageURL': 'https://sandbox.sslcommerz.com/EasyCheckOut/testcde86a9ed514afd61a49124ed056fbbd665'}


    # see the print(response_data) output to understand dict key 'GatewayPageURL'
    # redirected to sslcommerz payment system
    return redirect(response_data['GatewayPageURL'])



# accessing complete.html template// payment status (success/failure etc)
# payment er pore info ei page dekhabe
# @csrf_exempt deyar karone bangking er porer page(after pressing "success"/"successwith risk"/"failed" in payment bank/mobile_bank page)  e "post" method e ahob banking info gulo django show korbe(debug panel e ,error hole)
@csrf_exempt
def complete(request):

    if request.method=='post' or request.method=='POST':
        payment_data = request.POST
        status = payment_data['status']
        

        if status=='VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, f"Your Payment Completed Successfully! Page will be redirected!")

            # call purchase()
            return HttpResponseRedirect(reverse('App_Payment:purchase', kwargs={'val_id':val_id, 'tran_id':tran_id},))

        else:
            messages.warning(request, f"Your Payment Failed! Please Try Again! Page will be redirected!")


    return render(request, 'App_Payment/complete.html', context = {})


# purchase korar por cart clear korbe
# order er ordered=True and cart er purchased = True hbe
@login_required
def purchase(request, val_id, tran_id):

    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]

    order.ordered = True
    order.orderId = tran_id
    order.paymentId = val_id
    order.save()

    cart_items= Cart.objects.filter(user=request.user, purchased=False)

    for item in cart_items:
        item.purchased = True
        item.save()

    return HttpResponseRedirect(reverse('App_Shop:home'))


# show previous orders
@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {'orders': orders}

    except:
        messages.warning(request, "You do not have an active order")
        return redirect('App_Shop:home')

    return render(request, 'App_Payment/order.html', context)
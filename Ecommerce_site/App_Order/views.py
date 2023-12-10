from django.shortcuts import render, get_object_or_404, redirect

# Authentication
from django.contrib.auth.decorators import login_required

# Model
from App_Order.models import Cart, Order
from App_Shop.models import Product

# Messages
from django.contrib import messages

# Create your views here.

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)    # fetch the item using primary_key

    # check j cart e item already ase kina, na thakle create
    # oi user er e, purchased=False er jnno sudhu
    order_item = Cart.objects.get_or_create(item=item, user = request.user, purchased=False)

    order_qs = Order.objects.filter(user= request.user, ordered=False)
    # current user er kono incomplete order ase kina
    # order_qs[0] use kora hoise object k list e convert korte
    if order_qs.exists():
        order = order_qs[0]          # index 0 e incomplete order jeta "order" e save hoise

        # check if the current item is already in the order
        if order.orderitems.filter(item = item).exists():

            # item ase, new order ashse, tai quantity 1 barbe, order_item[0] use hoise object k list/dict e convert korte
            # TUPLE akare thakte pare, at a time 1 tai tuple thake, tai index=0 hole oitai peye jai
            # NOTE: 'quantity' models.py er 'Cart' class er ekta field
            order_item[0].quantity +=1  
            order_item[0].save()
            messages.info(request, "This item quantity was updated.")
            return redirect("App_Shop:home")
        
        else:   # item order e na thakle
            order.orderitems.add(order_item[0])
            messages.info(request, "This item was added to your cart.")
            return redirect("App_Shop:home")
        
    else: # kono inactive order nai
        #create new order and add item to that order
        order = Order(user= request.user)
        order.save()
        order.orderitems.add(order_item[0])
        messages.info(request, "This item was added to your cart.")
        return redirect("App_Shop:home")


# NOTE: order er kaj holo cart er shob item k bind kora


# Show cart items
@login_required
def cart_view(request):
    carts = Cart.objects.filter(user= request.user, purchased= False)
    orders = Order.objects.filter(user= request.user, ordered= False)

    if carts.exists() and orders.exists():
        order = orders[0]
        return render(request, 'App_Order/cart.html', context={'carts': carts, 'order': order})
    else:
        messages.warning(request, "You don't have any item in your cart!")
        return redirect("App_Shop:home")
    



@login_required
def remove_from_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    # jodi nkono order thake
    if order_qs.exists():
        # check j item remove korbo ta order er vitor ase kina
        order = order_qs[0]
        if order.orderitems.filter(item = item).exists():
            
            order_item = Cart.objects.filter(item = item, user = request.user, purchased = False)[0]       # item khuje ber kora ei user er jnno, last e [0] to convert tuple to accessible item

            # remove from orderitem
            order.orderitems.remove(order_item)
            # delete from cart
            order_item.delete()

            messages.warning(request, "This item was removed from your cart")
            return redirect("App_Order:cart")

        else:
            messages.info(request, "This item was not in your cart")
            return redirect('App_Shop:home')

    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")
    


# cart e '+' dle item quantity barbe
def increase_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    # jodi nkono order thake
    if order_qs.exists():
        # j item increase hbe ta order er item e ase kina
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            # increase quantity
            order_item = Cart.objects.filter(item = item, user = request.user, purchased = False)[0]

            if order_item.quantity >= 1:
                order_item.quantity += 1
                order_item.save()
                messages.info(request, f"{item.name} quantity has been updated")
                return redirect("App_Order:cart")
            
        else:
            messages.info(request, f"{item.name} is not in your cart")
            return redirect("App_Shop:home")

    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")
    



# cart e '-' dle item quantity kombe
def decrease_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_qs = Order.objects.filter(user=request.user, ordered= False)

    # jodi nkono order thake
    if order_qs.exists():
        # j item increase hbe ta order er item e ase kina
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            
            order_item = Cart.objects.filter(item = item, user = request.user, purchased = False)[0]

            # decrease quantity
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, f"{item.name} quantity has been updated")
                return redirect("App_Order:cart")
            
            else:
                # mane item 1 tai silo, seta bad dle item cart/order theke remove hye jabe
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.name} item has been removed from your cart")
                return redirect("App_Order:cart")

        else:
            messages.info(request, f"{item.name} is not in your cart")
            return redirect("App_Shop:home")

    else:
        messages.info(request, "You don't have an active order")
        return redirect("App_Shop:home")
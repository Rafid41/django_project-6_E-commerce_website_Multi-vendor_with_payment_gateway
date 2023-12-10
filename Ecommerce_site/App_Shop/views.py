from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

# import views
from django.views.generic import ListView, DetailView

#Models
from App_Shop.models import Product

# Mixin
from django.contrib.auth.mixins import LoginRequiredMixin


# add product
from App_Shop.forms import AddProductForm
from django.contrib.auth.decorators import login_required



# Create your views here.

# display products
class Home(ListView):
    # NOTE: ListView e context hisebe object_name set na korle by default 'object_list' name edata pass hy template e
    model = Product
    template_name = 'App_Shop/home.html'



class ProductDetail(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'App_Shop/product_detail.html'



@login_required
def add_product(request):
    form = AddProductForm()
    if request.method == 'POST':
        form = AddProductForm(request.POST, request.FILES)

        if form.is_valid():
            
            product = form.save(commit = False)
            product.seller = request.user
            product.save()

            return HttpResponseRedirect(reverse('App_Shop:home'))

    return render(request, 'App_Shop/add_product.html', context={'form': form})
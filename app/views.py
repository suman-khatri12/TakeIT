from django.shortcuts import render, redirect
from django.views import View
from .models import (Customer, Product, OrderPlaced, Cart)
from .forms import CustomerRegsitrationForm, LoginForm, CustomerProfileForm
from django.contrib import messages
from  django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class ProductView(View):
    def get(self, request):
        topwears = Product.objects.filter(category="TW")
        bottomwears = Product.objects.filter(category="BW")
        mobiles = Product.objects.filter(category="M")
        return render(request, 'app/home.html', {
            "bottomwears": bottomwears,
            "bottomwears": bottomwears,
            "mobiles": mobiles})


class ProductDetailView(View):
    def get(self, request, pk):
        product = Product.objects.get(pk=pk)
        item_aleardy = False
        if request.user.is_authenticated:
            item_aleardy = Cart.objects.filter(Q(product = product.id) & Q(user = request.user)).exists()

        return render(request, "app/productdetail.html", {'product': product, 'item_already': item_aleardy})

@login_required
def add_to_cart(request):
    user = request.user
    product = request.GET.get('prod_id')
    prod = Product.objects.get(id = product)
    Cart(user=user, product=prod).save()
    return redirect('/cart')


@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                temp = p.quantity * p.product.discounted_price
                amount += temp
                total = amount + shipping_amount
            return render(request, 'app/addtocart.html', {'carts': cart, 'totalamount': total, 'amount': amount})
        else:
            return render(request, 'app/emptycart.html')

@login_required
def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product =prod_id) & Q(user = request.user))
        c.quantity+= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp = p.quantity * p.product.discounted_price
                amount += temp

                data = {
                    "quantity": c.quantity,
                    "amount": amount,
                    "total": amount + shipping_amount,
                }
            return JsonResponse(data)


@login_required
def minus_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product =prod_id) & Q(user = request.user))
        c.quantity-= 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp = p.quantity * p.product.discounted_price
                amount = temp
                data = {
                    "quantity": c.quantity,
                    "amount": amount,
                    "total": amount + shipping_amount,
                }
            return JsonResponse(data)

@login_required
def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product =prod_id) & Q(user = request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                temp = p.quantity * p.product.discounted_price
                amount += temp

                data = {
                    "amount": amount,
                    "total": amount+ shipping_amount,
                }
            return JsonResponse(data)





@login_required
def address(request):
    add = Customer.objects.filter(user=request.user)
    print(add)
    return render(request, 'app/address.html', {"add": add})

@login_required
def orders(request):
    orders = OrderPlaced.objects.filter(user = request.user)

    return render(request, 'app/orders.html',{'orderplaced':orders})



def mobile(request, data=None):
    brand = Product.objects.filter(category='M').values_list('brand', flat=True).distinct()
    if data == None:
        mobiles = Product.objects.filter(category='M')
    elif data:
        mobiles = Product.objects.filter(category='M').filter(brand=data)
    return render(request, 'app/mobile.html', {"mobiles": mobiles, 'brand': brand})


class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegsitrationForm()
        return render(request, 'app/customerregistration.html', {'form': form})

    def post(self, request):
        form = CustomerRegsitrationForm(request.POST)
        if form.is_valid():
            messages.success(request, "Successfully registered")
            form.save()
        return render(request, 'app/customerregistration.html', {'form':form})

@login_required
def checkout(request):
    user =request.user
    add = Customer.objects.filter(user = user)
    cart_items = Cart.objects.filter(user = user)
    amount = 0.0
    shipping_amount = 70.0
    total = 0.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            temp = p.quantity * p.product.discounted_price
            amount += temp
        total = amount + shipping_amount
    return render(request, 'app/checkout.html', {'add':add, 'total':total,'cart_items':cart_items})

@login_required
def paymentdone(request):
    user = request.user
    custid = request.GET.get('custid')
    customer = Customer.objects.get(id=custid)
    cart = Cart.objects.filter(user = user)
    for c in cart:
        OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
        c.delete()
    return redirect('orders')




class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm
        return render(request, 'app/profile.html', {'form':form,'active':'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        if form.is_valid():
            usr = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            zipcode = form.cleaned_data['zipcode']
            state = form.cleaned_data['state']
            reg = Customer(user=usr, name=name, state=state,locality = locality, city=city,zipcode=zipcode)
            reg.save()
            messages.success(request, "successfully updated profile")

            return render(request, 'app/home.html', {'form':form, 'active': 'btn-primary'})







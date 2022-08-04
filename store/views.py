from django.contrib.auth import login
from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from django.views.generic import CreateView, FormView
from .forms import CustomerRegistrationForm, CustomerLoginForm
from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login


def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'home.html', context)


def cart(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'cart.html', context)


def checkout(request):
    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'checkout.html', context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Payment submitted..', safe=False)


# class CustomerLoginView(FormView):
#     template_name = "customerlogin.html"
#     form_class = CustomerLoginForm
#     success_url = reverse_lazy('home')
#
#     def form_valid(self, form):
#         uname = form.cleaned_data.get('username')
#         p_word = form.cleaned_data.get('password')
#         user = authenticate(username=uname, password=p_word)
#         if user is not None and user.customer:
#             login(self.request, user)
#         else:
#             return render(self.request, self.template_name,
#                           {"form": self.form_class, "error": "Invalid username or password"})
#
#         return super().form_valid(form)
#
#         # to overide the success_url variable
#
#     def get_success_url(self):
#         if 'next' in self.request.GET:
#             next_url = self.request.GET['next']
#             return next_url
#         else:
#             return self.success_url
#
#
# class CustomerRegistration(CreateView):
#     template_name = "customerregistration.html"
#     form_class = CustomerRegistrationForm
#     success_url = reverse_lazy('store:main')
#
#     def form_valid(self, form):
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         email = form.cleaned_data.get('email')
#         user = User.objects.create_user(username, email, password)
#         form.instance.user = user
#         login(self.request, user)
#         return super().form_valid(form)
#
#     # to overide the success_url variable
#     def get_success_url(self):
#         if 'next' in self.request.GET:
#             next_url = self.request.GET['next']
#             return next_url
#         else:
#             return self.success_url

class CustomerRegistration(CreateView):
    template_name = "customerregistration.html"
    form_class = CustomerRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        email = form.cleaned_data.get('email')
        user = User.objects.create_user(username, email, password)
        form.instance.user = user
        login(self.request, user)
        return super().form_valid(form)

    # to overide the success_url variable
    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET['next']
            return next_url
        else:
            return self.success_url


class CustomerLoginView(FormView):
    template_name = "customerlogin.html"
    form_class = CustomerLoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        uname = form.cleaned_data.get('username')
        p_word = form.cleaned_data.get('password')
        user = authenticate(username=uname, password=p_word)
        if user is not None and user.customer:
            login(self.request, user)
        else:
            return render(self.request, self.template_name,
                          {"form": self.form_class, "error": "Invalid username or password"})

        return super().form_valid(form)

    # to overide the success_url variable
    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url = self.request.GET['next']
            return next_url
        else:
            return self.success_url

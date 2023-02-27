import json
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from .models import MenuItem, Category, OrderModel
from django.shortcuts import render,redirect
from django.contrib import messages
from django.contrib.auth.models import User,auth
from .models import OrderModel

# Create your views here.

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')

class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')

class Order(View):
    def get(self, request, *args, **kwargs):
        biryani = MenuItem.objects.filter(category__name__contains='biryani')
        appetizers = MenuItem.objects.filter(category__name__contains='Appetizer')
        entres = MenuItem.objects.filter(category__name__contains='Entre')
        desserts = MenuItem.objects.filter(category__name__contains='Dessert')
        drinks = MenuItem.objects.filter(category__name__contains='Drink')

        context = {
            'appetizers': appetizers,
            'entres': entres,
            'desserts': desserts,
            'drinks': drinks,
            'biryani':biryani,
        }

        return render(request, 'customer/order.html', context)

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')

        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }

            order_items['items'].append(item_data)

            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])

        order = OrderModel.objects.create(
            price=price,
            name=name,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
        )
        order.items.add(*item_ids)

        body = ('Thank you for your order! Your food is being prepered and will be delivered soon!\n'
                f'Your total: {price}\n'
                'Thank you again for your order!')

        send_mail(
            'Thank You For Your Order!',
            body,
            'example@example.com',
            [email],
            fail_silently=False
        )

        context = {
            'items': order_items['items'],
            'price': price
        }

        return redirect('order-confirmation', pk=order.pk)
    
class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = OrderModel.objects.get(pk=pk)

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
        }

        return render(request, 'customer/order_confirmation.html', context)

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)

        if data['isPaid']:
            order = OrderModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()

        return redirect('payment-confirmation')

class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)

class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)

def register_re(request):
    if request.method == 'POST':
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        password1 = request.POST['password_1']
        password2 = request.POST['password_2']
        if password1 != password2:
            messages.error(request,'Both password are not same')
            return redirect('register_re')
        elif User.objects.filter(username = username).exists():
            messages.error(request,'name is used')
            return redirect('register_re')
        elif User.objects.filter(email = email).exists():
            messages.error(request,'email is used')
            return redirect('register_re')
        else:
            userdata = User.objects.create_user(username = username,first_name= firstname,last_name=lastname,email = email,password=password1)
            userdata.save()
            return redirect('re_login')
    return render(request,'restarent/register.html',)

def re_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username = username,password = password)
       
        if user is not None:
            auth.login(request,user)
            return redirect("home")
        else:
            messages.info(request,'invalid details')
            return redirect('re_login')
    
    return render(request,'restarent/login.html')

def home(request):
    my_data = OrderModel.objects.all()
    return render(request,'restarent/home.html',{'my_data': my_data})
    
def logout(request):
    auth.logout(request)
    return redirect('re_login')

def delete(request, id):
    OrderModel.objects.get(id=id).delete()
    return redirect('home')
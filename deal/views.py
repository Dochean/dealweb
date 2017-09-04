from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import LoginForm, RegisterForm
from .models import Good, Cart, Order, OrderList, WebUser
import json

# Create your views here.

def login(request):
    errors = []
    if request.user.is_authenticated():
        return redirect('home')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return redirect('home')
            errors.append('用户名密码错误或用户不存在。')
        errors.append('请正确填写表单！')
    else:
        form = LoginForm()
    return render(request, "login.html", {"errors": errors, "form": form})

@login_required
def logout(request):
    auth.logout(request)
    return redirect("home")

def register(request):
    errors = []
    infos = []
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            pwd = data['pwd2']
            email = data['email']
            try:
                user = User.objects.filter(username=username)[0:1].get()
            except ObjectDoesNotExist:
                user = None
            if user is not None:
                errors.append('用户名已存在.')
                return render(request, 'register.html', {"errors": errors, "form": form})
            user = User(username=username)
            user.set_password(pwd)
            user.email = email
            user.save()
            webuser = WebUser(user=user)
            webuser.save()
            infos.append('注册成功。')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {"errors": errors, "form": form})

def homepage(request):
    goods = Good.objects.all()
    context = {
        "goods": goods,
    }
    return render(request, "index.html", context)

def good(request, id):
    good = Good.objects.filter(id=id)[0]
    context = {
        "good": good,
    }
    return render(request, "good.html", context)

def add_good(request):
    if request.user.is_authenticated():
        for k, v in request.GET.items():
            #print(k, v)
            cart = None
            good = None
            try:
                good = Good.objects.filter(pk=int(k))[0:1].get()
            except ObjectDoesNotExist:
                good = None
            if good is not None:
                try:
                    cart = Cart.objects.filter(good=good, user=request.user)[0:1].get()
                except ObjectDoesNotExist:
                    cart = None
                if cart is not None:
                    cart.count += int(v)
                else:
                    cart = Cart(good=good, user=request.user, count=int(v))
                cart.save()
                res = json.dumps({'au':'true', 'op': 'true'})
            else:
                res = json.dumps({'au':'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)

@login_required
def carts(request):
    carts = Cart.objects.filter(user=request.user).all()
    for c in carts:
        c.ap = c.good.price*c.count
    context = {
        "carts": carts,
    }
    return render(request, 'carts.html', context)

def save_carts(request):
    if request.user.is_authenticated():
        carts = []
        flag = 0
        for k, v in request.GET.items():
            cart = None
            good = None
            try:
                good = Good.objects.filter(pk=int(k))[0:1].get()
            except ObjectDoesNotExist:
                good = None
            if good is not None:
                try:
                    cart = Cart.objects.filter(good=good, user=request.user)[0:1].get()
                except ObjectDoesNotExist:
                    cart = None
                if cart is not None and int(v)>0:
                    cart.count=int(v)
                    carts.append(cart)
                    flag = 1
                else:
                    flag = 0
                    break
            else:
                flag = 0
                break
        if flag:
            for c in carts:
                c.save()
            res = json.dumps({'au': 'true', 'op': 'true'})
        else:
            res = json.dumps({'au': 'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)

def del_good(request):
    if request.user.is_authenticated():
        try:
            cart = Cart.objects.filter(id=int(request.GET.get('id')))[0:1].get()
        except ObjectDoesNotExist:
            cart = None
        if cart is not None:
            cart.delete()
            res = json.dumps({'au': 'true', 'op': 'true'})
        else:
            res = json.dumps({'au': 'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)

def create_order(request):
    if request.user.is_authenticated():
        try:
            carts = Cart.objects.filter(user=request.user).all()
        except ObjectDoesNotExist:
            carts = None
        if carts is not None:
            flag = 1
            order_list = OrderList(user=request.user)
            order_list.save()
            lits = []
            ap = 0
            for cart in carts:
                order = None
                if cart.count <= cart.good.left:
                    order = Order(good=cart.good, count=cart.count, order_list=order_list)
                    order.ap = cart.good.price*cart.count
                    ap += order.ap
                    lits.append(order)
                else:
                    flag = 0
                    break
            if flag == 1:
                for cart in carts:
                    cart.good.left -= cart.count
                    cart.good.save()
                    cart.delete()
                for l in lits:
                    l.save()
                order_list.ap = ap
                order_list.save()
                res = json.dumps({'au': 'true', 'op': 'true'})
            else:
                order_list.delete()
                res = json.dumps({'au': 'true', 'op': 'false'})
        else:
            res = json.dumps({'au': 'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)

@login_required
def orders(request):
    order_lists = OrderList.objects.filter(user=request.user, status__gte=0).all().order_by('-stamp')

    for ol in order_lists:
        ol.ap = 0
        for o in ol.orders.all():
            ol.ap += o.ap
    #u = WebUser.objects.filter(user=request.user).get()
    u = request.user.webuser
    context = {
        'order_lists': order_lists,
        'money': u.money,
    }
    return render(request, "order_list.html", context)

def clear_order(request):
    if request.user.is_authenticated():
        try:
            ol = OrderList.objects.filter(id=int(request.GET.get('id')))[0:1].get()
        except ObjectDoesNotExist:
            ol = None
        if ol is not None:
            u = request.user.webuser
            if u.money >= ol.ap:
                u.money -= ol.ap
                ol.status = 1
                u.save()
                ol.save()
                res = json.dumps({'au': 'true', 'op': 'true'})
            else:
                res = json.dumps({'au': 'true', 'op': 'false'})
        else:
            res = json.dumps({'au': 'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)

def del_order(request):
    if request.user.is_authenticated():
        try:
            ol = OrderList.objects.filter(id=int(request.GET.get('id')))[0:1].get()
        except ObjectDoesNotExist:
            ol = None
        if ol is not None:
            ol.status = -1
            ol.save()
            res = json.dumps({'au': 'true', 'op': 'true'})
        else:
            res = json.dumps({'au': 'true', 'op': 'false'})
    else:
        res = json.dumps({'au': 'false', 'op': 'false'})
    return HttpResponse(res)
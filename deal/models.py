from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

# Create your models here.
class WebUser(models.Model):
    """user table"""

    user = models.OneToOneField(User, related_name="webuser")
    description = models.TextField(max_length=51200)
    money = models.IntegerField(default=10000)

    def __str__(self):
        return self.user.username

class Good(models.Model):
    """good table"""

    name = models.CharField(max_length=100)
    left = models.IntegerField()
    price = models.IntegerField()
    info = models.TextField(blank=True, default='')
    img = models.ImageField(default='', upload_to='deal/static/images/')

    def __str__(self):
        return self.name

class Cart(models.Model):
    """cart table"""

    good = models.ForeignKey(Good, related_name="incarts")
    user = models.ForeignKey(User, related_name="carts")
    count = models.IntegerField(default=0)

    def __str__(self):
        return self.good.name

class OrderList(models.Model):
    """ list table  0:待付, 1:支付完成, 2:已接收, 3:交易失败,"""

    user = models.ForeignKey(User, related_name="order_lists")
    status = models.IntegerField(default=0)
    stamp = models.DateTimeField(auto_now_add=True, blank=True)
    ap = models.IntegerField(default=0)

class Order(models.Model):
    """order table """

    good = models.ForeignKey(Good, related_name="orders")
    #user = models.ForeignKey(User, related_name="orders")
    count = models.IntegerField(default=0)
    #status = models.IntegerField(default=0)
    ap = models.IntegerField(default=0)
    order_list = models.ForeignKey(OrderList, related_name="orders")
    #stamp = models.DateTimeField(auto_now_add=True, blank=True, default=datetime.utcnow)

    def __str__(self):
        return self.good.name
from django.conf.urls import url, include
from .views import homepage, login, logout, good, add_good, carts, save_carts, del_good, register
from .views import create_order, orders, clear_order, del_order

urlpatterns = [
    url(r'^$', homepage, name="home"),
    url(r'^login/$', login, name="login"),
    url(r'^register/$', register, name="register"),
    url(r'^logout/', logout, name="logout"),
    url(r'^good/(?P<id>\d)/$', good, name="good"),
    url(r'^add-to-cart/', add_good, name="add-good"),
    url(r'^carts/', carts, name='carts'),
    url(r'^save-carts/', save_carts, name="save-carts"),
    url(r'^del-good/', del_good, name="del-good"),
    url(r'^create-order/', create_order, name="create-order"),
    url(r'^orders/', orders, name="orders"),
    url(r'^clear-order/', clear_order, name="clear-order"),
    url(r'^del-order/', del_order, name="del-order"),
]
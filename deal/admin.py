from django.contrib import admin
from .models import WebUser, Good, Cart
# Register your models here.

@admin.register(WebUser)
class UserAdmin(admin.ModelAdmin):
    #fields = ('name', 'passw')
    #list_display('passwd',)
    pass

@admin.register(Good)
class GoodAdmin(admin.ModelAdmin):
    
    pass

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass
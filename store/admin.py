from django.contrib import admin
from .models import Category, Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'image', 'is_active')


admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
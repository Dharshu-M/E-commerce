from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from store.models import Category, Product


def home(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', '').strip()

    if query:
        products = products.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(category__name__icontains=query)
        )

    if category_id.isdigit():
        products = products.filter(category_id=category_id)

    return render(request, 'client_side/home.html', {
        'products': products,
        'categories': Category.objects.all().order_by('name'),
        'query': query,
        'selected_category': category_id,
    })



def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(pk=product.pk)[:4]
    )
    return render(request, "client_side/product_detail.html", {
        "product": product,
        "related_products": related_products,
    })

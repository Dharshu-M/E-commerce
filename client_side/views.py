from django.db.models import Q
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render, redirect
from store.models import Category, Product, Wishlist


def _category_icon_class(name):
    name = name.lower()
    if 'mobile' in name or 'phone' in name:
        return 'bi-phone'
    if 'electronic' in name:
        return 'bi-headphones'
    if 'fashion' in name:
        return 'bi-handbag'
    if 'shoe' in name or 'foot' in name:
        return 'bi-sunglasses'
    if 'accessor' in name:
        return 'bi-smartwatch'
    if 'home' in name or 'living' in name:
        return 'bi-house-heart'
    if 'beauty' in name:
        return 'bi-brush'
    if 'toy' in name or 'game' in name:
        return 'bi-controller'
    if 'kitchen' in name:
        return 'bi-cup-hot'
    if 'sport' in name:
        return 'bi-dribbble'
    return 'bi-grid-3x3-gap-fill'


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

    wishlist_product_ids = set()
    if request.user.is_authenticated:
        wishlist_product_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    categories = Category.objects.all().order_by('name')
    for category in categories:
        category.icon_class = _category_icon_class(category.name)

    return render(request, 'client_side/home.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'wishlist_product': wishlist_product_ids,
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
        "in_wishlist": request.user.is_authenticated and Wishlist.objects.filter(
            user=request.user, product=product
        ).exists(),
    })

from django.shortcuts import get_object_or_404, render, redirect
from .models import Category,Product,AddToCart,Wishlist,Order,OrderItem
from django.db.models import Q,Sum,F
import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from django.utils.http import url_has_allowed_host_and_scheme

# Create your views here.

def base(request):
    return render(request,'base.html')

def owner_home(request):
    products = Product.objects.select_related('category')

    context = {
        'total_products': products.count(),
        'active_products': products.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'out_of_stock': products.filter(stock=0).count(),
        'low_stock': products.filter(stock__gt=0, stock__lte=5).order_by('stock')[:10],
        'recent_products': products.order_by('-created_at')[:5],
        'stock_value': products.aggregate(
            total=Sum(F('price') * F('stock'))
        )['total'] or 0,
    }
    return render(request, 'store/owner_home.html', context)

def add_category(request):
    if request.method == 'POST':
        name=request.POST.get("name")
        if name:
          Category.objects.get_or_create(name=name)
          return redirect("add_category")
    return render(request,'store/category.html')

def add_product(request):
    if request.method == 'POST':
        Product.objects.create(
            category_id=request.POST.get("category"),
            name=request.POST.get("name"),
            description=request.POST.get("description", ""),
            price=request.POST.get("price"),
            stock=request.POST.get("stock") or 0,
            image=request.FILES.get("image"),
            is_active=request.POST.get("is_active") == "on",
        )
        return redirect("add_product")
    categories=Category.objects.all()
    return render(request,'store/product.html',{"categories":categories})

def _product_view(request):
    
    products = Product.objects.select_related("category")

    q = request.GET.get("q")
    if q:
        products = products.filter(
            Q(name__icontains=q) | Q(category__name__icontains=q)
        )

    return render(request, "store/_product_list.html", {"products": products})

def update_product(request,id):
    product = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product.category_id = request.POST.get("category")
        product.name = request.POST.get("name", product.name)
        product.description = request.POST.get("description", product.description)
        product.price = request.POST.get("price", product.price)
        product.stock = request.POST.get("stock", product.stock) or 0
        product.is_active = request.POST.get("is_active") == "on"
        if request.FILES.get("image"):
            product.image = request.FILES["image"]
        product.save()
        return redirect("product_list")

    categories = Category.objects.all()
    return render(request, "store/product.html", {"product": product, "categories": categories})

def delete_product(request,id):
    proct_del=Product.objects.get(id=id)
    proct_del.delete()
    return render(request, "store/_product_list.html")
    



def addTocart(request):
    
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            if request.user.is_authenticated:
                data = json.load(request)
                product_qty = int(data['product_qty'])
                pid = data['pid']

                product = Product.objects.filter(id=pid, is_active=True).first()
                if not product:
                    return JsonResponse({'status': 'Product not found'}, status=200)
                if product.stock == 0:
                    return JsonResponse({'status': 'Sold out'}, status=200)
                if product_qty < 1:
                    return JsonResponse({'status': 'Invalid quantity'}, status=200)

                item, created = AddToCart.objects.get_or_create(
                    user=request.user, product=product, defaults={'quantity': 0}
                )
                item.quantity = min(item.quantity + product_qty, product.stock) 
                item.save()
                print(item.quantity,created)
                return JsonResponse({'status': 'success'}, status=200)
            else:
                return JsonResponse({'status': 'Login to addcart'}, status=200)
        else:
            return JsonResponse({'status': 'invalid'}, status=200)
    
    
@login_required
def cart_detail(request):
    items = AddToCart.objects.filter(user=request.user).select_related("product")
    total = sum(i.subtotal for i in items)
    return render(request, "client_side/cart_detail.html", {"items": items, "total": total})


@login_required
@require_POST
def cart_update(request, item_id):
    item = get_object_or_404(AddToCart, id=item_id, user=request.user)

    qty = int(request.POST.get("quantity", 1))

    if qty > item.product.stock:
        qty = item.product.stock
    if qty < 1:
        qty = 1

    item.quantity = qty
    item.save()
    return redirect("cart_detail")


@login_required
@require_POST
def cart_remove(request, item_id):
    item = get_object_or_404(AddToCart, id=item_id, user=request.user)
    item.delete()
    return redirect("cart_detail")




@require_POST
def toggleWishlist(request):
    next_url = request.POST.get('next', '')
    if not request.user.is_authenticated:
        return redirect('login')

    product = Product.objects.filter(id=request.POST.get('pid'), is_active=True).first()
    if not product:
        return redirect(next_url if url_has_allowed_host_and_scheme(next_url, {request.get_host()}) else 'client_home')

    item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    if not created:
        item.delete()
    return redirect(next_url if url_has_allowed_host_and_scheme(next_url, {request.get_host()}) else 'client_home')

@login_required
def wishlist_detail(request):
    items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "client_side/wishlist.html", {"items": items})


@login_required
@require_POST
def wishlist_remove(request, item_id):
    item = get_object_or_404(Wishlist, id=item_id, user=request.user)
    item.delete()
    return redirect("wishlist_detail")





@login_required
def checkout(request):
    items = AddToCart.objects.filter(user=request.user).select_related("product")
    if not items:
        return redirect("cart_detail")

    total = sum(i.subtotal for i in items)
    previous_order = Order.objects.filter(user=request.user).order_by("-created_at").first()
    ctx = {
        "items": items,
        "total": total,
        "form": {
            "full_name": previous_order.full_name if previous_order else "",
            "phone": previous_order.phone if previous_order else "",
            "address": previous_order.address if previous_order else "",
            "city": previous_order.city if previous_order else "",
            "pincode": previous_order.pincode if previous_order else "",
        },
    }

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        pincode = request.POST.get("pincode", "").strip()
        ctx["form"] = request.POST

        if not all([full_name, phone, address, city, pincode]):
            ctx["error"] = "Please fill in all the fields."
            return render(request, "client_side/checkout.html", ctx)

        
        for i in items:
            p = i.product
            if p.stock < i.quantity:
                ctx["error"] = f"Only {p.stock} of {p.name} left. Please update your cart."
                return render(request, "client_side/checkout.html", ctx)

        order = Order.objects.create(
            user=request.user, full_name=full_name, phone=phone,
            address=address, city=city, pincode=pincode,
            total=total, payment_method="COD",
        )

        for i in items:
            p = i.product
            OrderItem.objects.create(
                order=order, product=p, name=p.name,
                price=p.price, quantity=i.quantity,
            )
            p.stock -= i.quantity
            p.save()

        AddToCart.objects.filter(user=request.user).delete()

        return redirect("order_success", order_id=order.id)

    return render(request, "client_side/checkout.html", ctx)


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "client_side/order_success.html", {"order": order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "client_side/my_orders.html", {"orders": orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "client_side/order_detail.html", {"order": order})

@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == "Pending":
        for item in order.items.all():
            if item.product:                      
                item.product.stock += item.quantity
                item.product.save()

        order.status = "Cancelled"
        order.save()

    return redirect("order_detail", order_id=order.id)

@require_POST
def user_logout(request):
    logout(request)
    return redirect("client_home")

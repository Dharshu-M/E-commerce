from django.contrib import admin
from django.urls import path
from . import views

urlpatterns=[
    path('page/',views.base,name='page_base'),
    path('home/',views.owner_home,name='owner_home'),
    path('category/add',views.add_category,name='add_category'),
    path('product/add',views.add_product,name='add_product'),
    path('product/list',views._product_view,name='product_list'),
    path('product/update/<int:id>',views.update_product,name='product_update'),
    path('product/delete/<int:id>',views.delete_product,name='product_delete'),
    path('addTocart/',views.addTocart,name='add_to_cart'),
    path("cart_detail/",views.cart_detail,name='cart_detail'),
    path("addTocart/update/<int:item_id>/", views.cart_update, name="cart_update"),
    path("addTocart/remove/<int:item_id>/", views.cart_remove, name="cart_remove"),
    path("toggleWishlist/", views.toggleWishlist, name="toggle_wishlist"),
    path("wishlist/", views.wishlist_detail, name="wishlist_detail"),
    path("wishlist/remove/<int:item_id>/", views.wishlist_remove, name="wishlist_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-success/<int:order_id>/", views.order_success, name="order_success"),
    path("logout/", views.user_logout, name="logout"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("my-orders/<int:order_id>/", views.order_detail, name="order_detail"),
    path("my-orders/<int:order_id>/cancel/", views.cancel_order, name="cancel_order"),
]
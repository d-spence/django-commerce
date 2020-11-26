from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("listing/<int:listing_id>/", views.listing_view, name="listing"),
    path("listing/<int:listing_id>/comment/", views.post_comment, name="post-comment"),
    path("listing/<int:listing_id>/bidding/", views.place_bid, name="place-bid"),
    path("category/", views.category_view, name="category"),
    path("category/<str:category>/", views.index, name="index-by-category"),
    path("watchlist/", views.watch_list, name="watchlist"),
    path("watchlist/add/<int:listing_id>", views.watch_list_add, name="watchlist-add"),
    path("watchlist/rem/<int:listing_id>", views.watch_list_rem, name="watchlist-rem"),
]

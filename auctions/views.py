from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Comment, Category, Bid
from .forms import CommentForm, BiddingForm


def index(request, category=None, is_active=True):
    listings = Auction.objects.filter(active=True)
    if category is not None:
        cat = Category.objects.get(name=category)
        listings = listings.filter(category_id=cat)
    else:
        cat = None
    context = {
        'listings': listings,
        'category': cat,
    }
    return render(request, "auctions/index.html", context)


def listing_view(request, listing_id):
    """ Show the auction listing details and allow bidding on item if active """
    listing = Auction.objects.get(pk=listing_id)
    highest_bidder = Bid.objects.filter(listing_id=listing).filter(amount=listing.current_bid)
    comments = Comment.objects.filter(listing_id=listing.id)
    form = CommentForm()
    if len(highest_bidder) == 1:
        highest_bidder = highest_bidder.get()
    
    watched = False
    current_user_watched_items = request.user.watched.all()
    if listing in current_user_watched_items:
        watched = True
    
    context = {
        'listing': listing,
        'highest_bidder': highest_bidder,
        'comments': comments,
        'watched': watched,
        'form': form,
    }
    return render(request, 'auctions/listing.html', context)


def category_view(request):
    """ Display list of all categories with links to a filtered listing view that
    displays only listings of that category """
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'auctions/categories.html', context)


@login_required
def place_bid(request, listing_id):
    """ Handle bidding on listings """
    listing = Auction.objects.get(pk=listing_id)
    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            current_user = request.user
            if current_user.is_authenticated:
                bid_amount = form.cleaned_data["amount"]
                if bid_amount > listing.current_bid:
                    bid = Bid(amount=bid_amount, user_id=current_user, listing_id=listing)
                    bid.save() # Save the bid
                    listing.current_bid = bid_amount # Update to new highest bid amount
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", args=[listing_id]))
                return HttpResponseRedirect(reverse("place-bid", args=[listing_id]))
            else:
                return HttpResponseRedirect(reverse("login"))
    else:
        form = BiddingForm()

    context = {
        'listing': listing,
        'form': form,
    }
    return render(request, 'auctions/bidding.html', context)


@login_required
def post_comment(request, listing_id):
    """ Handle posting user comments on listings """
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            current_user = request.user
            if current_user.is_authenticated:
                comment_text = form.cleaned_data["comment"]
                comment = Comment(user_id=current_user, listing_id=Auction.objects.get(pk=listing_id),
                                  comment=comment_text)
                comment.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            else:
                return HttpResponseRedirect(reverse("login"))


@login_required
def watch_list(request):
    """ Display a user's watched items and allow deletion """
    current_user = request.user
    listings = current_user.watched.all()

    return render(request, 'auctions/watchlist.html', {'listings': listings})
    

@login_required
def watch_list_add(request, listing_id):
    """ Add an auction to current user's watchlist, then redirect """
    current_user = request.user
    listing = Auction.objects.get(pk=listing_id)
    current_user.watched.add(listing)

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


@login_required
def watch_list_rem(request, listing_id):
    """ Remove an auction to current user's watchlist, then redirect """
    current_user = request.user
    listing = Auction.objects.get(pk=listing_id)
    current_user.watched.remove(listing)

    return HttpResponseRedirect(reverse("watchlist"))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

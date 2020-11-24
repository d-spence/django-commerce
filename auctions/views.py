from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Comment, Category, Bid
from .forms import CommentForm, BiddingForm


def index(request, category=None, is_active=True):
    listings = Auction.objects.filter(active=True)
    if category is not None:
        listings = listings.filter(category_id=Category.objects.get(name=category))
    return render(request, "auctions/index.html", {'listings': listings})


def listing_view(request, listing_id):
    """ Show the auction listing details and allow bidding on item if active """
    listing = Auction.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing_id=listing.id)
    highest_bidder = Bid.objects.filter(listing_id=listing).filter(amount=listing.current_bid)
    if len(highest_bidder) == 1:
        highest_bidder = highest_bidder.get()
    form = CommentForm()

    context = {
        'listing': listing,
        'highest_bidder': highest_bidder,
        'comments': comments,
        'form': form,
    }
    return render(request, 'auctions/listing.html', context)


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
        

def category_view(request):
    """ Display list of all categories with links to a filtered listing view that
    displays only listings of that category """
    categories = Category.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'auctions/categories.html', context)


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

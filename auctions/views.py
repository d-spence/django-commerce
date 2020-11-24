from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Comment
from .forms import CommentForm


def index(request):
    listings = Auction.objects.filter(active=True)
    return render(request, "auctions/index.html", {'listings': listings})


def listing_view(request, listing_id):
    """ Show the auction listing details and allow bidding on item if active """
    listing = Auction.objects.get(pk=listing_id)
    comments = Comment.objects.filter(listing_id=listing.id)
    form = CommentForm()

    context = {
        'listing': listing,
        'comments': comments,
        'form': form,
    }
    return render(request, 'auctions/listing.html', context)


def post_comment(request, listing_id):
    """ Handle posting user comments on listings """
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = request.POST["comment"]
        

def category_view(request):
    pass


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

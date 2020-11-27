from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Comment, Category, Bid
from .forms import CommentForm, BiddingForm, ListingForm


def index(request, category=None, disp='active'):
    if disp == 'all':
        listings = Auction.objects.all()
    else:
        listings = Auction.objects.filter(active=True)

    if category is not None:
        cat = Category.objects.get(name=category)
        listings = listings.filter(category_id=cat)
    else:
        cat = None
    context = {
        'listings': listings,
        'category': cat,
        'disp': disp,
    }
    return render(request, "auctions/index.html", context)


def listing_view(request, listing_id):
    """ Show the auction listing details and allow bidding on item if active """
    listing = Auction.objects.get(pk=listing_id)
    highest_bidder = Bid.objects.filter(listing_id=listing).filter(amount=listing.current_bid)
    current_user = request.user
    comments = Comment.objects.filter(listing_id=listing.id)
    form = CommentForm()
    if len(highest_bidder) == 1:
        highest_bidder = highest_bidder.get()
    
    watched = False # Is the current user watching this listing?
    owner = False # Is the current user the owner of the listing?
    winner = False # Is the current user the listing winner?
    if current_user.is_authenticated:
        current_user_watched_items = current_user.watched.all()
        if listing in current_user_watched_items:
            watched = True
        current_user_listings = Auction.objects.filter(user_id=current_user)
        if listing in current_user_listings:
            owner = True
        current_user_bids = Bid.objects.filter(user_id=current_user)
        if highest_bidder in current_user_bids:
            winner = True
    
    context = {
        'listing': listing,
        'highest_bidder': highest_bidder,
        'comments': comments,
        'watched': watched,
        'owner': owner,
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
def create_listing(request):
    """ Allow signed-in users to create a new auction listing """
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data['title']
            category = form.cleaned_data['category_id']
            description = form.cleaned_data['description']
            starting_bid = form.cleaned_data['current_bid']
            image = form.files['image']
            new_listing = Auction(title=title, category_id=category,
                user_id=request.user, description=description,
                current_bid=starting_bid, image=image)
            new_listing.save()
            return HttpResponseRedirect(reverse("listing", args=[new_listing.id]))
        else:
            raise Http404("ListingForm POST data was not valid.")
    else:
        form = ListingForm()
        context = {
            'form': form,
        }
        return render(request, 'auctions/create_listing.html', context)


@login_required
def close_listing(request, listing_id):
    """ Close a listing if logged in user is the one who created it """
    listing = Auction.objects.get(pk=listing_id)
    if request.user == listing.user_id:
        listing.active = False
        listing.save()
        return HttpResponseRedirect(reverse("listing", args=[listing.id]))
    else:
        raise Http404("You are not authorized to close this listing.")

@login_required
def close_listing_confirm(request, listing_id):
    """ Confirm with the user before closing a listing """
    listing = Auction.objects.get(pk=listing_id)
    if request.user == listing.user_id:
        return render(request, 'auctions/confirm_close.html', {'listing': listing})
    else:
        raise Http404("You are not authorized to close this listing.")



@login_required
def place_bid(request, listing_id):
    """ Handle bidding on listings """
    listing = Auction.objects.get(pk=listing_id)
    if request.method == "POST":
        form = BiddingForm(request.POST)
        if form.is_valid():
            current_user = request.user
            bid_amount = form.cleaned_data["amount"]
            if bid_amount > listing.current_bid:
                bid = Bid(amount=bid_amount, user_id=current_user, listing_id=listing)
                bid.save() # Save the bid
                listing.current_bid = bid_amount # Update to new highest bid amount
                listing.save()
                return HttpResponseRedirect(reverse("listing", args=[listing_id]))
            else:
                messages.add_message(request, messages.INFO, 
                    "Your bid was too low. Your bid must be greater than the current highest bid.")
                return HttpResponseRedirect(reverse("place-bid", args=[listing_id]))
        else:
            raise Http404("BiddingForm POST data was not valid.")
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
            comment_text = form.cleaned_data["comment"]
            comment = Comment(user_id=current_user, listing_id=Auction.objects.get(pk=listing_id),
                                comment=comment_text)
            comment.save()
        else:
            raise Http404("CommentForm POST data was not valid.")

    return HttpResponseRedirect(reverse("listing", args=[listing_id]))


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

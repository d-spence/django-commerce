from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db import models


class User(AbstractUser):
    watched = models.ManyToManyField(
        'Auction', 
        blank=True, 
        related_name="watched_by"
    )

    def __str__(self):
        return f"{self.username} ({self.email})"


# Additional models
class Category(models.Model):
    """ Category model; must be a unique name """
    name = models.CharField(max_length=64, unique=True)
    
    def __str__(self):
        return f"{self.name}"


class Auction(models.Model):
    """ Primary data model for site auctions """
    title = models.CharField(max_length=128)
    active = models.BooleanField(default=True)
    date = models.DateTimeField(default=timezone.now)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField()
    current_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(default='default.png', upload_to='auction_imgs')

    def __str__(self):
        return f"{self.title} ({self.category_id}) listed by {self.user_id}"


class Comment(models.Model):
    comment = models.CharField(max_length=256)
    date = models.DateTimeField(default=timezone.now)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing_id.title}: {self.user_id.username}: {self.comment}"


class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_id = models.ForeignKey(Auction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.listing_id.title}: {self.user_id.username}: ${self.amount}"

from django.contrib import admin

from .models import User, Category, Auction, Comment, Bid


class AuctionAdmin(admin.ModelAdmin):
    """ customized admin options for Auction model """
    fieldsets = [
        ('Auction (Primary)', {'fields': ['title', 'category_id', 'current_bid', 'description']}),
        ('Auction (Secondary)', {'fields': ['user_id', 'date'],
                                 'classes': ['collapse']}),
        ('Image Details', {'fields': ['image']}),
    ]

    list_display = ('title', 'id', 'category_id', 'date', 'active')
    list_filter = ['date', 'category_id']
    list_per_page = 20
    search_fields = ['title']


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Comment)
admin.site.register(Bid)

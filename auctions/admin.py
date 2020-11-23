from django.contrib import admin

from .models import User, Category, Auction, Comment, Bid


class AuctionAdmin(admin.ModelAdmin):
    """ customized admin options for Auction model """
    list_display = ('title', 'id', 'user_id', 'category_id', 'date', 'active')
    list_filter = ['date']
    list_per_page = 20
    search_fields = ['title']


admin.site.register(User)
admin.site.register(Category)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Comment)
admin.site.register(Bid)

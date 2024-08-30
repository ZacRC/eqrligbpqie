from django.contrib import admin
from .models import User, ForumPost, ForumReply, Announcement, CommunityNews, Listing, MarketplaceNotification

admin.site.register(User)
admin.site.register(ForumPost)
admin.site.register(ForumReply)
admin.site.register(Announcement)
admin.site.register(CommunityNews)
admin.site.register(Listing)
admin.site.register(MarketplaceNotification)
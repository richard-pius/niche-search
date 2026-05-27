from django.contrib import admin
from niche_search.admin import custom_admin_site
from .models import SearchResult, UserBookmark, UserProfile

@admin.register(SearchResult, site=custom_admin_site)
class SearchResultAdmin(admin.ModelAdmin):
    list_display = ['title', 'source_site', 'rank', 'created_at']
    search_fields = ['title', 'description']

@admin.register(UserBookmark, site=custom_admin_site)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'result', 'created_at']

@admin.register(UserProfile, site=custom_admin_site)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'profile_picture']
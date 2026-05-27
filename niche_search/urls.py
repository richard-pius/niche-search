from django.urls import path, include
from niche_search.admin import custom_admin_site

urlpatterns = [
    path('admin/', custom_admin_site.urls),            # custom admin
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('search.urls')),
]
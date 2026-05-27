from django.urls import path, include   # include was missing
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks'),
    path('bookmark/add/<int:result_id>/', views.bookmark_add, name='bookmark_add'),
    path('bookmark/remove/<int:result_id>/', views.bookmark_remove, name='bookmark_remove'),
    path('profile/', views.profile, name='profile'),
]
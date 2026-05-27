from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django_ratelimit.decorators import ratelimit
from .models import SearchResult, UserBookmark
from .forms import SearchForm, UserRegistrationForm, ProfileUpdateForm
from django.core.paginator import Paginator
from django.db.models import Q
from .models import SearchResult
from .ranking import calculate_relevance

# just adding a comment.

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def home(request):
    form = SearchForm(request.GET)
    results = SearchResult.objects.all()
    query = request.GET.get('q', '')
    if query:
        results = results.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    paginator = Paginator(results, 10)
    page_number = request.GET.get('page')
    results_page = paginator.get_page(page_number)
    if request.user.is_authenticated:
        bookmarked_ids = set(
            UserBookmark.objects.filter(user=request.user, result__in=results_page)
            .values_list('result_id', flat=True)
        )
        for r in results_page:
            r.is_bookmarked = r.id in bookmarked_ids
    return render(request, 'search/home.html', {
        'form': form, 'results': results_page, 'query': query
    })

@login_required
def bookmark_add(request, result_id):
    result = get_object_or_404(SearchResult, pk=result_id)
    _, created = UserBookmark.objects.get_or_create(user=request.user, result=result)
    if created:
        messages.success(request, 'Bookmark added.')
    else:
        messages.info(request, 'Already bookmarked.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def bookmark_remove(request, result_id):
    result = get_object_or_404(SearchResult, pk=result_id)
    UserBookmark.objects.filter(user=request.user, result=result).delete()
    messages.success(request, 'Bookmark removed.')
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def bookmarks_list(request):
    bookmarks = UserBookmark.objects.filter(user=request.user).select_related('result')
    return render(request, 'search/bookmarks.html', {'bookmarks': bookmarks})

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES,
                                 instance=request.user.profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user.profile, user=request.user)
    return render(request, 'search/profile.html', {'form': form})


def home(request):
    form = SearchForm(request.GET)
    query = request.GET.get('q', '')
    
    if query:
        # Filter candidates
        results_qs = SearchResult.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
        # Convert to list (safe for 1500 items)
        results_list = list(results_qs)

        # Attach relevance score to each result
        for r in results_list:
            static_boost = getattr(r, 'rank', 0.0)   # use rank field if exists
            r.relevance_score = calculate_relevance(query, r, static_boost=static_boost)

        # Sort descending by relevance
        results_list.sort(key=lambda x: x.relevance_score, reverse=True)
    else:
        # No query → sort by static rank (if exists) or date
        results_list = SearchResult.objects.order_by('-rank', '-created_at')

    # Paginate (10 per page)
    paginator = Paginator(results_list, 10)
    page_number = request.GET.get('page')
    results_page = paginator.get_page(page_number)

    # Bookmark info for logged‑in users
    if request.user.is_authenticated:
        bookmarked_ids = set(
            UserBookmark.objects.filter(user=request.user, result__in=results_page)
            .values_list('result_id', flat=True)
        )
        for r in results_page:
            r.is_bookmarked = r.id in bookmarked_ids

    return render(request, 'search/home.html', {
        'form': form,
        'results': results_page,
        'query': query,
    })
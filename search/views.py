from django.db.models import Value, Case, When, F, IntegerField, Count, Q
from django.http import JsonResponse
from accounts.models import Profile
from post.models import Post, Comment
from django.db.models.functions import Length
from django.views.decorators import http
import os

def search(request):
    query = request.GET.get('query', '')
    
    # Search profiles
    profiles = Profile.objects.annotate(
        exact_match=Case(
            When(user__username__iexact=query, then=Value(1)),
            When(user__first_name__iexact=query, then=Value(2)),
            When(user__last_name__iexact=query, then=Value(3)),
            default=Value(0),
            output_field=IntegerField()
        ),
        partial_match=Case(
            When(user__username__icontains=query, then=Value(1)),
            When(user__first_name__icontains=query, then=Value(2)),
            When(user__last_name__icontains=query, then=Value(3)),
            default=Value(0),
            output_field=IntegerField()
        ),
        total_match=F('exact_match') + F('partial_match'),
        match=Case(
            When(exact_match=1, then=Value(100)),
            When(partial_match=1, then=Value(50)),
            default=Value(0),
            output_field=IntegerField()
        ) + Length('user__username')
    ).order_by('-total_match')
    
    # Search posts
    post_conditions = Q(caption__icontains=query) | Q(hash_tag__icontains=query)
    post_counts = Post.objects.filter(post_conditions).values('hash_tag').annotate(total_posts=Count('id'))
    
    # Serialize the search results
    search_results = []
    
    # Add profiles to search results
    for profile in profiles:
        search_results.append({
            'type': 'profile',
            'username': profile.user.username,
            'first_name': profile.user.first_name,
            'last_name': profile.user.last_name,
            'id': profile.user.id,
            'profile_pic': profile.profile_img.url,
            'match_score': profile.match,
        })
    
    # Add posts to search results
    for post_count in post_counts:
        search_results.append({
            'type': 'post',
            'hashtag': post_count['hash_tag'],
            'total_posts': post_count['total_posts'],
        })
    
    return JsonResponse({'results': search_results})

@http.require_GET
def search_by_hashtag(request, hashtag):
    # Search posts
    post_conditions = Q(hash_tag__icontains=hashtag)
    posts = Post.objects.filter(post_conditions)
    
    print('posts: ', posts)
    
    # Serialize the search results
    search_results = []
    
    # Add posts to search results
    for post in posts:
        search_results.append({
            'post_id': post.id,
            'likes_count': post.likes.count(),
            'comments_count': Comment.objects.filter(post=post).count(),
            'file_name': post.file.url,
        })
    
    return JsonResponse({'posts': search_results})

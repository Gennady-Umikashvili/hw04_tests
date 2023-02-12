from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Group, Post, User

NUMBERS_OF_POSTS = 10


def get_page_content(post_list, page_number):
    paginator = Paginator(post_list, NUMBERS_OF_POSTS)
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.all()
    page_obj = get_page_content(post_list,
                                request.GET.get('page'))
    return render(request, 'posts/index.html',
                  context={'page_obj': page_obj})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page_content(posts,
                                request.GET.get('page'))
    return render(request, 'posts/group_list.html',
                  context={'group': group,
                           'page_obj': page_obj})


def profile(request, username):
    user = get_object_or_404(User, username=username)
    # posts = Post.objects.filter(author=user)
    posts = user.posts.all()
    page_obj = get_page_content(posts,
                                request.GET.get('page'))
    return render(request, 'posts/profile.html',
                  context={'author': user,
                           'page_obj': page_obj})


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(
        request,
        'posts/post_detail.html', {'post': post})


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "posts/create_post.html",
                      context={"form": form})
    form.instance.author = request.user
    form.save()
    return redirect("posts:profile", request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None,
                    instance=post)
    if post.author != request.user:
        return redirect("posts:post_detail", post_id)
    if form.is_valid():
        form.save()
        return redirect("posts:post_detail", post_id)

    return render(request, "posts/create_post.html",
                  context={'form': form,
                           'is_edit': True})

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView)
from recipeblog.models import Post, Comment, Ingredient, Like, Rate
from recipeblog.forms import PostForm, CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError

# function based views use decorators | class based views use mixins
# Create your views here.


class AboutView(TemplateView):
    template_name = 'about.html'


class PostListView(ListView):
    model = Post

    # sql query filter  base on condition

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('created_date')


class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    redirect_field_name = 'recipeblog/post_detail.html'

    form_class = PostForm
    model = Post


class PostUpdateView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    redirect_field_name = 'recipeblog/post_detail.html'

    form_class = PostForm
    model = Post


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


class DraftListView(LoginRequiredMixin, ListView):
    login_url = '/login/'
    redirect_field_name = 'recipeblog/post_list.html'
    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')



@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = get_object_or_404(User, pk=request.user.id)
    post.publish(user)
    return redirect('post_detail', pk=pk)

@login_required
def post_like(request,pk):
    post = get_object_or_404(Post, pk=pk)
    user = get_object_or_404(User, pk=request.user.id)

    # Like instance created
    try:
        Like.objects.create(user=user, post=post)
    except IntegrityError:
        return redirect('post_detail', pk=pk)
    return redirect('post_detail', pk=pk)

@login_required
def post_rate(request,pk):
    post = get_object_or_404(Post, pk=pk)
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == "POST":
        try:
            point = request.POST.get['rate_point']
        except MultiValueDictKeyError:
            point = 0


    Rate.objects.update_or_create(user=user, post=post, rate_point=point)

    return redirect('post_detail', pk=pk)


####### COMMENT #######
@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'recipeblog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)




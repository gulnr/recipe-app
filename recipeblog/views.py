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
from django.db.models import Q
from django.db.models import Count
from django.utils.datastructures import MultiValueDictKeyError

# function based views use decorators | class based views use mixins
# Create your views here.


class PostListView(ListView):
    model = Post
    most_used_ingredients = Post.objects.all().values(
        'ingredients__ingredient_name').annotate(
            total=Count('ingredients')).order_by('-total')[:5]

    # sql query filter  base on condition
    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('created_date')

    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['most_used_ingredients'] = self.most_used_ingredients
        return context


class SearchPostListView(ListView):
    model = Post
    most_used_ingredients = Post.objects.all().values(
        'ingredients__ingredient_name').annotate(
            total=Count('ingredients')).order_by('-total')[:5]

    def get_queryset(self):
        query_list = [item.strip() for item in self.request.GET.get("query").split()]
        post_ids = set()
        for s_item in query_list:
            for ing in Ingredient.objects.filter(ingredient_name__contains=s_item):
                post_ids.add(ing.id)
        result_list = Post.objects.filter(
            ingredients__in=list(post_ids)).order_by("created_time")

        for s_item in query_list:
            result_list2 = Post.objects.filter(
                Q(title__contains=s_item)
                | Q(description__contains=s_item)).order_by('created_date')
            result_list = result_list | result_list2

            return result_list.distinct()

    def get_context_data(self, **kwargs):
        context = super(SearchPostListView, self).get_context_data(**kwargs)
        context['most_used_ingredients'] = self.most_used_ingredients
        return context


class TopIngredientView(ListView):
    model = Post

    most_used_ingredients = Post.objects.all().values(
        'ingredients__ingredient_name').annotate(
            total=Count('ingredients')).order_by('-total')[:5]

    def get_queryset(self, **kwarg):
        s_item = self.kwargs.get('item_val', None)
        post_ids=set()
        for ing in Ingredient.objects.filter(ingredient_name__contains=s_item):
                post_ids.add(ing.id)
        result_list = Post.objects.filter(ingredients__in=list(post_ids)).order_by("created_date")

        return result_list

    def get_context_data(self, **kwargs):
        context = super(TopIngredientView, self).get_context_data(**kwargs)
        context['most_used_ingredients'] = self.most_used_ingredients
        return context



class PostDetailView(DetailView):
    model = Post


class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = '/login/'
    form_class = PostForm
    model = Post

    # def post(self, request, *args, **kwargs):
    #     form = PostForm(request.POST)
    #     if form.is_valid():
    #         post_obj = form.save(commit=False)
    #         post_obj.author = self.get_object_or_404(User, pk=request.user.id)
    #         post_obj.save()
    #         return redirect('post_detail.html', post_obj.pk)
    #     return render(request, 'post_form.html', {'form': form})


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

    most_used_ingredients = Post.objects.all().values(
        'ingredients__ingredient_name').annotate(
            total=Count('ingredients')).order_by('-total')[:5]

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('created_date')

    def get_context_data(self, **kwargs):
        context = super(DraftListView, self).get_context_data(**kwargs)
        context['most_used_ingredients'] = self.most_used_ingredients
        return context


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
        point = request.POST.get('point')
        try:
            Rate.objects.create(user=user, post=post, rate_point=point)

        except IntegrityError:
            Rate.objects.filter(user=user, post=post).update(rate_point=point)

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




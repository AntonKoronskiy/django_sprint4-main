from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category, Comment
from django.utils.timezone import now
from django.core.paginator import Paginator

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView
from .forms import CreatePostForm, CreateCommentForm
from .forms import RegistrationForm, EditProfileForm
from .models import Post
from django.urls import reverse
from django.db.models import Count


class IndexView(ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments'))


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        self.category = get_object_or_404(
            Category,
            is_published=True,
            slug=category_slug
        )
        return Post.objects.filter(
            pub_date__lte=now(),
            is_published=True,
            category=self.category
        ).order_by('-pub_date').annotate(
            comment_count=Count('comments'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['comments'] = post.comments.prefetch_related('author').all()
        context['form'] = CreateCommentForm()
        return context

    def get_object(self, queryset=None):
        post = get_object_or_404(Post, pk=self.kwargs.get(self.pk_url_kwarg))
        if self.request.user == post.author:
            return post
        return get_object_or_404(
            Post.objects.filter(
                pub_date__lte=now(),
                is_published=True,
                category__is_published=True).order_by('-pub_date').annotate(
                    comment_count=Count('comments')),
            pk=self.kwargs.get(self.pk_url_kwarg))


def registration(request):
    template_name = 'registration/registration_form.html'
    form = RegistrationForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blog:index')

    return render(request, template_name, {'form': form})


def profile(request, username):
    user = get_object_or_404(User, username=username)

    if request.user == user:
        posts = Post.objects.filter(
            author=user).order_by('-pub_date').annotate(
                comment_count=Count('comments'))
    else:
        posts = Post.objects.filter(
            author=user,
            is_published=True).order_by('-pub_date').annotate(
                comment_count=Count('comments'))

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'profile': user,
        'page_obj': page_obj,
    }

    return render(request, 'blog/profile.html', context)


@login_required
def edit_profile(request):
    template_name = 'blog/user.html'

    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user)
    else:
        form = EditProfileForm(instance=request.user)

    return render(request, template_name, {'form': form})


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = 'blog/user.html'
    model = User
    form_class = EditProfileForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


@login_required
def posts_create(request):
    template_name = 'blog/create.html'

    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = CreatePostForm()

    context = {'form': form}

    return render(request, template_name, context)


class CreatePostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = CreatePostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


def post_edit(request, post_id):
    template_name = 'blog/create.html'

    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CreatePostForm(instance=post)

    context = {'form': form}

    return render(request, template_name, context)


@login_required
def comments_post(request, post_id):
    template_name = 'blog/comment.html'
    form = CreateCommentForm(request.POST or None)
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all().order_by('created_at')

    if request.method == 'POST':
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('blog:post_detail', post_id=post.id)

    context = {'form': form,
               'post': post,
               'comments': comments}

    return render(request, template_name, context)


def comment_edit(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post.id)

    if request.method == 'POST':
        form = CreateCommentForm(request.POST, request.FILES, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post.id)
    else:
        form = CreateCommentForm(instance=comment)

    context = {
        'form': form,
        'comment': comment}

    return render(request, template_name, context)


@login_required
def post_delete(request, post_id):
    template_name = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        post.delete()
        return redirect('blog:profile', request.user.username)

    context = {'form': post,
               'is_deleting': True}

    return render(request, template_name, context)


def comment_delete(request, post_id, comment_id):
    template_name = 'blog/comment.html'
    post = get_object_or_404(Post, id=post_id)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user != comment.author:
        return redirect('blog:post_detail', post_id=post_id)

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post.id)

    context = {'post': post,
               'comment': comment,
               'is_deleting': True}

    return render(request, template_name, context)

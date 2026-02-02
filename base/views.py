from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from .models import LFGPost, Message, GAME_MODES, RANKS, ROLES
from .forms import LFGPostForm

# Create your views here.
def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist.')
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist.')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration.')

    return render(request, 'base/login_register.html', {'form': form})

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    posts = LFGPost.objects.filter(
        Q(game_mode__icontains=q) |
        Q(title__icontains=q) |
        Q(description__icontains=q) |
        Q(host_rank__icontains=q) |
        Q(min_rank__icontains=q) |
        Q(host_role__icontains=q) |
        Q(looking_for_role__icontains=q)
    )
    post_count = posts.count()

    context = {
        'posts': posts,
        'post_count': post_count,
        'game_modes': GAME_MODES,
        'ranks': RANKS,
        'roles': ROLES,
    }
    return render(request, 'base/home.html', context)

def lfgpost(request, pk):
    post = LFGPost.objects.get(id=pk)
    title = post.title
    game_mode = post.game_mode
    host_role = post.host_role
    looking_for_role = post.looking_for_role
    host_rank = post.host_rank
    min_rank = post.min_rank
    description = post.description
    
    context = {'post': post, 'title': title, 'game_mode': game_mode, 'host_role': host_role , 'looking_for_role': looking_for_role, 'host_rank': host_rank, 'min_rank': min_rank , 'description': description,}
    return render(request, "base/lfgpost.html", context)

@login_required(login_url='login')
def create_lfgpost(request):
    form = LFGPostForm()

    if request.method == 'POST':
        form = LFGPostForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/post_form.html', context)

@login_required(login_url='login')
def updatePost(request, pk):
    post = LFGPost.objects.get(id=pk)
    form = LFGPostForm(instance=post)

    if request.user != post.host:
        return HttpResponse('You are not allowed here')

    if request.method == 'POST':
        form = LFGPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/post_form.html', context)

@login_required(login_url='login')
def deletePost(request, pk):
    post = LFGPost.objects.get(id=pk)

    if request.user != post.host:
        return HttpResponse("You don't have the permision to do this.")
    
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': post})

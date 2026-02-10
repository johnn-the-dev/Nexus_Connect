from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib import messages
from .models import LFGPost, Message, GAME_MODES, TIERS, ROLES, REGIONS
from .forms import LFGPostForm
from .riot_services import get_summoner_data, get_profile_stats, update_profile

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
    posts = LFGPost.objects.all()
    mode_filter = request.GET.get('mode')
    tier_filter = request.GET.get('tier')
    role_filter = request.GET.get('role')
    region_filter = request.GET.get('region')

    if q:
        posts = posts.filter(
            Q(title__icontains=q)|
            Q(description__icontains=q)
        )

    if mode_filter:
        posts = posts.filter(game_mode=mode_filter)

    if tier_filter:
        posts = posts.filter(min_tier=tier_filter)
    
    if role_filter:
        posts = posts.filter(looking_for_role=role_filter)

    if region_filter:
        posts = posts.filter(region=region_filter)
    
    post_count = posts.count()

    context = {
        'posts': posts,
        'post_count': post_count,
        'game_modes': GAME_MODES,
        'tiers': TIERS,
        'roles': ROLES,
        'regions': REGIONS,
    }

    return render(request, 'base/home.html', context)

def lfgpost(request, pk):
    post = LFGPost.objects.get(id=pk)
    title = post.title
    game_mode = post.game_mode
    region = post.region
    host_role = post.host_role
    looking_for_role = post.looking_for_role
    host_tier = post.host_tier
    min_tier = post.min_tier
    description = post.description
    participants = post.participants
    participants_count = participants.count()
    
    if request.method == 'POST':
        message_body = request.POST.get('body')
        
        Message.objects.create(
            user=request.user,
            chat_room=post,
            body=message_body
        )

        return redirect('lfgpost', pk=pk) 

    post_messages = post.messages.all()

    context = {'post': post, 'title': title, 'game_mode': game_mode, 'region': region , 'host_role': host_role , 'looking_for_role': looking_for_role, 'host_tier': host_tier,
               'min_tier': min_tier , 'description': description, 'participants': participants, 'participants_count': participants_count, 'messages': post_messages}

    return render(request, "base/lfgpost.html", context)

@login_required(login_url='login')
def joinPost(request, pk):
    post = LFGPost.objects.get(id=pk)

    if request.user != post.host:
        post.participants.add(request.user)

    return redirect('lfgpost', pk=pk)

@login_required(login_url='login')
def leavePost(request, pk):
    post = LFGPost.objects.get(id=pk)

    if request.user in post.participants.all():
        post.participants.remove(request.user)
    
    if request.user == post.host:
        post.delete()
        return redirect('home')

    if post.participants.count() == 0:
        post.delete()
        return redirect('home')

    return redirect('home')

@login_required(login_url='login')
def create_lfgpost(request):
    form = LFGPostForm()

    if request.method == 'POST':
        form = LFGPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.host = request.user
            post.save()
            post.participants.add(request.user)

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

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    posts = user.lfgpost_set.all()
    

    mode_filter = request.GET.get('mode')
    tier_filter = request.GET.get('tier')
    role_filter = request.GET.get('role')
    region_filter = request.GET.get('region')

    if mode_filter:
        posts = posts.filter(game_mode=mode_filter)
    
    if tier_filter:
        posts = posts.filter(min_tier=tier_filter)
    
    if role_filter:
        posts = posts.filter(looking_for_role=role_filter)

    if region_filter:
        posts = posts.filter(region=region_filter)

    post_count = posts.count()
    riot_stats = None

    if hasattr(user, "profile"):
        profile = user.profile
        

        if profile.puuid:
            try:
                update_profile(profile)
            except Exception as e:
                print(f"Error when checking username: {e}")
            
            try:
                riot_stats = get_profile_stats(profile.puuid, profile.platform)
            except Exception as e:
                print(f"Error when downloading data: {e}")

    context = {'user': user,
               'posts': posts,
               'post_count': post_count,
               "riot_stats": riot_stats,
               'game_modes': GAME_MODES,
               'tiers': TIERS,
               'roles': ROLES,
               'regions': REGIONS
            }
    
    return render(request, 'base/profile.html', context)

def riot_information(request):
    context = {}

    if request.method == "POST":
        game_name = request.POST.get("game_name")
        tag_line = request.POST.get("tag_line")
        platform = request.POST.get("platform")

        data = get_summoner_data(game_name, tag_line, platform)
        context["player_data"] = data

    return render(request, "lol_stats.html", context)

@login_required(login_url='login')
def link_riot_account(request):
    if request.method == "POST":
        game_name = request.POST.get("game_name")
        tag_line = request.POST.get("tag_line")
        platform = request.POST.get("platform")

        data = get_summoner_data(game_name, tag_line, platform)

        if data and "puuid" in data:
            profile = request.user.profile
            profile.riot_game_name = data["game_name"]
            profile.riot_tag_line = data["tag_line"]
            profile.platform = platform
            profile.puuid = data["puuid"]
            profile.icon_id = data.get("icon_id")
            
            profile.save()
            messages.success(request, f"Account {game_name}#{tag_line} was successfully connected.")
        else:
            messages.error(request, "Account wasn't found.")
    
    return redirect('user-profile', pk=request.user.id)

@login_required(login_url="login")
def unlink_riot_account(request):
    if request.method == "POST":
        profile = request.user.profile
        profile.riot_game_name = None
        profile.riot_tag_line = None
        profile.platform = None
        profile.puuid = None
        profile.icon_id = 29
        
        profile.save()
        messages.info(request, "Riot účet byl odpojen.")

    return redirect("user-profile", pk=request.user.id)
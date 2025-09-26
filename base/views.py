from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm, ProfileForm

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try: 
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist')
            return redirect('login')

        
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Username OR password is invalid')
            return redirect('login')
        else:
            login(request, user)
            return redirect('home')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # commit = False is so that can access user object right away for cleaning of data
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    # methods for ModelName.objects include .all() to return all
    # get to get specific object
    # filter to filter and returns objects matching condition e.g. WHERE
    # exclude to filter out and return objects not matching condition e.g. WHERE NOT
    topics = Topic.objects.all()[:5]
    room_count = rooms.count() # Faster than python len
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q)).order_by('-created')[:10]
    context = {'rooms': rooms, 
               'topics': topics, 
               'room_count': room_count, 
               'room_messages': room_messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    roomMessages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    # message_set -> modelname_set is to access children 

    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        # So that they are dynamically added once they comment
        return redirect('room', pk=room.id)
        # To avoid POST from messing up functionality redirect fully reloads
    context = {'room': room, 'roomMessages': roomMessages, 'participants': participants}
    return render(request, 'base/room.html', context)

# Serves as a middleware to require login
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm();
    topics = Topic.objects.all();
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )
        return redirect('home')
        # ModelForm helps to handle all the saving
    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    # pk is like the params.id
    room = Room.objects.get(id=pk)
    topics = Topic.objects.all();
    form = RoomForm(instance=room)
    # To pass in initial room values

    if request.user != room.host:
        return HttpResponseForbidden("You are not allowed here!")

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
    context = {'form': form, 'topics': topics, "room": room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponseForbidden("You are not allowed here!")
    
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponseForbidden("You are not allowed here!")
    
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, "topics": topics, "room_messages": room_messages}
    return render(request, 'base/profile.html', context)
    
def topicsPage(request): 
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all().order_by('-created')[:5]
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('user-profile', pk=user.id)
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, "base/update-user.html", {
        "user_form": user_form,
        "profile_form": profile_form
    })
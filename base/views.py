from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm, ProfileForm
from django.http import JsonResponse

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = (request.POST.get('username') or '').lower().strip()
        password = (request.POST.get('password') or '')

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist.')
            return redirect('login')

        if not user_obj.is_active:
            messages.error(request, 'This account is inactive.')
            return redirect('login')

        # Check password explicitly so we can show a specific message
        if not user_obj.check_password(password):
            messages.error(request, 'Incorrect password.')
            return redirect('login')

        # If we reached here, credentials are correct
        user = authenticate(request, username=username, password=password)
        if user is None:
            # Extremely rare path (custom backend quirks)
            messages.error(request, 'Authentication failed due to a server configuration issue.')
            return redirect('login')

        login(request, user)
        return redirect('home')

    return render(request, 'base/login_register.html', {'page': page})

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerUser(request):
    page = 'register'
    form = UserCreationForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            # push all form errors into the messages framework
            for field, errors in form.errors.items():
                label = "Password" if field == "password2" else field.capitalize()
                for e in errors:
                    messages.error(request, f"{label}: {e}")

    return render(request, 'base/login_register.html', {
        'page': page,
        'form': form,
    })

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
    roomMessages = room.message_set.all().order_by('-created')[:10]
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
    context = {'room': room, 
               'roomMessages': roomMessages, 
               'participants': participants,
               'initial_loaded': len(roomMessages),
               'page_size': 10,
               }
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
    room_messages = Message.objects.all().order_by('-created')[:4]
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

def room_messages_json(request, pk):
    try:
        offset = int(request.GET.get("offset", 0))
        limit = int(request.GET.get("limit", 10))
        limit = max(1, min(limit, 100))
    except ValueError:
        offset, limit = 0, 10

    qs = (Message.objects
          .filter(room_id=pk)
          .select_related("user__profile")
          .order_by("-created"))

    total = qs.count()
    items = list(qs[offset:offset+limit])

    data = []
    for m in items:
        img = getattr(getattr(m.user, "profile", None), "profile_img", None)
        data.append({
            "id": m.id,
            "user": m.user_id,
            "username": m.user.username,
            "body": m.body,
            "created": m.created.isoformat(),
            "profile_img": (img.url if img else None),
        })

    return JsonResponse({
        "messages": data,
        "total": total,
        "offset": offset,
        "limit": limit,
        "has_more": (offset + len(items) < total),
    })
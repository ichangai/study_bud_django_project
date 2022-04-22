from django.shortcuts import render, redirect
# for displaying flash messaging
from django.contrib import messages
# decorators for restricting pages to certain users
from django.contrib.auth.decorators import login_required
# import a lib to help with search
from django.db.models import Q
# for authenticating a user
from django.contrib.auth import authenticate, login, logout
# django register form
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
# this is where you import all your models
from .models import Room, Topic, Message
#this is a model class to import forms
from .forms import RoomForm, UserForm
# model for users
from django.contrib.auth.models import User




# Create your views here.

def loginPage(request):
    page = 'login'
    # restricting a user from re-logging in/sign in again
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exists')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # add session in db and browser
            login(request, user)
            # once user is logged in, redirect them to home
            return redirect('home')
        else:
            messages.error(request, 'Username or Password does not exists')

    context = {'page': page}
    return render(request, 'base/login_reg.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # the reason for putting commit false, we want to validate user's data  and ensure we save data as valid info(cleaning data)
            user.username = user.username.lower()
            user.save()
            # if the user is registered, we want to automatically sign in them.
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during the registration')

    return render(request, 'base/login_reg.html', {'form': form})


def home(request):
    # this is query parameters
    q = request.GET.get('q') if request.GET.get('q') != None else ' '
    # filter is used to find specific data searched by users
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) | 
        Q(description__icontains=q)
    )
    topics = Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    content = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages
    }

    return render(request, 'base/home.html', content)


def room(request, pk):
    room = Room.objects.get(id=pk)
    # room has many messages(children), so the message_set is used to call the relationship and display the child model
    room_messages = room.message_set.all()
    # importing participants
    participants = room.participants.all()
    # posting a comment
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        # we can add participants
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {
        'room': room,
        'room_messages': room_messages,
        'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    # we are getting all the rooms related to user
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        'user': user,
        'rooms': rooms,
        'room_messages': room_messages,
        'topics': topics
    }
    return render(request, 'base/profile.html', context)

# an authenticated user can add a room


@login_required(login_url='login')
# create room form
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        # capturing data
        topic_name = request.POST.get('topic')
        # get or create is used to check if an object already exists. If it isn't, its created
        topic, created = Topic.objects.get_or_create(name=topic_name)
        # create an object
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )

        # to return submitted data
        # print(request.POST)

        # form = RoomForm(request.POST)
        # checking if the form is valid
        # =======Model Form=======
        # if form.is_valid():
        # saving the form
        # room = form.save(commit = False)
        # automatically make the user the host
        # room.host = request.user
        # room.save()
        # =======end of Model Form======

        # redirecting the user to home
        return redirect('home')
       # rendering the form inside of the template
    context = {
        'form': form,
        'topics': topics
    }
    return render(request, 'base/room_form.html', context)

# an authenticated user/host can  update a room


@login_required(login_url='login')
# updating the room (passing in the request and the pk(primary key))
def updateRoom(request, pk):
    # to ensure we are getting the right room, we check if the id = pk
    room = Room.objects.get(id=pk)
    # this will ensure that the form field will be populated with the corresponding data
    form = RoomForm(instance=room)
    # restrict a host from editing another host's room
    topics = Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        # capturing data
        topic_name = request.POST.get('topic')
        # get or create is used to check if an object already exists. If it isn't, its created
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = request.POST.get('topic')
        room.description = request.POST.get('description')
        room.save()
        #model form for updating
        #form = RoomForm(request.POST, instance=room)
        #if form.is_valid():
        #form.save()
        return redirect('home')

    context = {
        'form': form,
        'topics': topics,
        'room': room,
        'topic': topic
    }
    return render(request, 'base/room_form.html', context)

# an authenticated user/host can delete a room


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    # restrict a host from editing another host's room
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})

# an authenticated user can delete a message


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    # restrict a host from editing another host's room
    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    context = {
        'form' : form
    }

    if request.method == 'POST':
        form = UserForm(request.POST, instance = user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render (request, 'base/update-user.html', context)


def topicsPage(request):
    # this is query parameters
    # q = request.GET.get('q') if request.GET.get('q') != None else ' '
    topics = Topic.objects.filter()
    context = {
        'topics': topics
    }
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html', {'room_messages' : room_messages})
from django.urls import path
from . import views

urlpatterns = [
    #login routes
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),    
    path('register/', views.registerUser, name="register"),

    #home routes
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    #room routes
    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    #message routes
     path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),
     path('update-user/', views.updateUser, name="update-user"),
    #Topics
     path('topics/', views.topicsPage, name="topics"),
    #activity
     path('activity/', views.activityPage, name="activity"),

]
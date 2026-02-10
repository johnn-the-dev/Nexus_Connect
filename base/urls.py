from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('post/<str:pk>/', views.lfgpost, name='lfgpost'),
    path('join-room/<str:pk>/', views.joinPost, name='join-room'),
    path('leave-room/<str:pk>/', views.leavePost, name='leave-room'),
    path('create-post/', views.create_lfgpost, name="create-post"),
    path('update-post/<str:pk>', views.updatePost, name="update-post"),
    path('delete-post/<str:pk>', views.deletePost, name='delete-post'),
    path('profile/<str:pk>', views.userProfile, name="user-profile"),
    path("link-riot/", views.link_riot_account, name="link-riot"),
    path("unlink-riot/", views.unlink_riot_account, name="unlink-riot"),
]

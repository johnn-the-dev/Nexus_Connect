from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.loginPage, name='login'),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('post/<str:pk>/', views.lfgpost, name='lfgpost'),
    path('create-post/', views.create_lfgpost, name="create-post"),
    path('update-post/<str:pk>', views.updatePost, name="update-post"),
    path('delete-post/<str:pk>', views.deletePost, name='delete-post'),
    path('profile/<str:pk>', views.userProfile, name="profile"),
]

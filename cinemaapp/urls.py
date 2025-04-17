from django.urls import path
from .import views
urlpatterns=[
    path('', views.index, name='index'),
    path('logout/', views.logout, name='logout'),
    path('explore_trending/', views.explore_trending, name='explore_trending'),


    # User
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('delete_account/<int:uid>/', views.delete_account, name='delete_account'),
    path('user_list_movies/', views.user_list_movies, name='user_list_movies'),
    path('add_review/<int:rid>/', views.add_review, name='add_review'),
    path('user_view_reviews/<int:rid>/', views.user_view_reviews, name='user_view_reviews'),
    path('like_review/<int:review_id>/', views.like_review, name='like_review'),
    path('dislike_review/<int:review_id>/', views.dislike_review, name='dislike_review'),
    path('list_user_reviews/', views.list_user_reviews, name='list_user_reviews'),
    path('delete_my_review/<int:rid>/', views.delete_my_review, name='delete_my_review'),

    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/<str:email>/', views.verify_otp, name='verify_otp'),
    path('reset-password/<str:email>/<str:otp>/', views.reset_password, name='reset_password'),

    

    # Admin
    path('adminhome/', views.adminhome, name='adminhome'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('add_movie/', views.add_movie, name='add_movie'),
    path('list_movies/', views.list_movies, name='list_movies'),
    path('delete_movie/<int:mid>/', views.delete_movie, name='delete_movie'),
    path('edit_movie/<int:mid>/', views.edit_movie, name='edit_movie'),
    path('user_list/', views.user_list, name='user_list'),
    path('delete_user/<int:uid>/', views.delete_user, name='delete_user'),
    path('view_reviews/', views.view_reviews, name='view_reviews'),
    path('view_review_reactions/', views.view_review_reactions, name='view_review_reactions'),
]
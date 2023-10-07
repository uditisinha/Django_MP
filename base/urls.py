from django.urls import path
from django.urls import re_path
from . import views


urlpatterns=[
    path('committees/', views.committees_list, name='committees_list'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('change_password/<token>', views.change_password, name = 'change_password'),
    path('', views.loginuser, name = 'login'),
    path('committee/<str:pk>/', views.comms, name = 'committee'),
    path('users_allowed/', views.users_allowed, name = 'users_allowed'),
    path('create_committee/', views.create_committee, name = 'create_committee'),
    path('edit_profile/<str:pk>/', views.edit_profile, name = 'edit_profile'),
    path('edit_committee/<str:pk>/', views.edit_committee, name = 'edit_committee'),
    path('delete_committee/<str:pk>/', views.delete_committee, name = 'delete_committee'),
    path('register/', views.registeruser, name = 'register'),
    path('verify/<auth_token>', views.verify, name = 'verify'),
    path('error/', views.error, name = 'error'),
    path('logout/', views.logoutuser, name = 'logout'),
    path('home/',views.home, name = 'home'),
    path('profile/<str:pk>', views.profile, name = 'profile'),
    path('edit-profile/<str:pk>', views.edit_profile, name = 'edit-profile'),
    path('delete-file/<str:pk>', views.deletefile, name = 'deletefile'),
    path('verified/', views.success, name = 'success'),
    path('searched-files.html/', views.search_files, name = 'search-files'),
    re_path(r'^media/files/(?P<path>.+)/(?P<filename>[^/]+\.[^/]+)$', views.filesview, name = 'file-view'),
    re_path(r'^media/files/(?P<path>.*)$', views.filestructure, name = 'file-system'),
    re_path(r'media/files/', views.filestructure, name = 'file-start'),
]
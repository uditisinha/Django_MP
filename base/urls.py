from django.urls import path
from django.urls import re_path
from . import views


urlpatterns=[
    path('subjects/', views.subjects_list, name='subjects_list'),
    path('forgot_password/', views.forgot_password, name = 'forgot_password'),
    path('change_password/<token>', views.change_password, name = 'change_password'),
    path('', views.loginuser, name = 'login'),
    path('subject/<str:pk>/', views.subs, name = 'subject'),
    path('create_subject/', views.create_subject, name = 'create_subject'),
    path('edit_profile/<str:pk>/', views.edit_profile, name = 'edit_profile'),
    path('delete_subject/<str:pk>/', views.delete_subject, name = 'delete_subject'),
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
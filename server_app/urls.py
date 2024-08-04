from django.urls import path
from . import views 


urlpatterns = [
    path("", views.index, name = "index"),
    path("create_user_page", views.create_user_page, name = "create_user_page"),
    path("create_user_page/create_user", views.create_user, name = "create_user"),
    path("read_user", views.read_user, name = "read_user"),
    path("read_user/delete_user", views.delete_user, name = "delete_user"),
    path("read_user/change_attribute_user", views.change_attribute_user, name = "change_attribute_user"),

    path("csrf", views.get_csrf_token),
    path('add_user_logs', views.add_user_logs, name = "add_user_logs"),
    path('add_computer_logs', views.add_computer_logs, name = "add_computer_logs"),
    
   
    path('manage_whitelist/', views.manage_whitelist, name='manage_whitelist'),
    path('manage_blacklist/', views.manage_blacklist, name='manage_blacklist'), 
   
]
    

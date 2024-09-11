from django.urls import path
from . import views, views_logs, views_users, views_blocked, views_wol, views_stream, views_monitoring
from . import views_section
urlpatterns = [
    path("", views.index, name="index"),
    path("create_user_page", views_users.create_user_page, name="create_user_page"),
    path("create_user", views_users.create_user, name="create_user"),
    path("read_user", views_users.read_user, name="read_user"),
    path("read_user/delete_user", views_users.delete_user, name="delete_user"),
    path("read_user/change_attribute_user", views_users.change_attribute_user, name="change_attribute_user"),
    path("auth_user", views_users.auth_user, name="auth_user"),
    path("get_all_student", views_users.get_all_student, name="get_all_student"),

    path('add_user_logon', views_logs.add_user_logon, name="add_user_logon"),
    path('add_user_logoff', views_logs.add_user_logoff, name="add_user_logoff"),
    
    path('check_rfid/', views.check_rfid, name='check_rfid'),
    path('view_records/', views.view_records, name='view_records'),
    path('update_approve_status/', views.update_approve_status, name='update_approve_status'),
    path('manage_schedules/', views.manage_schedules, name='manage_schedules'),

    path('manage_blocked_urls/', views_blocked.blocked_url_manage, name='manage_blocked_urls'),
   

    path('select_and_wake_computers', views_wol.select_and_wake_computers, name='select_and_wake_computers'),
    path('shutdown_computers', views_wol.shutdown_computers, name='shutdown_computers'),

    # Add paths for stream control
    path('control/', views_stream.control_view, name='control_stream'),  # Control panel
    path('start-stream/', views_stream.start_stream, name='start_stream'),  # Start streaming
    path('stop-stream/', views_stream.stop_stream, name='stop_stream'),  # Stop streaming

    # Path for streaming view
    path('stream/', views_stream.stream_view, name='stream'),
    path('stream-status/', views_stream.stream_status, name='stream_status'),

    # Monitoring URLs
    path('upload_screen/', views_monitoring.upload_screen, name='upload_screen'),
    path('view_screen/<str:client_id>/', views_monitoring.view_screen, name='view_screen'),

    # New path for client screens
    path('client_screens/', views_monitoring.client_screens_view, name='client_screens'),

    #Sections 
    path('add_section', views_section.add_section, name = "add_section"),
    path('delete_section', views_section.delete_section, name = "delete_section"),
    path('get_all_section', views_section.get_all_section, name = "get_all_section")
    #Input blocking
    #path()
]

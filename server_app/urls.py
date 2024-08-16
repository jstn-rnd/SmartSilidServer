from django.urls import path
from . import views, views_logs, views_users, views_blocked, views_wol, views_stream

urlpatterns = [
    path("", views.index, name="index"),
    path("create_user_page", views_users.create_user_page, name="create_user_page"),
    path("create_user", views_users.create_user, name="create_user"),
    path("read_user", views_users.read_user, name="read_user"),
    path("read_user/delete_user", views_users.delete_user, name="delete_user"),
    path("read_user/change_attribute_user", views_users.change_attribute_user, name="change_attribute_user"),
    path("auth_user", views_users.auth_user, name="auth_user"),

    path('add_user_logs', views_logs.add_user_logs, name="add_user_logs"),
    path('add_computer_logs', views_logs.add_computer_logs, name="add_computer_logs"),
    
    path('check_rfid/', views.check_rfid, name='check_rfid'),
    path('view_records/', views.view_records, name='view_records'),
    path('update_approve_status/', views.update_approve_status, name='update_approve_status'),
    path('manage_schedules/', views.manage_schedules, name='manage_schedules'),

    path('whitelist/', views_blocked.whitelist_view, name='whitelist'),
    path('blacklist/', views_blocked.blacklist_view, name='blacklist'),

    path('select_and_wake_computers', views_wol.select_and_wake_computers, name='select_and_wake_computers'),
    path('shutdown_computers', views_wol.shutdown_computers, name='shutdown_computers'),

    # Add paths for stream control
    path('control/', views_stream.control_view, name='control_stream'),  # Control panel
    path('start-stream/', views_stream.start_stream, name='start_stream'),  # Start streaming
    path('stop-stream/', views_stream.stop_stream, name='stop_stream'),  # Stop streaming

    # Path for streaming view
    path('stream/', views_stream.stream_view, name='stream'),
    path('stream-status/', views_stream.stream_status, name='stream_status'),
]

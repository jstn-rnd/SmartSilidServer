from django.urls import path
from . import views_logs, views_rfid, views_student, views_blocked, views_wol, views_stream, views_monitoring
from . import views_section, views_schedule, views_faculty, views_batch
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import consumers

urlpatterns = [
    
    path('auth/login', views_faculty.CustomTokenObtainPairView.as_view(), name='login'),
    path('auth/refresh', TokenRefreshView.as_view(), name='refresh'),

    # students 
    path("create_student", views_student.create_student, name="create_student"),
    path("delete_student", views_student.delete_student, name="delete_student"),
    path("change_password_student", views_student.change_password_student, name="change_password_student"),
    path("get_all_students", views_student.get_all_students, name="get_all_students"),
    path("move_section", views_student.move_section, name = "move_section"),
    path("update_student", views_student.update_student, name="update_student"),

    path("create_faculty", views_faculty.create_faculty, name="create_faculty"),
    path("authenticate", views_faculty.authenticate, name="authenticate"),
    path("get_all_faculty_and_rfid", views_faculty.get_all_faculty_and_rfid, name = "get_all_faculty_and_rfid"),
    path("delete_faculty", views_faculty.delete_faculty, name="delete_faculty"),
    path("update_faculty", views_faculty.update_faculty, name="update_faculty"),
    path("get_all_faculty", views_faculty.get_all_faculty, name = "get_all_faculty"),
    path("get_faculty_by_id", views_faculty.get_faculty_by_id, name = "get_faculty_by_id"),
    path("sign_up_admin", views_faculty.sign_up_admin, name = "sign_up_admin"),
    path("change_password_faculty_by_admin", views_faculty.change_password_faculty_by_admin, name = "change_password_faculty_by_admin"),
    path("change_password_faculty_by_faculty", views_faculty.change_password_faculty_by_faculty, name = "change_password_faculty_by_faculty"),

    path('add_user_logon', views_logs.add_user_logon, name="add_user_logon"),
    path('add_user_logoff', views_logs.add_user_logoff, name="add_user_logoff"),
    path('get_logs_computer', views_logs.get_logs_computer, name = "get_logs_computer"),

    path('check_rfid/', views_rfid.check_rfid, name='check_rfid'),
    path('bind_rfid', views_rfid.bind_rfid, name = "bind_rfid"),
    path("get_all_rfid", views_rfid.get_all_rfid, name = "get_all_rfid"), 
    path("get_logs_rfid", views_rfid.get_logs_rfid, name = "get_logs_rfid"),
    path("delete_rfid", views_rfid.delete_rfid, name = "delete_rfid"),

    path('view_records/', views_rfid.view_records, name='view_records'),
    path('update_approve_status/', views_rfid.update_approve_status, name='update_approve_status'),
    path('manage_schedules/', views_rfid.manage_schedules, name='manage_schedules'),

    path('manage_blocked_urls/', views_blocked.blocked_url_manage, name='manage_blocked_urls'),
   
    #wol
    #path('select_and_wake_computers', views_wol.select_and_wake_computers, name='select_and_wake_computers'),
    path('shutdown_computers', views_wol.shutdown_computers, name='shutdown_computers'),
    path('wake_computers', views_wol.wake_computers, name='wake_computers'),

    #computer
    path('get_all_computers', views_wol.get_all_computers, name = "get_all_computers"),
    path('set_computer_admin', views_wol.set_computer_admin, name = 'set_computer_admin'), 
    # Add paths for stream control
    path('stream/status/', views_stream.stream_status, name='stream_status'),
    path('stream/start/', views_stream.start_stream, name='start_stream'),
    path('stream/stop/', views_stream.stop_stream, name='stop_stream'),
    path('stream/', views_stream.stream_view, name='stream_view'),
    path('upload/', views_stream.upload_screen, name='upload_screen'),
    path('control/', views_stream.control_view, name='control_view'),

    # Monitoring URLs
    path('upload_screen/', views_monitoring.upload_monitor_screen, name='upload_screen'),
    path('view_screen/<str:client_id>/', views_monitoring.monitor_stream_view, name='view_screen'),  # Updated to 'view_screen'
    path('client_screens/', views_monitoring.client_screens_view, name='client_screens'),
    
    #Section
    path('add_section', views_section.add_section, name = "add_section"),
    path('delete_section', views_section.delete_section, name = "delete_section"),
    path('get_all_sections', views_section.get_all_sections, name = "get_all_sections"),
    #Input blocking
    
    path('get_url_block', views_blocked.get_url_block, name = "get_url_block"),
    path("add_url_block", views_blocked.add_url_block, name = "add_url_block"),
    path("delete_url_block", views_blocked.delete_url_block, name = "delete_url_block"),
    
    #Schedule
    path("add_schedule", views_schedule.add_schedule, name ="add_schedule"), 
    path("get_all_schedule", views_schedule.get_all_schedule, name = 'get_all_schedule'),
    path("update_schedule", views_schedule.update_schedule, name = 'update_schedule'),
    path("delete_schedule", views_schedule.delete_schedule, name ='delete_schedule'),

    path('upload_students', views_batch.upload_students_batch, name = 'upload_students'),
    path('upload_faculty', views_batch.upload_faculty_batch, name = 'upload_faculty'),
]


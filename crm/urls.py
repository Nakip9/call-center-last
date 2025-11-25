from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("leads/", views.lead_list, name="lead_list"),
    path("leads/new/", views.lead_create, name="lead_create"),
    path("leads/<int:pk>/call/", views.call_attempt_create, name="call_attempt"),
    path("attendance/toggle/", views.attendance_toggle, name="attendance_toggle"),
    path("attendance/", views.attendance_report, name="attendance"),
    path("scripts/", views.script_library, name="script_library"),
    path("scripts/manage/", views.script_manage, name="script_manage"),
    path("inbox/", views.inbox, name="inbox"),
    path("users/register/", views.user_register, name="user_register"),
]

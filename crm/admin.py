from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import Attendance, CallAttempt, Lead, Message, Revenue, Salary, Script, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "hire_date", "salary_rate", "status")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    list_display = ("username", "email", "role", "is_staff", "hire_date", "salary_rate")
    list_filter = ("role", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("lead_name", "phone_number", "manager", "created_by", "assigned_to", "payment_status", "amount_due")
    list_filter = ("payment_status", "stage")
    search_fields = ("lead_name", "phone_number", "manager")


@admin.register(CallAttempt)
class CallAttemptAdmin(admin.ModelAdmin):
    list_display = ("lead", "operator", "attempt_number", "call_result", "timestamp")
    list_filter = ("call_result",)
    search_fields = ("lead__lead_name", "operator__username")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("operator", "date", "check_in_time", "check_out_time", "status")
    list_filter = ("status",)


@admin.register(Script)
class ScriptAdmin(admin.ModelAdmin):
    list_display = ("script_name", "category", "updated_at")
    search_fields = ("script_name", "category")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("sender", "receiver", "timestamp", "is_read")
    list_filter = ("is_read",)


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ("operator", "month", "year", "total", "status")
    list_filter = ("status",)


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ("lead", "amount_paid", "paid_at")

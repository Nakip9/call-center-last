from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Attendance, CallAttempt, Lead, Message, Script, User


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "role", "hire_date", "salary_rate", "status")


class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = [
            "manager",
            "lead_name",
            "phone_number",
            "chat_id",
            "geo",
            "stage",
            "individual_request",
            "call_source",
            "assigned_to",
            "amount_due",
            "payment_status",
            "notes",
        ]
        widgets = {
            "individual_request": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class CallAttemptForm(forms.ModelForm):
    class Meta:
        model = CallAttempt
        fields = ["call_result", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["status"]


class ScriptForm(forms.ModelForm):
    class Meta:
        model = Script
        fields = ["script_name", "script_content", "category"]
        widgets = {"script_content": forms.Textarea(attrs={"rows": 6})}


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["receiver", "message_content"]
        widgets = {"message_content": forms.Textarea(attrs={"rows": 3})}

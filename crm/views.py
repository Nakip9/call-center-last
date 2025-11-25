from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import AttendanceForm, CallAttemptForm, LeadForm, MessageForm, ScriptForm, UserRegistrationForm
from .models import Attendance, CallAttempt, Lead, Message, Script, User


ROLE_LABELS = {
    User.ADMIN: "Admin",
    User.TTC_OPERATOR: "TTC Operator",
    User.CALL_CENTER: "Call Center Operator",
}


def role_required(allowed_roles):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in allowed_roles and not request.user.is_superuser:
                return HttpResponseForbidden("You do not have access to this page.")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("dashboard")
    return render(request, "crm/login.html", {"form": form})


@login_required
def dashboard(request):
    user = request.user
    role = user.role

    leads = Lead.objects.all() if role == User.ADMIN else Lead.objects.filter(created_by=user)
    assigned_leads = Lead.objects.filter(assigned_to=user)
    call_attempts = CallAttempt.objects.filter(operator=user) if role != User.ADMIN else CallAttempt.objects.all()
    scripts = Script.objects.all()
    attendance_today = Attendance.objects.filter(operator=user, date=date.today()).first()
    recent_messages = Message.objects.filter(receiver=user).select_related("sender")[:5]

    context = {
        "role": ROLE_LABELS.get(role, role),
        "leads": leads.order_by("-created_at")[:10],
        "assigned_leads": assigned_leads.order_by("-created_at")[:10],
        "call_attempts": call_attempts[:5],
        "scripts": scripts[:6],
        "attendance_today": attendance_today,
        "recent_messages": recent_messages,
    }
    return render(request, "crm/dashboard.html", context)


@login_required
@role_required([User.ADMIN, User.TTC_OPERATOR])
def lead_create(request):
    form = LeadForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        lead = form.save(commit=False)
        lead.created_by = request.user
        lead.timestamp = timezone.now()
        lead.save()
        form.save_m2m()

        if lead.assigned_to:
            Message.objects.create(
                sender=request.user,
                receiver=lead.assigned_to,
                message_content=f"New lead assigned: {lead.lead_name} ({lead.phone_number})",
            )
        messages.success(request, "Lead saved successfully.")
        return redirect("lead_list")
    return render(request, "crm/lead_form.html", {"form": form})


@login_required
def lead_list(request):
    user = request.user
    if user.role == User.ADMIN:
        qs = Lead.objects.all()
    elif user.role == User.CALL_CENTER:
        qs = Lead.objects.filter(assigned_to=user)
    else:
        qs = Lead.objects.filter(created_by=user)
    return render(request, "crm/lead_list.html", {"leads": qs.order_by("-created_at")})


@login_required
@role_required([User.ADMIN, User.CALL_CENTER])
def call_attempt_create(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    if request.user.role == User.CALL_CENTER and lead.assigned_to != request.user:
        raise Http404()

    form = CallAttemptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        attempt_number = lead.call_attempts.count() + 1
        attempt = form.save(commit=False)
        attempt.lead = lead
        attempt.operator = request.user
        attempt.attempt_number = attempt_number
        attempt.save()

        lead.stage = dict(CallAttempt.STATUS_CHOICES).get(attempt.call_result, lead.stage)
        lead.save(update_fields=["stage"])

        Message.objects.create(
            sender=request.user,
            receiver=lead.created_by,
            message_content=f"Call update for {lead.lead_name}: {attempt.get_call_result_display()}",
        )
        messages.success(request, "Call attempt logged.")
        return redirect("lead_list")

    return render(request, "crm/call_attempt_form.html", {"form": form, "lead": lead})


@login_required
def attendance_toggle(request):
    today = date.today()
    record, created = Attendance.objects.get_or_create(operator=request.user, date=today)
    if created or not record.check_in_time:
        record.check_in_time = timezone.now()
        record.status = "checked_in"
        messages.success(request, "Clocked in successfully.")
    elif not record.check_out_time:
        record.check_out_time = timezone.now()
        record.status = "checked_out"
        messages.success(request, "Clocked out successfully.")
    else:
        messages.info(request, "You have already clocked out today.")
    record.save()
    return redirect("dashboard")


@login_required
def attendance_report(request):
    records = Attendance.objects.filter(operator=request.user)
    if request.user.role == User.ADMIN:
        records = Attendance.objects.all()
    return render(request, "crm/attendance.html", {"records": records.order_by("-date")})


@login_required
@role_required([User.ADMIN])
def script_manage(request):
    scripts = Script.objects.all()
    form = ScriptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        script = form.save(commit=False)
        script.created_by = request.user
        script.save()
        messages.success(request, "Script saved.")
        return redirect("script_manage")
    return render(request, "crm/scripts.html", {"scripts": scripts, "form": form})


@login_required
def script_library(request):
    scripts = Script.objects.all()
    return render(request, "crm/script_library.html", {"scripts": scripts})


@login_required
def inbox(request):
    messages_qs = Message.objects.filter(receiver=request.user).select_related("sender")
    form = MessageForm(request.POST or None)
    form.fields["receiver"].queryset = User.objects.exclude(id=request.user.id)
    if request.method == "POST" and form.is_valid():
        msg = form.save(commit=False)
        msg.sender = request.user
        msg.save()
        messages.success(request, "Message sent.")
        return redirect("inbox")
    return render(
        request,
        "crm/inbox.html",
        {"messages": messages_qs.order_by("-timestamp"), "form": form},
    )


@login_required
@role_required([User.ADMIN])
def user_register(request):
    form = UserRegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.is_staff = True if user.role == User.ADMIN else False
        user.save()
        messages.success(request, "User account created.")
        return redirect("dashboard")
    return render(request, "crm/user_register.html", {"form": form})

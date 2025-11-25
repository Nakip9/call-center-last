from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    ADMIN = "admin"
    TTC_OPERATOR = "ttc_operator"
    CALL_CENTER = "call_center"

    ROLE_CHOICES = [
        (ADMIN, "Admin"),
        (TTC_OPERATOR, "TTC Operator"),
        (CALL_CENTER, "Call Center Operator"),
    ]

    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default=TTC_OPERATOR)
    hire_date = models.DateField(null=True, blank=True)
    salary_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=64, default="active")

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class Lead(models.Model):
    PAID = "paid"
    NOT_PAID = "not_paid"
    PAYMENT_CHOICES = [(PAID, "Paid"), (NOT_PAID, "Not Paid")]

    timestamp = models.DateTimeField(default=timezone.now)
    manager = models.CharField(max_length=255)
    lead_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=50)
    chat_id = models.CharField(max_length=255, blank=True)
    geo = models.CharField(max_length=255, blank=True)
    stage = models.CharField(max_length=255, blank=True)
    individual_request = models.TextField(blank=True)
    call_source = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="leads")
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_leads",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=16, choices=PAYMENT_CHOICES, default=NOT_PAID)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.lead_name} - {self.phone_number}"


class CallAttempt(models.Model):
    STATUS_CHOICES = [
        ("done", "Done"),
        ("busy", "Busy"),
        ("no_answer", "No Answer"),
        ("next_attempt", "Next attempt needed"),
        ("closed", "Lead closed"),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="call_attempts")
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="call_attempts")
    attempt_number = models.PositiveIntegerField(default=1)
    call_result = models.CharField(max_length=50, choices=STATUS_CHOICES)
    notes = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.lead} attempt {self.attempt_number}"


class Attendance(models.Model):
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_records")
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=32, default="pending")

    class Meta:
        ordering = ["-date", "-check_in_time"]

    def __str__(self):
        return f"{self.operator} - {self.date}"


class Script(models.Model):
    script_name = models.CharField(max_length=255)
    script_content = models.TextField()
    category = models.CharField(max_length=255, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.script_name


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    message_content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class Salary(models.Model):
    STATUS_CHOICES = [("paid", "Paid"), ("pending", "Pending")]

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="salaries")
    month = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bonuses = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")

    class Meta:
        unique_together = ("operator", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.operator} {self.month}/{self.year}"


class Revenue(models.Model):
    lead = models.OneToOneField(Lead, on_delete=models.CASCADE, related_name="revenue")
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Revenue for {self.lead}"

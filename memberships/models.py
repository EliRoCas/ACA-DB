from django.db import models
from django.utils import timezone
from datetime import timedelta


class Membership(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_months = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"
    
    
class Member(models.Model):

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]

    full_name = models.CharField(max_length=150)
    document = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    membership = models.ForeignKey(
        Membership,
        on_delete=models.SET_NULL,
        null=True,
        related_name='members'
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )

    membership_expires_at = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        if self.membership_expires_at:
            return self.membership_expires_at >= timezone.now().date()
        return False

    def __str__(self):
        return self.full_name
    
class Payment(models.Model):

    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('transfer', 'Transfer'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Actualizar vencimiento automáticamente
        if self.member.membership:
            today = timezone.now().date()
            duration = timedelta(days=self.member.membership.duration_months * 30)

            if self.member.membership_expires_at and self.member.membership_expires_at > today:
                self.member.membership_expires_at += duration
            else:
                self.member.membership_expires_at = today + duration

            self.member.status = 'active'
            self.member.save()

    def __str__(self):
        return f"Payment - {self.member.full_name}"    
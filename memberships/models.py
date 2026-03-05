from django.db import models
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta


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
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo'),
        ('pse', 'PSE'),
        ('card', 'Tarjeta'),
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
    
    payment_method = models.CharField(
        max_length=10,
        choices=PAYMENT_METHOD_CHOICES,
        default='cash',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_active(self):
        """Verifica si la membresía está activa basándose en la fecha de vencimiento"""
        if self.membership_expires_at:
            return self.membership_expires_at >= timezone.now().date()
        return False
    
    def update_status(self):
        """Actualiza el estado del miembro basándose en la fecha de vencimiento"""
        if self.membership_expires_at:
            if self.membership_expires_at >= timezone.now().date():
                self.status = 'active'
            else:
                self.status = 'inactive'
        # Si no hay fecha de vencimiento, no cambiar el estado (puede ser manual)
        return self.status
    
    def save(self, *args, **kwargs):
        """Sobrescribe save para actualizar el estado automáticamente"""
        # Solo actualizar el estado automáticamente si se indica explícitamente
        # o si viene de un pago (cuando skip_status_update no está presente)
        skip_update = kwargs.pop('skip_status_update', False)
        
        if not skip_update and self.membership_expires_at:
            self.update_status()
        
        super().save(*args, **kwargs)

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
            # Usar relativedelta para agregar meses exactos
            duration_months = self.member.membership.duration_months
            self.member.membership_expires_at = today + relativedelta(months=duration_months)

            # El estado se actualizará automáticamente en member.save() basado en la fecha
            self.member.save()  # skip_status_update=False por defecto, actualizará el estado

    def __str__(self):
        return f"Payment - {self.member.full_name}"    
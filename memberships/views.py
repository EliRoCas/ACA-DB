from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from .models import Membership, Member, Payment
from .forms import (CustomAuthenticationForm, MemberRegistrationForm, MemberAdminForm, 
                    AdminUserCreationForm, SimulatedPSEPaymentForm, SimulatedCardPaymentForm)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("membership_list")
        return super().handle_no_permission()


class LandingPageView(TemplateView):
    template_name = 'landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['memberships'] = Membership.objects.all().order_by('price')
        context['member_count'] = 150  
        return context

class MembershipListView(LoginRequiredMixin, ListView):
    model = Membership
    template_name = "memberships/membership_list.html"
    context_object_name = "memberships"
    ordering = ["name"]
    login_url = "login"

class MembershipCreateView(LoginRequiredMixin, CreateView):
    model = Membership
    fields = ["name", "price", "duration_months", "description"]
    template_name = "memberships/membership_form.html"
    success_url = reverse_lazy("membership_list")
    login_url = "login"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. Plan Premium",
            }
        )
        form.fields["price"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. 100.000 COP",
            }
        )
        form.fields["duration_months"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. 12",
            }
        )
        form.fields["description"].widget.attrs.update(
            {
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe beneficios y alcance del plan",
            }
        )

        if form.is_bound:
            for field_name in form.fields:
                current_classes = form.fields[field_name].widget.attrs.get("class", "").strip()
                state_class = "is-invalid" if form.errors.get(field_name) else "is-valid"
                form.fields[field_name].widget.attrs["class"] = f"{current_classes} {state_class}".strip()

        return form


class MembershipUpdateView(LoginRequiredMixin, UpdateView):
    model = Membership
    fields = ["name", "price", "duration_months", "description"]
    template_name = "memberships/membership_form.html"
    success_url = reverse_lazy("membership_list")
    login_url = "login"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields["name"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. Plan Premium",
            }
        )
        form.fields["price"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. 100.000 COP",
            }
        )
        form.fields["duration_months"].widget.attrs.update(
            {
                "class": "form-control",
                "placeholder": "Ej. 12",
            }
        )
        form.fields["description"].widget.attrs.update(
            {
                "class": "form-control",
                "rows": 4,
                "placeholder": "Describe beneficios y alcance del plan",
            }
        )

        if form.is_bound:
            for field_name in form.fields:
                current_classes = form.fields[field_name].widget.attrs.get("class", "").strip()
                state_class = "is-invalid" if form.errors.get(field_name) else "is-valid"
                form.fields[field_name].widget.attrs["class"] = f"{current_classes} {state_class}".strip()

        return form


class MembershipDeleteView(LoginRequiredMixin, DeleteView):
    model = Membership
    template_name = "memberships/membership_confirm_delete.html"
    success_url = reverse_lazy("membership_list")
    login_url = "login"


class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = "registration/login.html"
    success_url = reverse_lazy("membership_list")


class AdminUserCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Vista para que administradores creen otros usuarios administradores"""
    model = User
    form_class = AdminUserCreationForm
    template_name = "memberships/admin_user_form.html"
    success_url = reverse_lazy("admin_user_list")
    login_url = "login"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Crear Usuario Administrador'
        context['page_subtitle'] = 'Agrega un nuevo usuario administrador para el gimnasio.'
        return context


class AdminUserListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """Vista para listar usuarios administradores"""
    model = User
    template_name = "memberships/admin_user_list.html"
    context_object_name = "admin_users"
    login_url = "login"
    
    def get_queryset(self):
        # Solo mostrar usuarios que son staff (administradores)
        return User.objects.filter(is_staff=True).order_by('-date_joined')


class AdminUserDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """Eliminar usuarios administradores, excepto superusuarios"""
    model = User
    template_name = "memberships/admin_user_confirm_delete.html"
    success_url = reverse_lazy("admin_user_list")
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_superuser:
            raise PermissionDenied("No se puede eliminar un superusuario.")
        return super().dispatch(request, *args, **kwargs)


# ========== MEMBER VIEWS ==========

class MemberRegisterView(FormView):
    """Vista pública para que los clientes se registren como miembros"""
    template_name = "memberships/member_register.html"
    form_class = MemberRegistrationForm

    def form_valid(self, form):
        # Guardar el miembro
        member = form.save()
        payment_method = form.cleaned_data.get('payment_method')
        
        # Guardar el método de pago en el miembro
        member.payment_method = payment_method
        member.save()
        
        # Guardar datos en sesión para el pago
        self.request.session['pending_member_id'] = member.id
        self.request.session['pending_membership_id'] = member.membership.id if member.membership else None
        self.request.session['pending_payment_method'] = payment_method
        
        # Redirigir según el método de pago seleccionado
        if payment_method == 'cash':
            # Para efectivo, ir directo a página de éxito (sin pago automático)
            return redirect('member_register_success')
        elif payment_method == 'pse':
            # Redirigir a simulación de pago PSE
            return redirect('simulated_pse_payment')
        elif payment_method == 'card':
            # Redirigir a simulación de pago con tarjeta
            return redirect('simulated_card_payment')
        
        return redirect('member_register_success')
    
    def get_success_url(self):
        return reverse('member_register_success')


class MemberRegisterSuccessView(TemplateView):
    """Página de éxito después de registrarse como miembro"""
    template_name = "memberships/member_register_success.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener método de pago de la sesión
        payment_method = self.request.session.get('pending_payment_method', 'cash')
        context['payment_method'] = payment_method
        
        # Limpiar sesión (ahora también payment_processed para próximo flujo)
        self.request.session.pop('pending_member_id', None)
        self.request.session.pop('pending_membership_id', None)
        self.request.session.pop('pending_payment_method', None)
        self.request.session.pop('payment_processed', None)
        
        return context


class SimulatedPSEPaymentView(FormView):
    """Vista simulada para pago PSE"""
    template_name = "memberships/simulated_pse_payment.html"
    form_class = SimulatedPSEPaymentForm
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que haya un pago pendiente
        if 'pending_member_id' not in request.session:
            return redirect('member_register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('pending_member_id')
        if member_id:
            member = get_object_or_404(Member, id=member_id)
            context['member'] = member
            context['amount'] = member.membership.price if member.membership else 0
        return context
    
    def form_valid(self, form):
        # Simular procesamiento de pago PSE
        member_id = self.request.session.get('pending_member_id')
        
        # Proteger contra doble submit: validar flag en sesión
        if self.request.session.get('payment_processed'):
            return redirect('payment_success')
        
        member = get_object_or_404(Member, id=member_id)
        
        # Validar que no exista pago reciente (defensa N+1)
        recent_payment = Payment.objects.filter(
            member=member,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        
        if recent_payment:
            # Pago ya existe, redirigir a éxito
            return redirect('payment_success')
        
        # Crear pago simulado
        if member.membership:
            Payment.objects.create(
                member=member,
                amount=member.membership.price,
                method='transfer',  
            )
            # Marcar como procesado en sesión
            self.request.session['payment_processed'] = True
        
        return redirect('payment_success')


class SimulatedCardPaymentView(FormView):
    """Vista simulada para pago con tarjeta"""
    template_name = "memberships/simulated_card_payment.html"
    form_class = SimulatedCardPaymentForm
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar que haya un pago pendiente
        if 'pending_member_id' not in request.session:
            return redirect('member_register')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('pending_member_id')
        if member_id:
            member = get_object_or_404(Member, id=member_id)
            context['member'] = member
            context['amount'] = member.membership.price if member.membership else 0
        return context
    
    def form_valid(self, form):
        # Simular procesamiento de pago con tarjeta
        member_id = self.request.session.get('pending_member_id')
        
        # Proteger contra doble submit: validar flag en sesión
        if self.request.session.get('payment_processed'):
            return redirect('payment_success')
        
        member = get_object_or_404(Member, id=member_id)
        
        # Validar que no exista pago reciente (defensa N+1)
        recent_payment = Payment.objects.filter(
            member=member,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).exists()
        
        if recent_payment:
            # Pago ya existe, redirigir a éxito
            return redirect('payment_success')
        
        # Crear pago simulado
        if member.membership:
            Payment.objects.create(
                member=member,
                amount=member.membership.price,
                method='card',
            )
            # Marcar como procesado en sesión
            self.request.session['payment_processed'] = True
        
        return redirect('payment_success')


class PaymentSuccessView(TemplateView):
    """Página de éxito después de completar un pago simulado"""
    template_name = "memberships/payment_success.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        member_id = self.request.session.get('pending_member_id')
        if member_id:
            member = get_object_or_404(Member, id=member_id)
            context['member'] = member
        
        # Limpiar sesión
        self.request.session.pop('pending_member_id', None)
        self.request.session.pop('pending_membership_id', None)
        self.request.session.pop('pending_payment_method', None)
        self.request.session.pop('payment_processed', None)
        
        return context


class MemberListView(LoginRequiredMixin, ListView):
    """Lista de miembros - solo para usuarios autenticados"""
    model = Member
    template_name = "memberships/member_list.html"
    context_object_name = "members"
    ordering = ["-created_at"]
    login_url = "login"
    
    def get_queryset(self):
        """Obtiene la lista de miembros optimizando la carga de relaciones (evita N+1)"""
        queryset = super().get_queryset().select_related('membership')
        return queryset


class MemberCreateView(LoginRequiredMixin, CreateView):
    """Crear un nuevo miembro desde administración"""
    model = Member
    form_class = MemberAdminForm
    template_name = "memberships/member_form.html"
    success_url = reverse_lazy("member_list")
    login_url = "login"
    
    def form_valid(self, form):
        """Guardar el miembro y procesar el pago si es necesario"""
        self.object = form.save(commit=False)
        # Guardar el método de pago
        payment_method = form.cleaned_data.get('payment_method', 'cash')
        self.object.payment_method = payment_method
        # Usar skip_status_update=True para respetar el estado manual del formulario
        self.object.save(skip_status_update=True)
        
        # Si el método de pago es Tarjeta y hay membresía, crear Payment automático
        if payment_method == 'card' and self.object.membership:
            Payment.objects.create(
                member=self.object,
                amount=self.object.membership.price,
                method='card',
            )
            # Mostrar mensaje de éxito con pago registrado
            messages.success(
                self.request,
                'Miembro creado exitosamente. Pago registrado automáticamente.'
            )
        
        return redirect(self.get_success_url())


class MemberUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un miembro existente"""
    model = Member
    form_class = MemberAdminForm
    template_name = "memberships/member_form.html"
    success_url = reverse_lazy("member_list")
    login_url = "login"
    
    def form_valid(self, form):
        """Guardar el miembro y recalcular fechas si cambia el plan"""
        # Obtener el miembro original antes de cambios
        original_member = Member.objects.get(pk=self.object.pk)
        original_plan = original_member.membership
        
        self.object = form.save(commit=False)
        # Guardar el método de pago
        payment_method = form.cleaned_data.get('payment_method', 'cash')
        self.object.payment_method = payment_method
        
        # Verificar si el plan cambió
        new_plan = self.object.membership
        plan_changed = original_plan != new_plan
        
        # Si el plan cambió, recalcular la fecha de vencimiento desde hoy
        if plan_changed and new_plan:
            today = timezone.now().date()
            self.object.membership_expires_at = today + relativedelta(months=new_plan.duration_months)
        
        # Usar skip_status_update=True para respetar el estado manual del formulario
        self.object.save(skip_status_update=True)
        
        # Si el método de pago es Tarjeta y hay membresía, crear Payment automático
        if payment_method == 'card' and self.object.membership:
            # Verificar que no exista un pago reciente para evitar duplicados
            recent_payment = Payment.objects.filter(
                member=self.object,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).exists()
            
            if not recent_payment:
                Payment.objects.create(
                    member=self.object,
                    amount=self.object.membership.price,
                    method='card',
                )
                # Mostrar mensaje de éxito con pago registrado
                messages.success(
                    self.request,
                    'Miembro actualizado exitosamente. Pago registrado.'
                )
        elif plan_changed:
            # Mostrar mensaje si solo cambió el plan
            messages.success(
                self.request,
                'Miembro actualizado exitosamente. Fecha de vencimiento recalculada.'
            )
        
        return redirect(self.get_success_url())


class MemberDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar un miembro"""
    model = Member
    template_name = "memberships/member_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("member_list")
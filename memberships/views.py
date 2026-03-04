from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.views.generic.edit import FormView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from .models import Membership, Member
from .forms import CustomAuthenticationForm, MemberRegistrationForm, MemberAdminForm, AdminUserCreationForm


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return redirect("membership_list")
        return super().handle_no_permission()

# Create your views here.
class LandingPageView(TemplateView):
    template_name = 'memberships/landing.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['memberships'] = Membership.objects.all().order_by('price')
        context['member_count'] = 150  # Ejemplo
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
    success_url = reverse_lazy("member_register_success")

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class MemberRegisterSuccessView(TemplateView):
    """Página de éxito después de registrarse como miembro"""
    template_name = "memberships/member_register_success.html"


class MemberListView(LoginRequiredMixin, ListView):
    """Lista de miembros - solo para usuarios autenticados"""
    model = Member
    template_name = "memberships/member_list.html"
    context_object_name = "members"
    ordering = ["-created_at"]
    login_url = "login"


class MemberCreateView(LoginRequiredMixin, CreateView):
    """Crear un nuevo miembro desde administración"""
    model = Member
    form_class = MemberAdminForm
    template_name = "memberships/member_form.html"
    success_url = reverse_lazy("member_list")
    login_url = "login"


class MemberUpdateView(LoginRequiredMixin, UpdateView):
    """Editar un miembro existente"""
    model = Member
    form_class = MemberAdminForm
    template_name = "memberships/member_form.html"
    success_url = reverse_lazy("member_list")
    login_url = "login"


class MemberDeleteView(LoginRequiredMixin, DeleteView):
    """Eliminar un miembro"""
    model = Member
    template_name = "memberships/member_confirm_delete.html"
    login_url = "login"
    success_url = reverse_lazy("member_list")
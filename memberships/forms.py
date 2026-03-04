from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Member


# Constants for form labels and messages
# These are UI labels and error messages, not actual credentials
LABEL_USERNAME = 'Nombre de usuario'
# Form field labels - no sensitive data
LABEL_AUTH_SECRET = 'Contraseña'
LABEL_AUTH_SECRET_CONFIRM = 'Confirmar contraseña'
LABEL_FULL_NAME = 'Nombre Completo'
LABEL_DOCUMENT = 'Documento de Identidad'
LABEL_PHONE = 'Teléfono'
LABEL_EMAIL = 'Correo Electrónico'
LABEL_MEMBERSHIP = 'Plan de Membresía'
LABEL_STATUS = 'Estado'

ERROR_USERNAME_EXISTS = 'Este nombre de usuario ya está en uso.'
ERROR_DOCUMENT_EXISTS = 'Este documento ya está registrado.'

# Form field placeholders - no sensitive data
PLACEHOLDER_AUTH_SECRET = 'Ingresa una contraseña segura'
PLACEHOLDER_AUTH_SECRET_CONFIRM = 'Repite tu contraseña'
PLACEHOLDER_USERNAME_LOGIN = 'Ingresa tu nombre de usuario'
PLACEHOLDER_AUTH_SECRET_LOGIN = 'Ingresa tu contraseña'
PLACEHOLDER_FULL_NAME = 'Ej. Juan Pérez'
PLACEHOLDER_DOCUMENT = 'Ej. 1234567890'
PLACEHOLDER_PHONE = 'Ej. +57 300 123 4567'
PLACEHOLDER_EMAIL = 'Ej. juanperez@gmail.com'


class CustomAuthenticationForm(AuthenticationForm):
    """Custom AuthenticationForm with Bootstrap styling"""
    
    username = forms.CharField(
        label=LABEL_USERNAME,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': PLACEHOLDER_USERNAME_LOGIN,
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label=LABEL_AUTH_SECRET,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': PLACEHOLDER_AUTH_SECRET_LOGIN,
        })
    )


class AdminUserCreationForm(UserCreationForm):
    """Formulario para que administradores creen otros usuarios administradores"""
    
    username = forms.CharField(
        label=LABEL_USERNAME,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. nombreusuario',
        })
    )
    password1 = forms.CharField(
        label=LABEL_AUTH_SECRET,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': PLACEHOLDER_AUTH_SECRET,
        })
    )
    password2 = forms.CharField(
        label=LABEL_AUTH_SECRET_CONFIRM,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': PLACEHOLDER_AUTH_SECRET_CONFIRM,
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError(ERROR_USERNAME_EXISTS)
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        # Marcar el usuario como staff (administrador)
        user.is_staff = True
        if commit:
            user.save()
        return user


class MemberRegistrationForm(forms.ModelForm):
    """Form para que clientes se registren como miembros del gimnasio (formulario público)"""
    
    class Meta:
        model = Member
        fields = ['full_name', 'document', 'phone', 'email', 'membership']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar estilos Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
            })
        
        # Personalizaciones específicas
        self.fields['full_name'].widget.attrs.update({
            'placeholder': PLACEHOLDER_FULL_NAME,
        })
        self.fields['document'].widget.attrs.update({
            'placeholder': PLACEHOLDER_DOCUMENT,
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': PLACEHOLDER_PHONE,
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': PLACEHOLDER_EMAIL,
        })
        
        # Los labels en castellano
        self.fields['full_name'].label = LABEL_FULL_NAME
        self.fields['document'].label = LABEL_DOCUMENT
        self.fields['phone'].label = LABEL_PHONE
        self.fields['email'].label = LABEL_EMAIL
        self.fields['membership'].label = LABEL_MEMBERSHIP
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if Member.objects.filter(document=document).exists():
            raise forms.ValidationError(ERROR_DOCUMENT_EXISTS)
        return document


class MemberAdminForm(forms.ModelForm):
    """Form para administradores (incluye estado)"""
    
    class Meta:
        model = Member
        fields = ['full_name', 'document', 'phone', 'email', 'membership', 'status']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar estilos Bootstrap a todos los campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
            })
        
        # Personalizaciones específicas
        self.fields['full_name'].widget.attrs.update({
            'placeholder': PLACEHOLDER_FULL_NAME,
        })
        self.fields['document'].widget.attrs.update({
            'placeholder': PLACEHOLDER_DOCUMENT,
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': PLACEHOLDER_PHONE,
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': PLACEHOLDER_EMAIL,
        })
        
        # Los labels en castellano
        self.fields['full_name'].label = LABEL_FULL_NAME
        self.fields['document'].label = LABEL_DOCUMENT
        self.fields['phone'].label = LABEL_PHONE
        self.fields['email'].label = LABEL_EMAIL
        self.fields['membership'].label = LABEL_MEMBERSHIP
        self.fields['status'].label = LABEL_STATUS
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        # Si estamos editando, permitir el documento actual
        if self.instance.pk:
            if Member.objects.filter(document=document).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(ERROR_DOCUMENT_EXISTS)
        else:
            if Member.objects.filter(document=document).exists():
                raise forms.ValidationError(ERROR_DOCUMENT_EXISTS)
        return document

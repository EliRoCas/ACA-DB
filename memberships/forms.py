from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Member, Membership


class CustomUserCreationForm(UserCreationForm):
    """Custom UserCreationForm with Bootstrap styling"""
    
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. miusuario123',
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa una contraseña segura',
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Custom AuthenticationForm with Bootstrap styling"""
    
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña',
        })
    )


class AdminUserCreationForm(UserCreationForm):
    """Formulario para que administradores creen otros usuarios administradores"""
    
    username = forms.CharField(
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. nombreusuario',
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa una contraseña segura',
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repite tu contraseña',
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Este nombre de usuario ya está en uso.')
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
            'placeholder': 'Ej. Juan Pérez',
        })
        self.fields['document'].widget.attrs.update({
            'placeholder': 'Ej. 1234567890',
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': 'Ej. +57 300 123 4567',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Ej. juanperez@gmail.com',
        })
        
        # Los labels en castellano
        self.fields['full_name'].label = 'Nombre Completo'
        self.fields['document'].label = 'Documento de Identidad'
        self.fields['phone'].label = 'Teléfono'
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['membership'].label = 'Plan de Membresía'
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if Member.objects.filter(document=document).exists():
            raise forms.ValidationError('Este documento ya está registrado.')
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
            'placeholder': 'Ej. Juan Pérez',
        })
        self.fields['document'].widget.attrs.update({
            'placeholder': 'Ej. 1234567890',
        })
        self.fields['phone'].widget.attrs.update({
            'placeholder': 'Ej. +57 300 123 4567',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Ej. juanperez@gmail.com',
        })
        
        # Los labels en castellano
        self.fields['full_name'].label = 'Nombre Completo'
        self.fields['document'].label = 'Documento de Identidad'
        self.fields['phone'].label = 'Teléfono'
        self.fields['email'].label = 'Correo Electrónico'
        self.fields['membership'].label = 'Plan de Membresía'
        self.fields['status'].label = 'Estado'
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        # Si estamos editando, permitir el documento actual
        if self.instance.pk:
            if Member.objects.filter(document=document).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este documento ya está registrado.')
        else:
            if Member.objects.filter(document=document).exists():
                raise forms.ValidationError('Este documento ya está registrado.')
        return document

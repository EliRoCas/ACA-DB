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
LABEL_EXPIRES_AT = 'Fecha de Vencimiento'
LABEL_PAYMENT_METHOD = 'Método de Pago'

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
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo (Pagar en el gimnasio)'),
        ('pse', 'PSE (Pago en línea)'),
        ('card', 'Tarjeta de Crédito/Débito'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label=LABEL_PAYMENT_METHOD,
        initial='cash'
    )
    
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
        
        # Información adicional
        self.fields['membership'].help_text = 'Selecciona el plan que mejor se adapte a tus necesidades'
    
    def clean_document(self):
        document = self.cleaned_data.get('document')
        if Member.objects.filter(document=document).exists():
            raise forms.ValidationError(ERROR_DOCUMENT_EXISTS)
        return document


class MemberAdminForm(forms.ModelForm):
    """Form para administradores (incluye estado y método de pago)"""

    STATUS_CHOICES = [
        (True, 'Activo'),
        (False, 'Inactivo'),
    ]

    status = forms.TypedChoiceField(
        choices=STATUS_CHOICES,
        coerce=lambda value: value in (True, 'True', 'true', '1', 1),
        widget=forms.Select,
        label=LABEL_STATUS,
        initial=True,
    )
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Efectivo (Cambio manual de estado)'),
        ('card', 'Tarjeta de Crédito/Débito'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        label=LABEL_PAYMENT_METHOD,
        initial='cash',
        required=False,
        help_text='Selecciona el método de pago que utilizará este miembro'
    )
    
    class Meta:
        model = Member
        fields = ['full_name', 'document', 'phone', 'email', 'membership', 'status', 'membership_expires_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si estamos editando, usar el payment_method guardado como valor inicial
        if self.instance.pk and self.instance.payment_method:
            self.fields['payment_method'].initial = self.instance.payment_method
        
        # Aplicar estilos Bootstrap a todos los campos (excepto payment_method que usa RadioSelect)
        for field_name, field in self.fields.items():
            if field_name != 'payment_method':
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
        self.fields['membership_expires_at'].label = LABEL_EXPIRES_AT
        
        # Hacer membership_expires_at opcional visualmente
        self.fields['membership_expires_at'].required = False
        self.fields['membership_expires_at'].help_text = 'Dejar vacío si aún no tiene membresía activa. Se calculará automáticamente al registrar un pago.'
        
        # Configurar el widget de fecha
        self.fields['membership_expires_at'].widget.attrs.update({
            'type': 'date',
            'class': 'form-control',
        })
    
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


class SimulatedPSEPaymentForm(forms.Form):
    """Formulario simulado para pago PSE"""
    
    BANK_CHOICES = [
        ('', 'Selecciona tu banco'),
        ('bancolombia', 'Bancolombia'),
        ('davivienda', 'Davivienda'),
        ('banco_bogota', 'Banco de Bogotá'),
        ('bbva', 'BBVA'),
        ('banco_popular', 'Banco Popular'),
        ('colpatria', 'Colpatria'),
        ('av_villas', 'AV Villas'),
    ]
    
    PERSON_TYPE_CHOICES = [
        ('natural', 'Persona Natural'),
        ('juridica', 'Persona Jurídica'),
    ]
    
    bank = forms.ChoiceField(
        choices=BANK_CHOICES,
        label='Banco',
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    
    person_type = forms.ChoiceField(
        choices=PERSON_TYPE_CHOICES,
        label='Tipo de Persona',
        widget=forms.RadioSelect(),
        initial='natural'
    )
    
    document_number = forms.CharField(
        label='Número de Documento',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej. 1234567890'
        })
    )
    
    def clean_bank(self):
        bank = self.cleaned_data.get('bank')
        if not bank:
            raise forms.ValidationError('Debes seleccionar un banco')
        return bank


class SimulatedCardPaymentForm(forms.Form):
    """Formulario simulado para pago con tarjeta"""
    
    card_number = forms.CharField(
        label='Número de Tarjeta',
        max_length=19,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '1234 5678 9012 3456',
            'maxlength': '19',
            'pattern': '[0-9 ]*'
        })
    )
    
    cardholder_name = forms.CharField(
        label='Nombre del Titular',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre como aparece en la tarjeta',
            'style': 'text-transform: uppercase;'
        })
    )
    
    expiry_date = forms.CharField(
        label='Fecha de Vencimiento',
        max_length=5,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/AA',
            'maxlength': '5',
            'pattern': '[0-9/]*'
        })
    )
    
    cvv = forms.CharField(
        label='CVV',
        max_length=4,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '***',
            'maxlength': '4',
            'pattern': '[0-9]*'
        })
    )
    
    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number', '').replace(' ', '')
        if not card_number.isdigit():
            raise forms.ValidationError('El número de tarjeta debe contener solo dígitos')
        if len(card_number) < 13 or len(card_number) > 19:
            raise forms.ValidationError('Número de tarjeta inválido')
        return card_number
    
    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv', '')
        if not cvv.isdigit():
            raise forms.ValidationError('El CVV debe contener solo dígitos')
        if len(cvv) < 3 or len(cvv) > 4:
            raise forms.ValidationError('CVV inválido')
        return cvv
    
    def clean_expiry_date(self):
        expiry = self.cleaned_data.get('expiry_date', '')
        error_msg = 'Formato inválido. Use MM/AA'
        
        if '/' not in expiry:
            raise forms.ValidationError(error_msg)
        parts = expiry.split('/')
        if len(parts) != 2:
            raise forms.ValidationError(error_msg)
        month, year = parts
        if not month.isdigit() or not year.isdigit():
            raise forms.ValidationError('El mes y año deben ser numéricos')
        if len(month) != 2 or len(year) != 2:
            raise forms.ValidationError(error_msg)
        if int(month) < 1 or int(month) > 12:
            raise forms.ValidationError('Mes inválido')
        return expiry

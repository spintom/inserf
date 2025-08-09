from django import forms


class ContactForm(forms.Form):
    nombre = forms.CharField(label="Nombre", max_length=100, widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': 'Tu nombre'
    }))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        'class': 'input',
        'placeholder': 'tu@email.com'
    }))
    telefono = forms.CharField(label="Teléfono", max_length=30, required=False, widget=forms.TextInput(attrs={
        'class': 'input',
        'placeholder': '+56 9 1234 5678'
    }))
    mensaje = forms.CharField(label="Mensaje", widget=forms.Textarea(attrs={
        'class': 'textarea',
        'rows': 4,
        'placeholder': 'Cuéntanos en qué te podemos ayudar'
    }))
    hpot = forms.CharField(required=False, widget=forms.HiddenInput())

    def cleaned_summary(self):
        if not self.is_valid():
            return None
        cd = self.cleaned_data
        tel = cd.get('telefono')
        tel_line = f"\nTeléfono: {tel}" if tel else ''
        return f"Nombre: {cd['nombre']}\nEmail: {cd['email']}{tel_line}\n\nMensaje:\n{cd['mensaje']}"

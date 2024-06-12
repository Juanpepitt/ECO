from django import forms

from django.core.exceptions import ValidationError

from .widgets import CommaDecimalWidget

##########################
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

CATEGORIAS_PRODUCTO = [
    ('Alimentación', 'Alimentación'),
    ('Tecnología', 'Tecnología'),
    ('Ropa', 'Ropa'),
    ('Hogar', 'Hogar'),
    ('Otros', 'Otros'),
]

class ProductForm(forms.Form):
    nombre = forms.CharField(label='Nombre de producto', max_length=150, strip=False, widget=forms.TextInput(attrs={'autofocus': True, 'style': 'width: 100%;'}), required=True)
    categoria = forms.ChoiceField(label='Categoría de producto', choices=CATEGORIAS_PRODUCTO, required=True, widget=forms.Select(attrs={'style': 'width: 100%;'}))
    descripcion = forms.CharField(label='Descripción del producto', widget=forms.Textarea(attrs={'autofocus': True, 'style': 'width: 100%;'}), strip=True)
    disponibilidad = forms.BooleanField(label='Disponible', required=False)
    precio = forms.DecimalField(label='Precio en €', max_digits=10, decimal_places=2, required=True, help_text="Si se trata de un producto a granel, añade el precio en €/kg", widget=CommaDecimalWidget())
    stock = forms.IntegerField(label='Número de unidades disponibles en Stock', required=False)
    imagen = forms.ImageField(label='Imagen del producto', required=False)
    # imagenes = forms.FileField(label='Imagen o imágenes del producto', widget=MultipleFileInput(attrs={'multiple': True, 'style': 'width: 100%;'}))
    # imagen_url = forms.URLField(required=False)

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor que 0.')
        return precio


##########################
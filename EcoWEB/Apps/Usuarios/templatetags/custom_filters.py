from django import template
import math

register = template.Library()

@register.filter
def format_decimal(value):
    """
    Formatea un número decimal reemplazando el punto por una coma
    y eliminando la parte decimal si es .00 o .0. 
    Si tiene decimales significativos, muestra siempre dos dígitos después de la coma.
    """
    try:
        value = float(value)
        if value.is_integer():
            return str(int(value))
        formatted_value = "{:,.2f}".format(value).replace(',', ' ').replace('.', ',').replace(' ', '.')
        if formatted_value.endswith(',00'):
            return formatted_value[:-3]
        return formatted_value
    except (ValueError, TypeError):
        return value

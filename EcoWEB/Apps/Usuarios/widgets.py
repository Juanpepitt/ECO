from django import forms

class CommaDecimalWidget(forms.TextInput):
    def format_value(self, value):
        if value is None:
            return ''
        return str(value).replace('.', ',')

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        if value:
            value = value.replace(',', '.')
        return value

from django import forms

from .widgets import BootstrapDateTimePickerInput, BootstrapDatePickerInput
from django.utils.formats import get_format


class DateTimeForm(forms.Form):
    date = forms.DateTimeField(
        input_formats=['%d.%m.%Y %H:%M'],
        widget=BootstrapDateTimePickerInput()
    )


class DateForm(forms.Form):
    date = forms.DateField(
        input_formats=['%d.%m.%Y'],
        widget=BootstrapDatePickerInput()
    )
    print(get_format('DATE_FORMAT'))

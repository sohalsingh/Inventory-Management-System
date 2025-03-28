from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity', 'price']

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")
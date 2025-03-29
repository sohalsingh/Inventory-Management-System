from django import forms
from .models import Order, OrderItem, Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'quantity', 'price']

class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Upload CSV File")

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "customer_email", "customer_phone", "customer_address", "payment_type"]

class OrderItemForm(forms.Form):
    items = forms.ModelMultipleChoiceField(queryset=Item.objects.all(), widget=forms.CheckboxSelectMultiple)  # ✅ Allow multiple selections
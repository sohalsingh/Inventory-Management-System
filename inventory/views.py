from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse
from .models import Item
from .forms import ItemForm, CSVUploadForm
import json
import csv

# ✅ Add Item View
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/add_item.html', {'form': form})

# ✅ Update Item View
def update_item(request, pk):  # ✅ Ensure function uses "pk"
    item = get_object_or_404(Item, id=pk)  # ✅ Ensure matching field name
    
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ItemForm(instance=item)

    return render(request, 'inventory/update_item.html', {'form': form})


# ✅ Correct Delete Item View
def delete_item(request, pk):  # ✅ Change "item_id" to "pk"
    item = get_object_or_404(Item, id=pk)  # ✅ Ensure matching field name
    if request.method == "POST":
        item.delete()
        return redirect('inventory_list')
    return render(request, 'inventory/delete_item.html', {'item': item})


# ✅ Signup View
def signup_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto-login after signup
            return redirect('inventory_list')
    else:
        form = UserCreationForm()
    return render(request, 'inventory/signup.html', {'form': form})

# ✅ Login View
def login_view(request):
    form = AuthenticationForm(request, data=request.POST)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inventory_list')

    return render(request, 'inventory/login.html', {'form': form})

# ✅ Logout View
def logout_view(request):
    logout(request)
    return redirect('login')

# ✅ Inventory List View
def inventory_list(request):
    items = Item.objects.all()
    
    # ✅ Extract product names & quantities
    labels = list(items.values_list('name', flat=True))
    data = list(items.values_list('quantity', flat=True))

    return render(request, 'inventory/inventory_list.html', {
        'items': items,
        'labels': json.dumps(labels),  # ✅ Ensure JSON format
        'data': json.dumps(data)       # ✅ Ensure JSON format
    })

# ✅ Import CSV File
def import_csv(request):
    if request.method == "POST":
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES["csv_file"]

            if not csv_file.name.endswith(".csv"):
                messages.error(request, "Invalid file format. Please upload a CSV file.")
                return redirect("inventory_list")

            try:
                decoded_file = csv_file.read().decode("utf-8").splitlines()
                reader = csv.reader(decoded_file)
                next(reader)  # ✅ Skip header row

                for row in reader:
                    name, quantity, price = row
                    Item.objects.create(name=name, quantity=int(quantity), price=float(price))

                messages.success(request, "Inventory data imported successfully!")
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

    return redirect("inventory_list")

# ✅ Export Inventory Data as CSV
def export_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="inventory_data.csv"'

    writer = csv.writer(response)
    writer.writerow(["Name", "Quantity", "Price"])  # ✅ CSV Header

    items = Item.objects.all().values_list("name", "quantity", "price")
    for item in items:
        writer.writerow(item)

    return response

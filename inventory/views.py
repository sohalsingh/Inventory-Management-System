import json
from django.shortcuts import render, redirect, get_object_or_404
from .models import Item
from .forms import ItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.http import HttpResponse  # ✅ For debugging

# Signup View
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

# Login View
def login_view(request):
    print("✅ login_view is being called")  # Debug message

    form = AuthenticationForm(request, data=request.POST)
    
    if request.method == "POST":
        print("✅ POST request detected")  # Debug message
        if form.is_valid():
            print("✅ Form is valid")  # Debug message
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                print("✅ User authenticated")  # Debug message
                login(request, user)
                return redirect('inventory_list')
            else:
                print("❌ User authentication failed")  # Debug message
        else:
            print("❌ Form is invalid")  # Debug message

    print("✅ Rendering login.html")  # Debug message
    return render(request, 'inventory/login.html', {'form': form})

# ✅ Fix: Add `logout_view`
def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout

# Protect inventory list with login_required
@login_required
def inventory_list(request):
    items = Item.objects.all()

    # ✅ Convert QuerySet to lists for Chart.js
    labels = list(items.values_list('name', flat=True))  
    data = list(items.values_list('quantity', flat=True))  

    # ✅ Debugging: Print values to check if they exist
    print("Labels:", labels)  
    print("Data:", data)  

    return render(request, 'inventory/inventory_list.html', {
        'items': items,
        'labels': json.dumps(labels),  # ✅ Convert to JSON for JavaScript
        'data': json.dumps(data)
    })
# Create New Item
def add_item(request):
    if request.method == "POST":
        form = ItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ItemForm()
    return render(request, 'inventory/add_item.html', {'form': form})


# Update Item
def update_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_list')
    else:
        form = ItemForm(instance=item)
    return render(request, 'inventory/update_item.html', {'form': form})

# Delete Item
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    if request.method == "POST":
        item.delete()
        return redirect('inventory_list')
    return render(request, 'inventory/delete_item.html', {'item': item})

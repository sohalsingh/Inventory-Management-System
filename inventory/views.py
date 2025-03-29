from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import HttpResponse
from .models import Item, Order, OrderItem
from .forms import ItemForm, CSVUploadForm, OrderForm, OrderItemForm
import json
import csv
from io import BytesIO 
from reportlab.lib.pagesizes import letter  # ✅ pdf size
from reportlab.pdfgen import canvas  # ✅ PDF Library
from decimal import Decimal  # ✅ Import Decimal
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet



# ✅ Checkout Page
def checkout(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save()  # ✅ Save Order

            # ✅ Process Multiple Items
            items = request.POST.getlist("item")
            quantities = request.POST.getlist("quantity")

            for item_id, quantity in zip(items, quantities):
                item = Item.objects.get(id=item_id)
                quantity = int(quantity)

                if item.quantity >= quantity:
                    OrderItem.objects.create(order=order, item=item, quantity=quantity)
                    item.quantity -= quantity  # ✅ Reduce stock
                    item.save()
                else:
                    return HttpResponse("Not enough stock available!")

            return redirect("invoice_pdf", order_id=order.id)

    else:
        order_form = OrderForm()
        order_item_form = OrderItemForm()

    return render(request, "inventory/checkout.html", {
        "order_form": order_form,
        "order_item_form": order_item_form
    })

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
    writer.writerow(["Name", "Quantity", "Price (₹)"])  # ✅ CSV Header

    items = Item.objects.all().values_list("name", "quantity", "price")
    for item in items:
        writer.writerow(item)

    return response

def checkout(request):
    if request.method == "POST":
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save()  # ✅ Save Order

            # ✅ Process Multiple Items with Different Quantities
            selected_items = request.POST.getlist("items")

            for item_id in selected_items:
                quantity_key = f"quantity_{item_id}"
                quantity = int(request.POST.get(quantity_key, 1))  # Default 1 if missing
                item = Item.objects.get(id=item_id)

                if item.quantity >= quantity:
                    OrderItem.objects.create(order=order, item=item, quantity=quantity)
                    item.quantity -= quantity  # ✅ Reduce stock
                    item.save()
                else:
                    return HttpResponse("Not enough stock available!")

            return redirect("invoice_pdf", order_id=order.id)

    else:
        order_form = OrderForm()
        order_item_form = OrderItemForm()

    return render(request, "inventory/checkout.html", {
        "order_form": order_form,
        "order_item_form": order_item_form
    })

def invoice_pdf(request, order_id):
    order = Order.objects.get(id=order_id)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    elements = []  # ✅ Store PDF elements

    styles = getSampleStyleSheet()
    
    # ✅ Title
    elements.append(Paragraph(f"Invoice for Order #{order.id}", styles["Title"]))
    elements.append(Paragraph(f"Customer: {order.customer_name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {order.customer_email}", styles["Normal"]))
    elements.append(Paragraph(f"Phone: {order.customer_phone}", styles["Normal"]))
    elements.append(Paragraph(f"Address: {order.customer_address}", styles["Normal"]))
    
    elements.append(Paragraph("<br/><br/>", styles["Normal"]))  # ✅ Space before table

    # ✅ Table Data (Header Row)
    data = [
        ["Item Name", "Quantity", "Unit Price (INR)", "Total Price (INR)"]
    ]

    total_amount = Decimal("0.00")

    # ✅ Adding Each Item to the Table
    for order_item in order.items.all():
        item_total = order_item.quantity * order_item.item.price
        total_amount += Decimal(item_total)  # ✅ Ensure Decimal type
        data.append([
            order_item.item.name,
            str(order_item.quantity),
            f"{order_item.item.price:.2f}",
            f"{item_total:.2f}",
        ])

    gst_rate = Decimal("0.18")
    gst_amount = total_amount * gst_rate
    grand_total = total_amount + gst_amount

    # ✅ Add Totals to Table
    data.append(["", "", "Subtotal:", f"{total_amount:.2f}"])
    data.append(["", "", "GST (18%):", f"{gst_amount:.2f}"])
    data.append(["", "", "Grand Total:", f"{grand_total:.2f}"])

    # ✅ Create Table & Styling
    table = Table(data, colWidths=[2.5 * inch, 1 * inch, 1.5 * inch, 1.5 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # ✅ Header Row Grey
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),  # ✅ White Text
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # ✅ Center Align Text
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),  # ✅ Bold Header
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),  # ✅ Space Below Header
        ("GRID", (0, 0), (-1, -1), 1, colors.black),  # ✅ Black Grid Lines
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),  # ✅ Light Background
    ]))

    elements.append(table)  # ✅ Add Table to PDF

    doc.build(elements)  # ✅ Build the PDF

    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{order.id}.pdf"'
    return response
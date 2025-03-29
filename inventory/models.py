from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=15, blank=True, null=True)  # ✅ Allows empty values
    customer_address = models.TextField(blank=True, null=True)  # ✅ Allows empty values
    payment_type = models.CharField(max_length=10, choices=[("Cash", "Cash"), ("UPI", "UPI"), ("Card", "Card")])
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):  # ✅ Calculates total price for all items
        return sum(item.get_total() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)  # ✅ Ensure this field exists
    quantity = models.PositiveIntegerField()

    def get_total(self):
        return self.item.price * self.quantity  # ✅ Use 'item' instead of 'product'


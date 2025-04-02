from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from .views import signup_view, login_view, logout_view, inventory_list, add_item, update_item, delete_item, import_csv, export_csv, checkout, invoice_pdf, generate_upi_qr
urlpatterns = [
    path('', inventory_list, name='inventory_list'),
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('add/', add_item, name='add_item'),
    path("update/<int:pk>/", update_item, name="update_item"),  # ✅ Change "item_id" to "pk"
    path('delete/<int:pk>/', delete_item, name='delete_item'),
    path('import_csv/', import_csv, name='import_csv'),  # ✅ New URL for CSV import
    path("export_csv/", export_csv, name="export_csv"),  # ✅ Export CSV Route
    path("checkout/", checkout, name="checkout"),
    path("invoice/<int:order_id>/", invoice_pdf, name="invoice_pdf"),
    path("generate-qr/", generate_upi_qr, name="generate_upi_qr"),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

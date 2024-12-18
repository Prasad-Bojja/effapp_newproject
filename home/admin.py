from django.contrib import admin
from .models import PaymentTransaction
# Register your models here.

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
  list_display = ('order_id', 'first_name','email_id','mobile','base_amount', 'create_at')
  search_fields = ('order_id', 'first_name','email_id','mobile')
from django.db import models


# Choices for payment status
STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('SUCCESS', 'Success'),
    ('FAILED', 'Failed'),
]

class PaymentTransaction(models.Model):
    order_id = models.CharField(max_length=50)
    amount = models.IntegerField(blank=True, null=True)
    base_amount = models.IntegerField(default=0)
    payment_link = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    response_code = models.CharField(max_length=20, blank=True, null=True)
    message = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    email_id = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=100, blank=True, null=True)
    payment_instrument = models.JSONField(blank=True, null=True)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    create_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.email_id} - {self.order_id} - {self.status}"

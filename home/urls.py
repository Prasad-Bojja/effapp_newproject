from django.urls import path
from .views import create_payment_transaction,login_view,payment_status,home


urlpatterns = [
   
    path('create_payment_transaction/', create_payment_transaction, name='create_payment_transaction'),
    #path('', login_view, name='login'),
    path('payment-status/', payment_status, name='payment_status'),
    path('',home,name='home')
    #path('download-pdf/<str:order_id>/', download_pdf, name='download_pdf'),
    #path('download_pdf_in_phonepe_transaction/<str:order_id>/', download_pdf_in_phonepe_transaction, name='download_pdf_in_phonepe_transaction'),


]


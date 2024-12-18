import os
from dotenv import load_dotenv
load_dotenv()

MERCHANT_ID= os.getenv('MERCHANT_ID')
PHONE_PE_SALT = os.getenv('PHONE_PE_SALT')
PHONE_PE_HOST = os.getenv('PHONE_PE_HOST')
DJANGO_CUSTOM_REDIRECT_URL =os.getenv('DJANGO_CUSTOM_REDIRECT_URL')
DJANGO_CUSTOM_CALLBACK_URL = os.getenv('DJANGO_CUSTOM_CALLBACK_URL')
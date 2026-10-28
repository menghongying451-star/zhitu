from django.urls import path
from . import views

app_name = 'pdf_processing'

urlpatterns = [
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
]
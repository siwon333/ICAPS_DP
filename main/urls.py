from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'), # Home page
    path('issues/', views.issues, name='issues'), # Health issues page
    path('order/', views.order, name='order'),# How to order Jamu page
    path('info/', views.info, name='info'), # Description of Jamu page
    path('waiting/', views.waiting, name='waiting'), # Waiting page
    path('complete/', views.complete, name='complete'), # complete page
    path('chatbot/', views.chatbot, name='chatbot'), # Chatbot page
    
    # API endpoints
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('api/order-status/', views.order_status_api, name='order_status_api'),
]
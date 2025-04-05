from django.urls import path
from .views import HelloWorldAPIView

app_name = 'members'

urlpatterns = [
    path('hello/', HelloWorldAPIView.as_view(), name='hello_world'),
]

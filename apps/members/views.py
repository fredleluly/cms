from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import HelloWorldSerializer


class HelloWorldAPIView(APIView):
    """
    A simple API view that returns a hello world message
    """
    
    def get(self, request, format=None):
        """
        Return a simple hello world message
        """
        content = {'message': 'Hello, World!'}
        return Response(content)
    
    def post(self, request, format=None):
        """
        Return a personalized hello message with the provided name
        """
        serializer = HelloWorldSerializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data.get('your_name', 'World')
            content = {'message': f'Hello, {name}!'}
            return Response(content)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

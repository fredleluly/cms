from rest_framework import serializers


class HelloWorldSerializer(serializers.Serializer):
    """
    A simple serializer for our hello world API endpoint
    """
    message = serializers.CharField(read_only=True)
    your_name = serializers.CharField(required=False, max_length=100)

from django.shortcuts import render
from django.core.cache import cache
from django.conf import settings
from django.urls import reverse
from .models import MaintenanceMode

class MaintenanceModeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Paths that should always be accessible
        exempt_paths = [
            reverse('admin:index'),
            '/admin/login/',
            '/static/',
            '/media/',
        ]
        
        # Check if current path is exempt
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)

        # Get maintenance status from cache
        maintenance_mode = cache.get('maintenance_mode')
        if not maintenance_mode:
            try:
                mode = MaintenanceMode.objects.first()
                if mode:
                    maintenance_mode = {
                        'is_active': mode.is_active,
                        'message': mode.message,
                        'allowed_ips': [ip.strip() for ip in mode.allowed_ips.split(',') if ip.strip()]
                    }
                    cache.set('maintenance_mode', maintenance_mode)
            except:
                return self.get_response(request)

        if maintenance_mode and maintenance_mode['is_active']:
            # Allow staff members
            if request.user.is_authenticated and request.user.is_staff:
                return self.get_response(request)

            # Check IP address
            client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            if client_ip in maintenance_mode.get('allowed_ips', []):
                return self.get_response(request)

            # Show maintenance page
            context = {
                'maintenance_message': maintenance_mode['message']
            }
            return render(request, 'maintenance.html', context, status=503)

        return self.get_response(request) 
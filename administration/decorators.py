import json
from functools import wraps
from rest_framework.response import Response
from rest_framework import status


def parse_json(view_func):
    """Decorator which parse json from request.body to request.json"""

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            if request.body:
                try:
                    request.json = json.loads(request.body.decode())
                except ValueError:
                    return Response({'errors': 'Invalid JSON input'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                request.json = {}
        return view_func(request, *args, **kwargs)

    return _wrapped_view

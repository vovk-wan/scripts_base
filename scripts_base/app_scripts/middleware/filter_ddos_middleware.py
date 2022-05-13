from typing import Dict, List
from django.core.exceptions import PermissionDenied
from time import time


class FilterDdosMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.number_requests_for_ip: Dict[str, List[time]] = dict()

    def __call__(self, request, *args, **kwargs):
        ip = request.META.get('REMOTE_ADDR')
        self.number_requests_for_ip.setdefault(ip, [])
        n_sec = 5
        self.number_requests_for_ip[ip].append(time())
        n_requests = len(list(filter(lambda x: time() - x <= n_sec, self.number_requests_for_ip.get(ip, []))))

        if n_requests > 5:
            raise PermissionDenied

        response = self.get_response(request)

        return response

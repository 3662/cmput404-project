import json

from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator, EmptyPage
from django.http import JsonResponse, HttpResponse, Http404
from django.views import View
from posts.forms import PostForm
from django.core.exceptions import ValidationError

from service.server_authorization import is_server_authorized, is_local_server, get_401_response
from service.models import ServerNode
import requests
from urllib.parse import urlparse



class ProxyView(View):
    http_method_names = ['get', 'head', 'options', 'post']

    def get(self, request):
        '''
        GET [local]: Makes a GET request on behalf of the frontend.

        Returns: 
            - 200: if the request is successful
            - 400: if the data is invalid
            - 404: if the response is not in valid JSON
            - Other: foreign nodes might return other statuses 
        '''
        if not is_server_authorized(request):
            return get_401_response()

        url = request.GET.get('url')
        if not '/authors' in url:
            return JsonResponse({'detail': f'This path is not supported'}, status=400)

        return self._do_proxy(url, 'GET')

    def head(self, request):
        '''
        Handles HEAD request of the same GET request.

        Returns: 
            - 200: if the request is successful
            - 400: if the data is invalid
            - 404: if the response is not in valid JSON
            - Other: foreign nodes might return other statuses 
        '''
        if not is_server_authorized(request):
            return get_401_response()

        url = request.GET.get('url')
        if not '/authors' in url:
            return JsonResponse({'detail': f'This path is not supported'}, status=400)

        response = self._do_proxy(url, 'GET')
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Length'] = str(len(bytes(data_json, 'utf-8')))

        return response
        

    def post(self, request):
        '''
        POST [local]: Makes a POST request on behalf of the frontend

        Returns: 
            - 200: if the request is successful
            - 400: if the data is invalid
            - 404: if the response is not in valid JSON
            - Other: foreign nodes might return other statuses 
        '''
        if not is_local_server(request):
            return get_401_response()
        
        url = request.GET.get('url')

        if not (url.endswith('/inbox') or url.endswith('/inbox/')):
            return JsonResponse({
                'detail': f'This path is not supported'
            }, status=400)

        return self._do_proxy(url, 'POST', data=request.body)

    def _do_proxy(self, url, method, data=None):
        '''Makes a request on behalf of the frontend'''
        auth = self._get_auth_or_none(url)
        if not auth:
            return JsonResponse({
                'detail': f'The node {url} needs to be connected by serveradmin first'
            }, status=400)
        
        proxy_response = None
        if method == 'GET':
            proxy_response = requests.get(url, auth=auth)
        elif method == 'POST':
            proxy_response = requests.post(url, auth=auth, data=data)
        
        data = {}
        try:
            data = proxy_response.json()
        except:
            return JsonResponse(
                {'detail': 'The request returned a non-JSON response'},
                status=404
            )
    
        return JsonResponse(data, status=proxy_response.status_code)

    
    def _get_auth_or_none(self, url):        
        auth = None
        host = urlparse(url).netloc
        for node in ServerNode.objects.all():
            if host in node.host:
                auth = (node.sending_username, node.sending_password)
                break
        return auth


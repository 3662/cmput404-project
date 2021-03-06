import base64

from django.http import HttpResponse
from django.http.request import HttpRequest
from django.conf import settings

from service.models import ServerNode


def get_401_response() -> HttpResponse:
    '''
    Returns a HttpResponse with WWW_Authenticate header and 401 status code.
    '''
    response = HttpResponse(status=401)
    response.headers['WWW-Authenticate'] = 'Basic realm="Group 09"'
    return response


def is_server_authorized(request: HttpRequest) -> ServerNode:
    '''
    Given a HttpRequest, returns True if the server is authorized. Otherwise, False.

    The server is authorized if Authorization header is included with valid credentials.
    '''

    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if auth_header is None:
        return None

    auth_type, auth_info = auth_header.split(' ')

    if auth_type.lower() != "basic":
        return None

    auth_info = auth_info.encode('utf-8')
    try:
        username, password = base64.b64decode(auth_info).decode('utf-8').split(':')
    except ValueError:
        return None
    node_q = ServerNode.objects.filter(receiving_username=username, receiving_password=password)

    return node_q.get() if node_q.exists() else None


def is_local_server(request: HttpRequest) -> bool:
    '''
    Returns True if the server is a local server. Otherwise, False.
    '''
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if auth_header is None:
        return None

    auth_type, auth_info = auth_header.split(' ')

    if auth_type.lower() != "basic":
        return None

    auth_info = auth_info.encode('utf-8')
    try:
        username, password = base64.b64decode(auth_info).decode('utf-8').split(':')
    except ValueError:
        return None
    node_q = ServerNode.objects.filter(receiving_username=username, receiving_password=password, is_local=True)

    return node_q.get() if node_q.exists() else None

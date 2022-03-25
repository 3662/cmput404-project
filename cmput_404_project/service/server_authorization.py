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


def get_403_response() -> HttpResponse:
    '''
    Returns a HttpResponse with 403 status code.
    '''
    message = "You do not have a permission"
    response = HttpResponse(message, status=403)
    return response


def is_server_authorized(request: HttpRequest) -> bool:
    '''
    Given a HttpRequest, returns True if the server is authorized. Otherwise, False.

    The server is authorized if
        - it is local server, or
        - Authorization header is included with valid credentials.
    '''
    host = request.get_host()
    node_q = ServerNode.objects.filter(host=host)

    if not node_q.exists():
        return False

    node = node_q.get()
    if node.is_local:
        return True

    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if auth_header is None:
        return False

    auth_type, auth_info = auth_header.split(' ')

    if auth_type.lower() != "basic":
        return False

    auth_info = auth_info.encode('utf-8')
    try:
        username, password = base64.b64decode(auth_info).decode('utf-8').split(':')
    except ValueError:
        return False

    return (username == node.receiving_username) and (password == node.receiving_password)


def is_local_server(request: HttpRequest) -> bool:
    '''
    Returns True if the server is a local server. Otherwise, False.
    '''
    host = request.get_host()
    node_q = ServerNode.objects.filter(host=host)

    if not node_q.exists():
        return False

    node = node_q.get()
    return node.is_local
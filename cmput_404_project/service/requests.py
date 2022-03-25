import base64

from service.models import ServerNode

def get_b64_server_credential(server_host: str):
    '''
    If server_host is in ServerNode and is not a local server, 
    it returns a string with base64 encoded username and password 
    that can be used to put in "Authorization:" header.

    If server_host is either no in ServerNode or is a local server, 
    it returns None.

    Example server_host: 
        - 127:0:0:1:5000
        - cmput-404-w22-project-group09.herokuapp.com

    Example Usage:

        b64_authorization = get_b64_server_credential(host)
        if b64_authorization:
            headers['Authorization'] = b64_authorization

    '''
    q = ServerNode.objects.filter(host=server_host)
    node = None
    if q.exists():
        node = q.get()
    
    # server_host does not exist or is a local server
    if (node is None) or node.is_local:
        return None 

    credential = f"{node.username}:{node.password}".encode("utf-8")
    b64_crediential = base64.b64encode(credential)

    return f"Basic {b64_crediential.decode('utf-8')}"

    


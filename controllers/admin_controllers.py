#from ..server import *
import sys
from os import path
import os

def print_ok():
    print("ruta: ",sys.path.append(path.join(path.dirname(__file__), '..')))
    x =  sys.path
    print("x: ",x)


'''
def gets_admin(environ, path):    
    path = '/'+path
    if path == "/registrar_cliente":
        data = get_registro_cliente(environ)

    # Los siguientes dos metodos pertenecen a los auditores tambien
    elif path == "/show_users":
        data = show_users(environ)

    elif path == "/movimientos":
        data = get_total_movimientos(environ)

    elif path == "/sobregiros":
        data = get_sobregiros(environ)

    elif path == "/informacion_dinero":
        data = get_all_money(environ)

    elif path.startswith("/client"):
        params = path.split("/")
        data = get_user_info_by_nit(environ, params[-1])

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data
    '''
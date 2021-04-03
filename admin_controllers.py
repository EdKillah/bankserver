from admin_services import *

#from server import get_registro_cliente, show_users, get_total_movimientos, get_sobregiros, get_all_money, get_user_info_by_nit, render_template, templates

def gets_admin(environ, path):    
    path = '/'+path    
    print("\n PATH EN GET ADMIN: {}  \n".format(path))
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
    

def posts_admin(environ, path):
    path = '/'+path
    if ((path == "/registrar_cliente") & (environ.get("REQUEST_METHOD") == 'POST')):
        data = registro_cliente(environ)
    
    elif(path == "/modificar_saldo"):
        data = modificar_saldo(environ)

    elif(path == "/autorizar_sobregiro"):
        data = autorizar_sobregiro(environ)

    return data

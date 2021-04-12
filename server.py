import urllib.parse
from pymongo import MongoClient
import json
from datetime import datetime
from persistence.databases import *
#from controllers.admin_controllers import *
from admin_controllers import *
from general_services import *
from usuario_activo import *

templates = get_templates_route()

'''
    comienza a funcionar todo pero hay problema con validación del usuario activo,
    se tarda mucho y lo toma como nulo 
    validar directamente sobre los metodos en vez de llamar a general_services
'''


'''
    Mapeadores de rutas
'''

# Unicamente gets


def home(environ):
    return render_template(
        template_name=templates+'index.html',
        context={'message': ''}
    )


def registro_usuario(environ):
    return render_template(
        template_name=templates+'create_account.html',
        context={}
    )


def get_login(environ):
    return render_template(
        template_name=templates+'login.html',
        context={}
    )


def get_movimientos_cliente(environ):
    usuario_activo = get_usuario_activo()
    collections = transactions_db()
    results = collections.find(
        {'cuenta_origen': usuario_activo['user_nit']})
    movimientos = find_all(results)
    retiros_collection = retiros_db()
    resultados = retiros_collection.find(
        {'usuario_retiro': usuario_activo['user_nit']})
    retiros = find_all(resultados)
    return render_template(
        template_name=templates+'movimientos_cliente.html',
        context={'movimientos': movimientos, 'retiros': retiros}
    )




def get_transaction_view(environ):
    usuario_activo = get_usuario_activo()
    user = ''
    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    return render_template(
        template_name=templates+'transaction_form.html',
        context={'message': '', 'user': user, 'saldo': usuario_activo['saldo']}
    )


def get_retiro_view(environ):
    usuario_activo = get_usuario_activo()
    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = users_db()
    usuario = collections.find_one({'user_nit': usuario_activo['user_nit']})
    return render_template(
        template_name=templates+'retiro.html',
        context={'user': user, 'saldo': usuario['saldo'], 'message': ''}
    )



def get_sobregiro_view(environ):
    usuario_activo = get_usuario_activo()
    user = 'Usuario: ' + \
        usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = users_db()
    usuario = collections.find_one(
        {'user_nit': usuario_activo['user_nit']})
    return render_template(
        template_name=templates+'solicitar_sobregiro.html',
        context={'user': user, 'saldo': usuario['saldo'], 'message': ''}
    )


def get_sobregiros_auditor(environ):
    usuario_activo = get_usuario_activo()
    user = 'Usuario: '+usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = sobregiros_db()
    results = collections.find()
    sobregiros = find_all(results)
    return render_template(
        template_name=templates+'sobregiros_auditor.html',
        context={'user': user, 'message': '', 'sobregiros': sobregiros}
    )


# POST UNICAMENTE


def create_user(environ):

    json = get_json_decoded(environ)
    user = get_user_by_nit(json['nit'])

    if(user != None):
        collections = users_db()
        user['user_mail'] = json['email']
        user['user_password'] = json['password']
        collections.insert_one(user)
        return render_template(
            template_name=templates+'login.html',
            context={}
        )
    else:
        return render_template(
            template_name=templates+'index.html',
            context={"message": "Usuario no activo."}
        )


def login(environ):
    #global usuario_activo
    json = get_json_decoded(environ)
    
    user = get_user_by_mail(json['user_mail'], 'users')
    message = {'message': 'Usuario o contraseña incorrectos!'}

    if(user != None):
        if(user['user_password'] == json['user_password']):
            message['message'] = 'Logueado con exito!'
            #usuario_activo = user
            set_usuario_activo(user)

        return render_template(
            template_name=templates+'index.html',
            context={'message': message['message']}
        )
    else:
        user = get_user_by_mail(json['user_mail'], 'administrators')
        if(user!=None):
            if(user['user_password'] == json['user_password']):
                message['message'] = 'Logueado con exito!'
                #usuario_activo = user                
                set_usuario_activo(user)
        else:
            user = get_user_by_mail(json['user_mail'], 'auditors')
            if(user!=None):
                if(user['user_password'] == json['user_password']):
                    message['message'] = 'Logueado con exito!'
                    set_usuario_activo(user)
                    #usuario_activo = user                
        return render_template(
            template_name=templates+'index.html',
            context={'message': message['message']}
        )



def get_date_now():
    now = datetime.now()
    fecha = "{}/{}/{} - {}:{}:{}".format(now.day, now.month,
                                         now.year, now.hour, now.minute, now.second)
    return fecha


def prepare_transaction(json):
    monto = int(json['monto'])
    usuario_activo = get_usuario_activo()
    if(usuario_activo['saldo'] >= monto):        
        json["cuenta_origen"] = usuario_activo['user_nit']
        json["fecha"] = get_date_now()
        collection = users_db()
        collection.update_one({"user_nit": json['cuenta_destino']}, {
                              "$inc": {"saldo": monto}})
        collection.update_one({"user_nit": json['cuenta_origen']}, {
                              "$inc": {"saldo": -monto}})

        del json['password']
        return json
    return None


def make_transaction(environ):
    usuario_activo = get_usuario_activo()
    json = get_json_decoded(environ)
    if compare_passwords(json['password'], usuario_activo['user_password']):
        print("LAS CONTRASEÑAS SON LAS MISMAS: ",json['password'])
        if exists_user(json['cuenta_destino']):
            json = prepare_transaction(json)
            if(json != None):
                collections = transactions_db()
                collections.insert_one(json)
        else:
            return render_template(
                template_name=templates+'transaction_form.html',
                context={'message': 'El destinatario no existe', 'user': usuario_activo['user_name']+usuario_activo['user_lastname'], 'saldo':usuario_activo['saldo'] })
    else:
        print("LAS CONTRASEÑAS NO SON LO MISMO!!!: ",json["password"],usuario_activo['user_password'])
        #context={'message': '', 'user': user, 'saldo': usuario_activo['saldo']}
        return render_template(
            template_name=templates+'transaction_form.html',
            context={'message': 'Contraseña incorrecta.',
                     'user': usuario_activo['user_name']+usuario_activo['user_lastname'], 'saldo':usuario_activo['saldo']}
        )
    print("paso del ELSE LE DA IGUAL******************")
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Realizo la transaccion'}
    )


def solicitar_sobregiro(environ):
    usuario_activo = get_usuario_activo()
    json = get_json_decoded(environ)
    json['solicitante'] = usuario_activo['user_nit']
    collections = sobregiros_activos_db()
    print("\n COLLECTIONS EN SOLICITAR SOBREGIRO USUARIO: ",collections, "\n")
    tiene_sobregiro= collections.find_one({'solicitante': usuario_activo['user_nit']})
    
    if(tiene_sobregiro==None):
        collections.insert_one(json)
        message = 'Ha solicitado un sobregiro'
    else:
        message = 'TIENE SOBREGIROS PENDIENTES, NO SE REALIZO SOBREGIRO.'
    return render_template(
        template_name=templates+'index.html',
        context={'message': message}
    )



def hacer_retiro(environ):
    usuario_activo = get_usuario_activo()
    json = get_json_decoded(environ)
    if compare_passwords(json['password'], usuario_activo['user_password']):
        user_collection = users_db()
        retiros_collection = retiros_db()
        cash = int(json['monto'])

        user_collection.update_one({"user_nit": usuario_activo['user_nit']}, {
                               "$inc": {"saldo": -cash}})

        json['usuario_retiro'] = usuario_activo['user_nit']
        json['monto'] = cash
        json['fecha'] = get_date_now()
        del json['password']
        retiros_collection.insert_one(json)
    else:
        print("LAS CONTRASEÑAS NO SON LO MISMO!!!: ",json["password"],usuario_activo['user_password'])
        #context={'message': '', 'user': user, 'saldo': usuario_activo['saldo']}
        return render_template(
            template_name=templates+'retiro.html',
            context={'message': 'Contraseña incorrecta.',
                     'user': usuario_activo['user_name']+usuario_activo['user_lastname'], 'saldo':usuario_activo['saldo']}
        )
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Ha realizado un retiro.'}
    )


def create_administrator(environ):
    
    json = get_json_decoded(environ)
    #collection = administrators_db()
    collection = auditors_db()
    collection.insert_one(json)
    return render_template(
        template_name=templates+'index.html',
        context={'message': 'Se creo el auditor.'}
    )




def posts(environ, path):

    if ((path == "/login")):
        data = login(environ)


    elif(path == "/make_transaction"):
        data = make_transaction(environ)

    elif(path == "/retiro"):
        data = hacer_retiro(environ)

    elif(path == "/solicitar_sobregiro"):
        data = solicitar_sobregiro(environ)

    return data




def gets(environ, path):
    if path == "":
        data = home(environ)

    elif path == "/login":
        data = get_login(environ)
    
    elif path == "/transferencia":
        data = get_transaction_view(environ)

    elif path == "/mis_movimientos":
        data = get_movimientos_cliente(environ)

    elif path == "/retiro":
        data = get_retiro_view(environ)

    elif path == "/solicitar_sobregiro":
        data = get_sobregiro_view(environ)

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data





def gets_auditor(environ, path):

    path = '/'+path        

    if path == "/movimientos":
        data = get_total_movimientos(environ)

    elif path == "/sobregiros":
        data = get_sobregiros_auditor(environ)

    elif path == "/informacion_dinero":
        data = get_all_money(environ)    

    else:
        data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    return data    



def prueba(environ, start_response):
    headers = [('content-type', 'application/json'), ('Access-Control-Allow-Origin', '*'),
                ('Access-Control-Allow-Headers', 'Authorization, Content-Type'),
                ('Access-Control-Allow-Methods', 'POST')]
    test = json.dumps(['foo', {'bar': ('baz', None, 1.0, 2)}])    
    test1 = bytes(test, 'utf-8') # or test.encode('utf-8')
    start_response('200 OK', headers)
    return [test1]


# Ejecutor de aplicacion


def app(environ, start_response):
    usuario_activo = get_usuario_activo()
    print("usuario activo app: ",usuario_activo)

    path = environ.get("PATH_INFO")
    print("path: ", path)
    if path.endswith("/"):
        path = path[:-1]
    if(environ.get("REQUEST_METHOD") == 'POST') & (path == '/login') & (usuario_activo == None):
        data = login(environ)
    
    if(environ.get("REQUEST_METHOD") == 'GET'):
        if(path=='/json'):
            print("ENTRA EN JSON PATH! VA A RETORNAR EL JSON")
            return prueba(environ, start_response)

    if(usuario_activo != None): #validate_user()
        #print("EL USUARIO ESTA LOGUEADO: ",usuario_activo, "PATh: ",path)
        #print("tipo usuario activo: ",type(usuario_activo))
        if(environ.get("REQUEST_METHOD") == 'POST'):
            if(path.startswith("/admin") & (usuario_activo['rol_user'] == 'admin')):
                params = path.split("/")
                ruta = params[-1]
                data = posts_admin(environ, ruta)                            

            else:
                data = posts(environ, path)

        elif(environ.get("REQUEST_METHOD") == 'GET'):            
            ##Metodo de prueba de json:
            if(path=='/json'):
                print("ENTRA EN JSON PATH! VA A RETORNAR EL JSON")
                return prueba(environ, start_response)
            if(path.startswith("/admin") & (usuario_activo['rol_user'] == 'admin')):
                params = path.split("/")
                if((len(params) > 3) & (params[2] == 'client')):
                    ruta = params[2]+'/'+params[3]                    
                else:
                    ruta = params[-1]
                data = gets_admin(environ, ruta)

            elif(path.startswith("/auditor") & (usuario_activo['rol_user'] == 'auditor')):
                params = path.split("/")
                ruta = params[-1]
                data = gets_auditor(environ, ruta)
            else:
                data = gets(environ, path)

    else:
        print("NO ESTA LOGUEADO: ",path)
        if path == "/registrar_cuenta":
            data = registro_usuario(environ)
        elif ((path == "/create_account")):            
            data = create_user(environ)
            #data = create_administrator(environ)
        elif ((path == "/login") & (environ.get("REQUEST_METHOD") == 'GET')):
            data = get_login(environ)
        elif (path == ""):
            data = get_login(environ)
        else:
            data = render_template(template_name=templates +
                               '404.html', context={"path": path})

    data = data.encode("utf-8")
    start_response(
        f"200 OK", [
            ("Content-Type", "text/html"),
            ("Content-Length", str(len(data)))
        ]
    )
    return iter([data])
 
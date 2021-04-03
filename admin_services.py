from persistence.databases import *
from general_services import *
from usuario_activo import *

templates = get_templates_route()

def get_registro_cliente(environ):
    return render_template(
        template_name=templates+'registro_cliente.html',
        context={}
    )

def show_users(environ):

    collections = init_db()
    results = collections.find()

    users = find_all(results)

    return render_template(
        template_name=templates+'users.html',
        context={"usuarios": users}
    )

def get_total_movimientos(environ):

    movimientos, total_transacciones = get_movimientos()
    numero_transacciones = len(movimientos)
    retiros, total_retiros = get_total_retiros()
    numero_retiros = len(retiros)
    return render_template(
        template_name=templates+'movements.html',
        context={'movimientos': movimientos, 'numero_transacciones': numero_transacciones,
                 'total_transacciones': total_transacciones, 'retiros': retiros, 'total_retiros':total_retiros,'numero_retiros':numero_retiros}
    )


def get_sobregiros(environ):
    usuario_activo = get_usuario_activo()
    print("\n USUARIO ACTIVO EN ADMIN SOBREGIROS: ",usuario_activo," \n")
    user = 'Usuario: '+usuario_activo['user_name']+' '+usuario_activo['user_lastname']
    collections = sobregiros_activos_db()
    results = collections.find()
    sobregiros = find_all(results)
    return render_template(
        template_name=templates+'sobregiros.html',
        context={'user': user, 'message': '', 'sobregiros': sobregiros}
    )

def get_all_money(environ):

    collection = users_db()
    results = collection.find()
    dinero = find_all(results)
    dinero_total = 0
    for x in dinero:
        dinero_total += float(dinero[x]['saldo'])
    

    return render_template(
        template_name=templates+'dinero.html',
        context={'dinero_disponible': dinero_total}
    )


def get_user_info_by_nit(environ, nit):

    usuario = get_client_by_nit(nit)
    del usuario['_id']
    del usuario['user_password']
    return render_template(
        template_name=templates+'user_info.html',
        context={'user': usuario}
    )


def get_movimientos():
    collections = transactions_db()
    results = collections.find()
    movimientos = find_all(results)
    total = 0

    for movimiento in movimientos:
        total += float(movimientos[movimiento]['monto'])

    return movimientos, total


def get_client_by_nit(nit):
    collections = users_db()
    result = collections.find_one({"user_nit": nit})
    return result



def get_total_retiros():
    collection = retiros_db()
    results = collection.find()
    retiros = find_all(results)
    total = 0
    for retiro in retiros:
        total += float(retiros[retiro]['monto'])

    return retiros, total


#POSTS

def registro_cliente(environ):

    # validar que el cliente no este repetido C.C
    message = "El cliente ya existe"
    json = get_json_decoded(environ)
    json['saldo'] = 100000
    
    collections = init_db()
    exists_user = collections.find_one({'user_nit' : json['user_nit']})
    print("USUARIO EXISTE: ",exists_user)
    if(exists_user == None):
        collections.insert_one(json)
        message = "Cliente creador con exito"
        print("Va a crear el usuario")

    return render_template(
        template_name=templates+'index.html',
        context={'message': message}
    )


def modificar_saldo(environ):
    
    json = get_json_decoded(environ)
    if(exists_user(json['user_nit'])):
        collections = users_db()
        cash = int(json['new_cash'])
        collections.update_one({"user_nit": json['user_nit']}, {
                               "$inc": {"saldo": cash}})
    else:
        return render_template(
            template_name=templates+'index.html',
            context={'message': 'Ha ocurrido un problema.'}
        )

    return render_template(
        template_name=templates+'index.html',
        context={'message': 'modifico un saldo.'}
    )


def autorizar_sobregiro(environ):
    print("ENTRANDO EN AUTORIZAR SOBREGIRO")
    usuario_activo = get_usuario_activo()
    json = get_json_decoded(environ)
    print("\n json en aturoizar sobregiro {} :".format(json),"\n")    
    collections = sobregiros_activos_db()
    print("\nSOLICITANTE: ",collections.find_one({"solicitante": json['nit_solicitante']}),"\n")
    sobregiro = collections.find_one({"solicitante": json['nit_solicitante']})
    sobregiro['estado'] = json['estado_sobregiro']
    sobregiro['revisador_por'] = usuario_activo['user_name']+" "+usuario_activo['user_lastname']
    print("\n SOBRGIRO: ",sobregiro,"\n")
    historial_sobregiros = sobregiros_db()
    historial_sobregiros.insert(sobregiro)
    collections.remove({"solicitante":sobregiro['solicitante']})
    '''
    collections.update_one({"solicitante": json['nit_solicitante']}, {
        "$set": {"estado": json['estado_sobregiro']}})
    collections.update_one({"solicitante": json['nit_solicitante']}, {"$set": {
        "revisado_por": usuario_activo['user_name']+" "+usuario_activo['user_lastname']}})
    '''
    results = collections.find()
    sobregiros = find_all(results)
    print("Sobregiros final: ",sobregiros)
    
    return render_template(
        template_name=templates+'sobregiros.html',
        context={'message': '', 'sobregiros': sobregiros}
    )


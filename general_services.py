import urllib.parse
from persistence.databases import *
from usuario_activo import *


def find_all(results):
    data = {}
    cont = 0
    for r in results:
        r.pop('_id')
        data[cont] = r
        cont += 1
    return data


def get_json_decoded(environ):
    request_body_size = get_request_body_size(environ)
    request_body = environ['wsgi.input'].read(request_body_size)
    json_body = urllib.parse.parse_qs(request_body)
    json_decode = {}
    for i in json_body:
        json_decode[i.decode('utf-8')] = json_body[i][0].decode('utf-8')
    return json_decode




def exists_user(user_nit):
    collections = users_db()
    result = collections.find_one({'user_nit': user_nit})
    band = False
    if result != None:
        band = True
    return band


def get_request_body_size(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    return request_body_size



def get_user_by_mail(mail, db):
    
    if(db == 'administrators'):
        collections = administrators_db()
    elif(db == 'auditors'):
        collections = auditors_db()
    else:  # (db=='administators'):
        collections = users_db()


    result = collections.find_one({"user_mail": mail})
    return result




def remove_value(json, field):
    r = dict(json)
    del r[field]
    return r


def compare_passwords(pwd1, pwd2):
    band = False
    if(pwd1 == pwd2):
        band = True
    return band


def validate_user():
    usuario_activo = get_usuario_activo()
    print("usuario acitvo validate: ",usuario_activo)
    band = False
    if usuario_activo != None:
        band = True
    return band


def get_user_by_nit(nit):
    collections = init_db()
    result = collections.find_one({"user_nit": nit})
    return result

def get_templates_route():
    return './templates/'


def render_template(template_name='index.html', context={}):
    html_str = ""
    with open(template_name, 'r') as f:
        html_str = f.read()
        html_str = html_str.format(**context)
    return html_str

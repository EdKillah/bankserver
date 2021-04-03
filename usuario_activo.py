usuario_activo = None

def set_usuario_activo(user):
    global usuario_activo    
    usuario_activo = user
    #print("entra en set user_activo: ",usuario_activo, "usuario_activo")

def get_usuario_activo():    
    global usuario_activo
    print("entra en get_usuario_activo: ",usuario_activo)
    return usuario_activo
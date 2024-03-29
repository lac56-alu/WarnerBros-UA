# ---------------------- IMPORTS ----------------------
import json
import socket
from time import sleep
import sys
import requests
import stomp
import time
import hashlib
import getpass

# ---------------------- Variables Globales ----------------------
HEADER = 100
FORMATO_MSG = 'utf-8'

ipRegistry = 0
puertoRegistry = 0
ipBroker = 0
puertoBroker = 0
ipAPI = 0
puertoAPI = 0
serverAPI = "/lac56-alu/SD-REGISTRY/1.0.0/"
topicVisitor = "/topic/VISITOR"
topicEngine = "/topic/engine"
ipActiveMQ = '127.0.0.1'
puertoActiveMQ = 61613
global topicRespuesta
salidaEjecucion = True


currentUser = []

def asignarNombrePass(u,p, currentUser):
    currentUser.append(u)
    currentUser.append(p)

def asignarToken(t,currentUser):
    currentUser.append(t)

def asignarTODO(u,p,t, currentUser):
    currentUser.append(u)
    currentUser.append(p)
    currentUser.append(t)

def borrarCurrent(currentUser):
    currentUser = []

class Listener(object):
    def __init__(self, conn):
        self.conn = conn
        self.count = 0
        self.start = time.time()
    def on_message(headers, message):
        # ESTE ES EL TOPIC QUE ESTA A LA ESCUCHA
        topicRespuesta = "/topic/" + str(currentUser[0])
        if(message.headers['destination'] == topicRespuesta):
            print(message.body)


# ---------------------- Modulos SOCKETS ----------------------
def enviarMensaje(msg):
    nuevoMSG = msg.encode(FORMATO_MSG)
    msg_length = len(nuevoMSG)
    send_length = str(msg_length).encode(FORMATO_MSG)
    send_length += b' ' * (HEADER - len(send_length))
    cliente.send(send_length)
    cliente.send(nuevoMSG)

def enviarEngine(msg):
    try:
        conn = stomp.Connection([(ipActiveMQ, puertoActiveMQ)])
        conn.connect(login="", passcode="", wait=True)
        conn.send(topicEngine, msg, headers=None)
    except Exception as e:
        print("Error Enviar Mensaje:", e)


def menuInicio():
    print("Elige método de conexión:")
    print(" 1. Sockets")
    print(" 2. API Rest")
    seleccion = input()


    if int(seleccion) == 1:
        return seleccion
    elif int(seleccion) == 2:
        return seleccion
    else:
        print("Introduce una de las dos opciones")
        menuInicio()

def logInSockets():
    print(" Nombre Usuario: ")
    userName = input()
    password = getpass.getpass(' Introduce la contraseña: ')

    hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
    pos = slice(0, len(hash) // 2)
    correctPass = hash[pos]

    asignarNombrePass(userName, correctPass, currentUser)

    cadena = "logIn," + userName + "," + str(correctPass)
    return cadena


def crearUsuarioSockets():
    comprobarPass = False

    print(" Nombre Usuario: ")
    userName = input()

    while not comprobarPass:
        password = getpass.getpass(' Constraseña: ')
        password2 = getpass.getpass('Repita la contraseña: ')

        if password == password2:
            comprobarPass = True
            hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
            pos = slice(0, len(hash) // 2)
            correctPass = hash[pos]

    cadena = "crearUsuario," + userName + "," + str(correctPass)
    return cadena

def modificarUsuario():
    comprobarPass = False

    passOld = getpass.getpass(' Introduzca la contraseña actual: ')
    hash = hashlib.sha512(passOld.encode("utf-8")).hexdigest()
    pos = slice(0, len(hash) // 2)
    correctPass = hash[pos]

    if correctPass == currentUser[1]:
        while not comprobarPass:
            password = getpass.getpass(' Constraseña nueva: ')
            password2 = getpass.getpass(' Repita la contraseña nueva: ')

            if password == password2:
                comprobarPass = True
                hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
                pos = slice(0, len(hash) // 2)
                correctPass = hash[pos]

        asignarNombrePass(currentUser[0], correctPass, currentUser)
        cadena = "modificar," + currentUser[0] + "," + correctPass + "," + currentUser[2]
        return cadena
    else:
        cadena = ""
        print("Credenciales incorrectas")
        return cadena

def crearListener(topic):
    conn = stomp.Connection([(ipActiveMQ, int(puertoActiveMQ))])
    listener = Listener(conn)
    conn.set_listener('listener', listener)
    conn.connect(login="", passcode="", wait=True)
    conn.subscribe(topic, id=1, ack='auto')

def entradaParque(activador):
    sleep(2)
    print("Elige una de las opciones:")
    print(" 1. Mostrar el mapa")
    print(" 2. Movimiento")
    print(" 0. Salir del parque")
    seleccion = input()

    if int(seleccion) == 1:
        msg = "mostrarMapa," + currentUser[0]
        enviarEngine(msg)

        entradaParque(activador)

    elif int(seleccion) == 2:
        comprobarOpcion = False

        while comprobarOpcion == False:
            print("¿Hacia donde quieres desplazarte?")
            print("Opciones: N, NE, E, SE, S, SO, O, NO")
            direccion = input()

            if direccion == 'N' or direccion == 'NE' or direccion == 'E' or direccion == 'SE' or direccion == 'S' or direccion == 'SO' or direccion == 'O' or direccion == 'NO':
                comprobarOpcion = True
                break

        msg = "mover," + currentUser[0] + "," + direccion
        enviarEngine(msg)

        entradaParque(activador)

    elif int(seleccion) == 0:
        msg = "salir," + currentUser[0]
        enviarEngine(msg)

        if activador == "sck":
            menuRegistradoSockets()
        elif activador == "api":
            menuRegistradoAPI()


def menuRegistradoSockets():
    sleep(2)
    print("Elige una de las opciones:")
    print(" 1. Entrar al parque")
    print(" 2. Editar Perfil")
    print(" 3. Borrar Perfil")
    print(" 0. Salir")
    seleccion = input()

    if int(seleccion) == 1:
        topicRespuesta = "/topic/" + str(currentUser[0])
        crearListener(topicRespuesta)

        msg = "entrar," + str(currentUser[0])
        enviarEngine(msg)

        activador = "sck"
        entradaParque(activador)

    elif int(seleccion) == 2:
        datosModificarUsuario = modificarUsuario()

        if datosModificarUsuario == "":
            menuRegistradoSockets()

        enviarMensaje(datosModificarUsuario)
        msg = cliente.recv(HEADER).decode(FORMATO_MSG)
        print(msg)
        menuRegistradoSockets()

    elif int(seleccion) == 3:
        print("¿Seguro que quiere borrar su usuario? y/n")
        seleccion = input()
        sys.stdin.flush()

        if seleccion == "y":
            cadenaBorrar = "deleteUsuario," + currentUser[0] + "," + currentUser[2]
            enviarMensaje(cadenaBorrar)
            msg = cliente.recv(HEADER).decode(FORMATO_MSG)
            print(msg)

            borrarCurrent(currentUser)
            menuSockets()
        else:
            menuRegistradoSockets()
    elif int(seleccion) == 0:
        print(" Saliendo de la aplicacion...")
    else:
        print("Introduce una de las dos opciones")
        menuRegistradoSockets()


def menuSockets():
    print("1. LogIn")
    print("2. Crear Usuario")
    print("0. SALIR")
    seleccion = input()

    if int(seleccion) == 1:
        datosLogIn = logInSockets()
        enviarMensaje(datosLogIn)
        msg = cliente.recv(HEADER).decode(FORMATO_MSG)

        if msg == "No encontrado":
            print("Credenciales Incorrectas")
            menuSockets()
        elif msg == "Error":
            print("Error al realizar la operacion...")
        else:
            print("Acceso Correcto")
            asignarToken(msg, currentUser)
            menuRegistradoSockets()
    elif int(seleccion) == 2:
        datosCrearUsuario = crearUsuarioSockets()
        enviarMensaje(datosCrearUsuario)
        msg = cliente.recv(HEADER).decode(FORMATO_MSG)
        print(msg)
        menuSockets()
    elif int(seleccion) == 0:
        print("  Saliendo de la aplicacion...")
        return
    else:
        print("Introduce una opcion valida")
        menuSockets()

# ---------------------- Modulos API ----------------------

def modificarUsuarioAPI():
    comprobarPass = False

    print(" Introduzca la contraseña actual: ")
    passOld = input()
    hash = hashlib.sha512(passOld.encode("utf-8")).hexdigest()
    pos = slice(0, len(hash) // 2)
    correctPassOld = hash[pos]


    while not comprobarPass:
        print(" Constraseña nueva: ")
        password = input()
        print(" Repita la contraseña nueva: ")
        password2 = input()

        if password == password2:
            comprobarPass = True
            hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
            pos = slice(0, len(hash) // 2)
            correctPass = hash[pos]


    try:
        endPoint = "http://" + str(ipAPI) + ":" + str(puertoAPI) + serverAPI + "modificarUsuario/" + currentUser[2]
        body = {"name": currentUser[0], "oldPassword": correctPassOld, "newPassword": correctPass}
        jsonBody = json.dumps(body)

        response = requests.put(
            endPoint,
            jsonBody,
            headers={'Content-Type': 'application/json'}
        )
        print(response.status_code)
        jsonRespuesta = json.loads(response.text)

        if response.status_code == 201:
            msg = jsonRespuesta['cadena']
            print("Usuario modificado correctamente.")
        else:
            msg = "Valores no validos."
    except Exception:
        msg = "No se ha podido conectar con el endpoint."

    return msg

def borrarUsuarioAPI():
    msg = ""
    print("¿Seguro que quiere borrar su usuario? y/n")
    seleccion = input()

    if seleccion == "y":
        print(" Introduzca la contraseña actual: ")
        password = input()
        hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
        pos = slice(0, len(hash) // 2)
        correctPass = hash[pos]

        if correctPass == currentUser[1]:
            print("las contraseñas coinciden")
            endPoint = "http://" + str(ipAPI) + ":" + str(puertoAPI) + serverAPI \
                       + "borrarUsuario/" + currentUser[2] + "/" + currentUser[0]
            response = requests.delete(
                endPoint,
                headers={'Content-Type': 'application/json'}
            )

            jsonRespuesta = json.loads(response.text)

            if response.status_code == 201:
                print(jsonRespuesta['cadena'])
                msg = jsonRespuesta['cadena']
            else:
                print(jsonRespuesta['cadena'])
                msg = "No se ha podido borrar el usuario."
        else:
            print("Credendiales incorrectas.")


    elif seleccion == "n":
        print("Operación cancelada.")

    return msg



def menuRegistradoAPI():
    print("Elige una de las opciones:")
    print(" 1. Entrar al parque")
    print(" 2. Editar Perfil")
    print(" 3. Borrar Perfil")
    print(" 0. Salir")
    seleccion = input()

    if int(seleccion) == 1:
        topicRespuesta = "/topic/" + str(currentUser[0])
        crearListener(topicRespuesta)

        msg = "entrar," + str(currentUser[0])
        enviarEngine(msg)

        activador = "api"
        entradaParque(activador)


    elif int(seleccion) == 2:
        modificarUsuarioAPI()
        menuRegistradoAPI()

    elif int(seleccion) == 3:
        resp = borrarUsuarioAPI()

        if resp == "No se ha podido borrar el usuario." or resp == "":
            menuRegistradoAPI()
        else:
            borrarCurrent(currentUser)
            menuAPI()

    elif int(seleccion) == 0:
        print("Saliendo de la aplicacion...")


def crearUsuarioAPI():
    msg = ""

    print(" Nombre Usuario: ")
    userName = input()
    print(" Constraseña: ")
    password = input()
    hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
    pos = slice(0, len(hash) // 2)
    correctPass = hash[pos]

    try:
        endPoint = "http://" + str(ipAPI) + ":" + str(puertoAPI) + serverAPI + "nuevoUsuario"
        body = {"name": userName, "password": correctPass}
        jsonBody = json.dumps(body)

        response = requests.post(
            endPoint,
            jsonBody,
            headers={'Content-Type': 'application/json'}
        )

        jsonRespuesta = json.loads(response.text)

        if response.status_code == 201:
            print("Usuario creado correctamente.")
            msg = jsonRespuesta['cadena']
            print("Su token es: " + msg)
        else:
            msg = "Valores no validos."
    except Exception:
        msg = "No se ha podido conectar con el endpoint."

    return msg



def logInAPI():
    msg = ""

    print(" Nombre Usuario: ")
    userName = input()
    print(" Constraseña: ")
    password = input()
    hash = hashlib.sha512(password.encode("utf-8")).hexdigest()
    pos = slice(0, len(hash) // 2)
    correctPass = hash[pos]

    try:
        endPoint = "http://" + str(ipAPI) + ":" + str(puertoAPI) + serverAPI + "login"
        body = {"name": userName, "password": correctPass}
        jsonBody = json.dumps(body)

        response = requests.post(
            endPoint,
            jsonBody,
            headers={'Content-Type': 'application/json'}
        )

        jsonRespuesta = json.loads(response.text)

        if response.status_code == 201:
            token = jsonRespuesta['cadena']
            try:
                asignarTODO(userName, password, token, currentUser)
            except Exception as e:
                print(e)

            """currentUser.append(userName)
            currentUser.append(password)
            currentUser.append(token)"""
            msg = "Usuario logeado correctamente."
        else:
            msg = "Credenciales Incorrectas"
    except Exception:
        msg = "No se ha podido conectar con el endpoint."

    return msg

def menuAPI():
    print("1. LogIn")
    print("2. Crear Usuario")
    print("0. SALIR")
    seleccion = input()

    if int(seleccion) == 1:
        respuestaLogin = logInAPI()
        print(respuestaLogin)

        if respuestaLogin == "Usuario logeado correctamente.":
            menuRegistradoAPI()
        elif respuestaLogin == "No se ha podido conectar con el endpoint.":
            menuInicio()
        elif respuestaLogin == "Credenciales Incorrectas":
            menuAPI()

    elif int(seleccion) == 2:
        respuestaCrear = crearUsuarioAPI()

        if respuestaCrear == "Valores no validos." or respuestaCrear == "No se ha podido conectar con el endpoint.":
            menuAPI()
        else:
            currentUser.append(respuestaCrear)
    elif int(seleccion) == 0:
        print("  Saliendo de la aplicacion...")
        return
    else:
        print("Introduce una opcion valida")
        menuAPI()



# ---------------------- MAIN ----------------------
ipRegistry = sys.argv[1]
puertoRegistry = sys.argv[2]
ipBroker = sys.argv[3]
puertoBroker = sys.argv[4]
ipAPI = sys.argv[5]
puertoAPI = sys.argv[6]
salidaEjecucion = True

eleccion = menuInicio()

if int(eleccion) == 1:

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parseToInt = int(puertoRegistry)
    direccionRegistro = (ipRegistry, parseToInt)

    while salidaEjecucion:
        try:
            currentUser = []
            cliente.connect(direccionRegistro)
            print("Conexion completada.")
            print(" ################### SOCKETS ###################")
            menuSockets()
            break
        except Exception as e:
            print(e)
            print("No se puede establecer la conexion...")
            print(" Intentandolo de nuevo...")
            sleep(5)
            break
else:
    currentUser = []
    menuAPI()

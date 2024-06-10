import flask
from flask import Flask, render_template, request, redirect, session
from flask import url_for
import requests
import json
import pyrebase
import logging

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


app = Flask(__name__)
app.secret_key = '19b93bf5fda393880d9fae74a2b17d0a9bbe51e28a6266e64e86958f8f992c76'  # Cambia esto por una clave secreta segura
 
Config = {
    "apiKey": "AIzaSyDakXI8n291Wxk5tCY9ObRn2dMWefnGOUc",
    "authDomain": "proyfinalpweb.firebaseapp.com",
    "storageBucket": "proyfinalpweb-final-pw.appspot.com",
    "projectId": "proyfinalpweb",
    "messagingSenderId": "666889027120",
    "appId": "1:666889027120:web:0d874de567123c2ca977f5",
    # Esta se  encuentra en el apartado de 'Realtime Database' en 'firebase'
    "databaseURL": "https://proyfinalpweb-default-rtdb.firebaseio.com/"
}

# store information
global SESSION
SESSION = {}

firebase = pyrebase.initialize_app(Config)
auth = firebase.auth()
db = firebase.database()


@app.route('/')
def index():
    return render_template('login.html')

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        login_data = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        try:
            login = auth.sign_in_with_email_and_password(login_data['email'],login_data['password'])
            SESSION['user_id'] = login['localId']  # Guardar el ID de usuario en la sesión

            return 'Usuario Valido'
            #return render_template('home.html')
            #return render_template(url_for('home'))
        except:
            return 'Error en el inicio de sesión. Por favor, verifique sus credenciales.'
    return render_template('login.html')


# Ruta para registrar un nuevo usuario
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        dob = request.form['dob']
        nombre = request.form['firstname']
        apellidopaterno = request.form['apellidoPaterno']
        apellidomaterno = request.form['apellidoMaterno']
    
        register_data = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }
        data = {
            'email': email,
            'dob': dob,
            'firstname': nombre,
            'apellidopaterno': apellidopaterno,
            'apellidomaterno': apellidomaterno,
        }
        try:
            user = auth.create_user_with_email_and_password(register_data['email'],register_data['password'])
            uid = user['localId']
            db.child('users').child(uid).set(data)
            return render_template('login.html')
        except:
            return 'Error en el registro. Por favor, inténtelo de nuevo.'
    return render_template('register.html')

# Ruta para la página de inicio (requiere autenticación)
@app.route('/home')
def home():
    return render_template('home.html')

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    SESSION.pop('user_id', None)
    return redirect(url_for('login'))

# Ruta para la página de perfil
@app.route('/profile')
def profile():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        user_info = None
        try:
            user_info = db.child("users").child(user_id).get().val()
        except:
            pass
        return render_template('profile.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        if request.method == 'POST':
            # Obtén los datos actualizados del formulario
            nombre = request.form['firstname']
            email = request.form['email']
            # Agregar más campos de información del usuario según sea necesario

            # Realiza la actualización en la base de datos
            try:
                db.child("users").child(user_id).update({
                    "firstname": nombre,
                    "email": email,
                    # Agregar más campos de información del usuario según sea necesario
                })
                user_info = db.child("users").child(user_id).get().val()
                return render_template('profile.html', user_info=user_info)
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('profile'))
    
@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        try:
            # Elimina al usuario y sus datos de la base de datos
            db.child('users').child(user_id).remove()
            auth.delete_user_account(user_id)
            SESSION.clear() # Borra la sesión del usuario después de la eliminación
            return redirect(url_for('login'))
            #return 'Usuario eliminado exitosamente.'
        except:
            return 'Error al eliminar el usuario.'
    else:
        return redirect(url_for('home'))
    
@app.route('/materia')
def materia():
    return render_template('alta_materia.html')


# Ruta para registrar una nueva materia
@app.route('/alta_materia', methods=['GET', 'POST'])
def alta_materia():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            
            Nombre = request.form['Nombre']
            Clave = request.form['Clave']
            Semestre = request.form['Semestre']
            FechaInicio = request.form['FechaInicio']
            FechaFin = request.form['FechaFin']
            
            try:
                # Guardar los datos en la base de datos
                tamano = db.child('users').child(user_id).child('materia').get().val()  # Utiliza push para generar un ID único para cada materia
                logging.info(tamano)
                if tamano is None:
                    m_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    m_id = ultimo_elemento.get('Materia_id')
                    
                    
                print(m_id)
                data = {
                    'Nombre': Nombre,
                    'Clave': Clave,
                    'Semestre': Semestre,
                    'FechaInicio': FechaInicio,
                    'FechaFin': FechaFin,
                    'Materia_id': m_id,
                }
                
                #db.child('materia').child(size).set(data)
                db.child('users').child(user_id).child('materia').child(m_id).set(data)
                
                print("Datos guardados exitosamente.")
                
                return redirect(url_for('materia'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return f'Error en el registro: {str(e)}'
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
# Ruta para buscar la materia por su clave
@app.route('/buscar_materia', methods=['POST'])
def buscar_materia():
    user_id = SESSION['user_id']
    clave = request.form['Clave']
    
    materias = db.child('users').child(user_id).child('materia').get().val()
    
    # Verificar si se encontró el objeto de materias
    if materias:
        # Recorrer cada materia en la lista de materias
        if isinstance(materias, list):
            for materia in materias:
                if materia.get('Clave') == clave:
                    materia_encontrada =  materia
    
    #materia_encontrada = db.child('users').child(user_id).child('materia').order_by_child("Clave").equal_to(clave).get().val()
    if materia_encontrada:
        return render_template('detalle_materia.html', materia=materia_encontrada)
    else:
        return render_template('error_materia_no_encontrada.html', clave=clave)

@app.route('/detalle_materia/<materia_id>', methods=['GET'])
def detalle_materia(materia_id):
    # Aquí puedes obtener los detalles de la materia con el ID proporcionado desde la base de datos
    # Por ejemplo, si estás usando Firebase Realtime Database, podrías hacer algo como:
    materia = db.child("materias").child(materia_id).get().val()
    if materia:
        return render_template('detalle_materia.html', materia=materia)
    else:
        # Manejar el caso en el que la materia no exista
        return "La materia no fue encontrada.", 404

# Ruta para actualizar la materia
@app.route('/actualizar_materia', methods=['POST'])
def actualizar_materia():
    # Recibes los datos actualizados del formulario
    nueva_nombre = request.form['Nombre']
    nueva_clave = request.form['Clave']
    nueva_semestre = request.form['Semestre']
    nueva_fecha_inicio = request.form['FechaInicio']
    nueva_fecha_fin = request.form['FechaFin']
    
    # Aquí realizas la lógica para actualizar la materia en la base de datos
    # y rediriges a la página de inicio después de la actualización
    return redirect(url_for('index'))

# Ruta para borrar la materia
@app.route('/borrar_materia', methods=['POST'])
def borrar_materia():
    # Recibes la clave de la materia a borrar
    clave = request.form['Clave']
    # Aquí realizas la lógica para borrar la materia de la base de datos
    # y rediriges a la página de inicio después del borrado
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)

import flask
from flask import Flask, render_template, request, redirect, session, flash
from flask import url_for
from collections import OrderedDict
import requests
import json
import pyrebase
import traceback

#TODO Agregar columna baja logica a las tablas

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

user_admins = ["user1", "4tPugWZNslXrY7TcQkz5M4J23vv1", "9MM7xT43gQUpAdD7wnABlZCz20B2"]
user_profes = ["Y4nLiNhfO5UEwZkJe33HhFFqBwZ2",""]



@app.route('/')
def index():
    return render_template('login.html')

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        dob = request.form['dob']
        nombre = request.form['firstname']
        apellidopaterno = request.form['apellidoPaterno']
        apellidomaterno = request.form['apellidoMaterno']
        borradologico = False
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
            'Borrado_Logico': borradologico,
        }
        try:
            user = auth.create_user_with_email_and_password(register_data['email'],register_data['password'])
            uid = user['localId']
            db.child('users').child(uid).set(data)
            return render_template('login.html')
        except:
            return 'Error en el registro. Por favor, inténtelo de nuevo.'
    return render_template('register.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/logout')
def logout():
    SESSION.pop('user_id', None)
    return redirect(url_for('login'))


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
            dob = request.form['dob']
            apellidopaterno = request.form['apellidopaterno']
            apellidomaterno = request.form['apellidomaterno']
            
            
            # Realiza la actualización en la base de datos
            try:
                db.child("users").child(user_id).update({
                    'email': email,
                    'dob': dob,
                    'firstname': nombre,
                    'apellidopaterno': apellidopaterno,
                    'apellidomaterno': apellidomaterno,
                    # Agregar más campos de información del usuario según sea necesario
                })
                user_info = db.child("users").child(user_id).get().val()
                return render_template('profile.html', user_info=user_info)
                #return 'Perfil actualizado exitosamente.'
            except:
                return render_template('profile.html', user_info=user_info)
    else:
        return redirect(url_for('profile'))
    
@app.route('/baja_logica_user', methods=['POST'])
def baja_logica_user():  
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        if request.method == 'POST':
            # Realiza la actualización en la base de datos
            try:
                db.child("users").child(user_id).update({
                    'Borrado_Logico': True,
                    # Agregar más campos de información del usuario según sea necesario
                })
                user_info = db.child("users").child(user_id).get().val()
                return render_template('profile.html', user_info=user_info)
                #return 'Perfil actualizado exitosamente.'
            except:
                return render_template('profile.html', user_info=user_info)
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



@app.route('/profesor')
def profesor():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        if user_id in user_admins:        
            profesores = db.child('profesor').get().val()
            return render_template('alta_profesor.html',profesores=profesores)
        else:
            flash("Usuario no tiene permiso para accesar a esta función", "danger")
            return redirect(url_for('home'))
    else:
        flash("Usuario no tiene permiso para accesar a esta función", "danger")
        return redirect(url_for('home'))

@app.route('/alta_profesor', methods=['GET', 'POST'])
def alta_profesor():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            
            Nombre = request.form['Nombre']
            apellidopaterno = request.form['apellidoPaterno']
            apellidomaterno = request.form['apellidoMaterno']
            Clave = request.form['Clave']
            borradologico = False

            try:
                # Guardar los datos en la base de datos
                tamano = db.child('profesor').get().val()  # Utiliza push para generar un ID único para cada materia
                if tamano is None:
                    p_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    p_id = ultimo_elemento.get('Profesor_id')
                    print(type(p_id))         # <class 'int'>
                    p_id = int(p_id)
                    p_id = p_id + 1
                    
                    
                print(p_id)
                data = {
                    'Nombre': Nombre,
                    'Apellido_Paterno':apellidopaterno,
                    'Apellido_Materno':apellidomaterno,
                    'Clave': Clave,
                    'Borrado_Logico': borradologico,
                    'Profesor_id': p_id,
                }
                
                #db.child('profesor').child(size).set(data)
                db.child('profesor').child(p_id).set(data)
                
                print("Datos guardados exitosamente.")
                
                return redirect(url_for('profesor'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return f'Error en el registro: {str(e)}'
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
@app.route('/buscar_profesor', methods=['POST'])
def buscar_profesor():
    user_id = SESSION['user_id']
    clave = request.form['Clave']

    try:
        profesores = db.child('profesor').get().val()
        
        # Inicializar la variable profesor_encontrado
        profesor_encontrado = None
        
        # Verificar si se encontró el objeto de profesores
        if profesores:
            # Recorrer cada materia en la lista de profesores
            if isinstance(profesores, list):
                for profesor in profesores:
                    if profesor.get('Clave') == clave:
                        profesor_encontrado = profesor
                        break
        
        # Comprobar si se encontró el profesor
        if profesor_encontrado:
            return render_template('detalle_profesor.html', profesor=profesor_encontrado)
        else:
            flash('No se encontró al profesor con la Clave especificada.', 'danger')
            return redirect(url_for('profesor'))
    
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        return (f"Error al buscar el profesor: {e}")

@app.route('/actualizar_profesor', methods=['POST'])
def actualizar_profesor():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            nueva_nombre = request.form['Nombre']
            nueva_apellidopaterno = request.form['Apellido_Paterno']
            nueva_apellidomaterno = request.form['Apellido_Materno']
            Profesor_id = request.form['Profesor_id']

            try:
                db.child('profesor').child(Profesor_id).update({
                    'Nombre': nueva_nombre,
                    'apellidopaterno': nueva_apellidopaterno,
                    'apellidomaterno': nueva_apellidomaterno,
                    'Borrado_Logico': False,
                    'Profesor_id': Profesor_id,
                })
                return redirect(url_for('profesor'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el profesor. Inténtalo de nuevo.'
    else:
        return redirect(url_for('profesor'))

@app.route('/baja_logica_porfesor', methods=['POST'])
def baja_logica_porfesor():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            Profesor_id = request.form['Profesor_id']

            try:
                db.child('profesor').child(Profesor_id).update({
                    'Borrado_Logico': True,
                    'Profesor_id': Profesor_id,
                })
                return redirect(url_for('profesor'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el profeor. Inténtalo de nuevo.'
    else:
        return redirect(url_for('profesor'))

@app.route('/borrar_profesor', methods=['POST'])
def borrar_profesor():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        Profesor_id = request.form['Profesor_id']
        try:
            # Elimina al usuario y sus datos de la base de datos
            materia_node = db.child('profesor').child(Profesor_id).child('materia').get().val()

            # Verificar si el nodo de la materia no tiene hijos
            if not materia_node:
                # El nodo de la materia está vacío, no tiene hijos
                db.child('profesor').child(Profesor_id).remove()
                return redirect(url_for('profesor'))
                #return 'Usuario eliminado exitosamente.'
            else:
                return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


    
@app.route('/materia')
def materia():
    try:
        user_id = SESSION.get('user_id')  # Utiliza get para evitar errores si 'user_id' no está en SESSION
        materias = db.child('materia').get().val()

        # Obtener las claves de los profesores de la base de datos
        profesores = db.child('profesor').get().val()
        claves_profesores = []
        for profesor in profesores:
            if not profesor['Borrado_Logico']:
                claves_profesores.append(profesor['Clave'])

        # Obtener las claves de las horarios del usuario de la base de datos
        horarios = db.child('horario').get().val()
        claves_horarios = []
        for horario in horarios:
            if not horario['Borrado_Logico']:
                claves_horarios.append(horario['Clave'])

        # Pasar las claves de los profesores y horarios al template HTML
        return render_template('alta_materia.html', claves_profesores=claves_profesores, claves_horarios=claves_horarios, materias=materias)
    except Exception as e:
        print(f"Error en la función 'materia': {str(e)}")
        return redirect(url_for('home'))

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
            Profesor_Clave = request.form['profesor']
            Horario_Clave = request.form['horario']
            borradologico = False

            try:
                # Guardar los datos en la base de datos
                tamano = db.child('materia').get().val()  # Utiliza push para generar un ID único para cada materia
                if tamano is None:
                    m_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    m_id = ultimo_elemento.get('Materia_id')
                    m_id = int(m_id)
                    print(m_id)
                    m_id = m_id + 1
                    
                    
                print(m_id)
                data = {
                    'Nombre': Nombre,
                    'Clave': Clave,
                    'Semestre': Semestre,
                    'FechaInicio': FechaInicio,
                    'FechaFin': FechaFin,
                    'Profesor_Clave': Profesor_Clave,
                    'Horario_Clave': Horario_Clave,
                    'Borrado_Logico': borradologico,
                    'Materia_id': m_id,
                }
                
                profesores = db.child('profesor').get().val()
                # Verificar si se encontró el objeto de materias
                if profesores:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(profesores, list):
                        for profesor in profesores:
                            if profesor.get('Clave') == Profesor_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    profesor_encontrado =  profesor
                
                horarios = db.child('horario').get().val()
                # Verificar si se encontró el objeto de materias
                if horarios:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(horarios, list):
                        for horario in horarios:
                            if horario.get('Clave') == Horario_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    horario_encontrado =  horario
                
                db.child('materia').child(m_id).set(data)

                db.child('horario').child(horario_encontrado['Horario_id']).child('materia').child(m_id).set({'Materia_id': m_id,
                                                                                                              'Materia_Clave':Clave,
                                                                                                              'Horario_nombre':horario_encontrado['Nombre'],
                                                                                                              'Horario_Clave':horario_encontrado['Clave']})                
                db.child('profesor').child(profesor_encontrado['Profesor_id']).child('materia').child(m_id).set({'Materia_id': m_id,
                                                                                                              'Materia_Clave':Clave,
                                                                                                              'Profesor_nombre':profesor_encontrado['Nombre'],
                                                                                                              'Profesor_Clave':profesor_encontrado['Clave']})                
                
                print("Datos guardados exitosamente.")
                
                return redirect(url_for('materia'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return f'Error en el registro: {str(e)}'
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
@app.route('/buscar_materia', methods=['POST'])
def buscar_materia():
    user_id = SESSION['user_id']
    clave = request.form['Clave']
    
    try:           
        materias = db.child('materia').get().val()
        
        # Verificar si se encontró el objeto de materias
        if materias:
            # Recorrer cada materia en la lista de materias
            if isinstance(materias, list):
                for materia in materias:
                    if materia.get('Clave') == clave:
                        #if materia.get('Borrado_Logico') == False:
                            materia_encontrada =  materia
                
        if materia_encontrada:
            # Obtener las claves de los profesores de la base de datos
            profesores = db.child('profesor').get().val()
            claves_profesores = [profesor.get('Clave') for profesor in profesores] if profesores else []
            print(claves_profesores)
            # Obtener las claves de las horarios del usuario de la base de datos
            horarios = db.child('horario').get().val()
            claves_horarios = [horario.get('Clave') for horario in horarios] if horarios else []
            print(claves_horarios)

            # Pasar las claves de los profesores y horarios al template HT
            return render_template('detalle_materia.html', materia=materia_encontrada,  claves_profesores=claves_profesores, claves_horarios=claves_horarios)
        
        else:
            flash('No se encontró la Materia con la Clave especificada.', 'danger')
            return redirect(url_for('materia'))
        
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        flash('Fallo Y No se encontró la Materia con la Clave especificada.', 'danger')
        return redirect(url_for('materia'))
    
@app.route('/actualizar_materia', methods=['POST'])
def actualizar_materia():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            nueva_nombre = request.form['Nombre']
            nueva_semestre = request.form['Semestre']
            nueva_fecha_inicio = request.form['FechaInicio']
            nueva_fecha_fin = request.form['FechaFin']
            nueva_Profesor_Clave = request.form['profesor']
            nueva_Horario_Clave = request.form['horario']
            Materia_id = request.form['Materia_id']
            Profesor_Clave = request.form['Clave_Profesor_Anterior']
            Horario_Clave = request.form['Clave_Horario_Anterior']

            try:
                db.child('materia').child(Materia_id).update({
                    'Nombre': nueva_nombre,
                    'Semestre': nueva_semestre,
                    'FechaInicio': nueva_fecha_inicio,
                    'FechaFin': nueva_fecha_fin,
                    'Profesor_Clave': nueva_Profesor_Clave,
                    'Horario_Clave': nueva_Horario_Clave,
                    'Borrado_Logico': False,
                    'Materia_id': Materia_id,
                })
                profesores = db.child('profesor').get().val()
                # Verificar si se encontró el objeto de profesores
                if profesores:
                    # Recorrer cada materia en la lista de profesores
                    if isinstance(profesores, list):
                        for profesor in profesores:
                            if profesor.get('Clave') == nueva_Profesor_Clave:
                                profesor_encontrado =  profesor
                
                horarios = db.child('horario').get().val()
                # Verificar si se encontró el objeto de materias
                if horarios:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(horarios, list):
                        for horario in horarios:
                            if horario.get('Clave') == nueva_Horario_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    horario_encontrado =  horario
                
                db.child('profesor').child(profesor_encontrado(id)).child('materia').child(Materia_id).set({'Materia_id': Materia_id})
                db.child('horario').child(horario_encontrado(id)).child('materia').child(Materia_id).set({'Materia_id': Materia_id})     
                
                
                profesores = db.child('profesor').get().val()
                # Verificar si se encontró el objeto de profesores
                if profesores:
                    # Recorrer cada materia en la lista de profesores
                    if isinstance(profesores, list):
                        for profesor in profesores:
                            if profesor.get('Clave') == Profesor_Clave:
                                profesor_encontrado =  profesor
                
                
                horarios = db.child('horario').get().val()
                # Verificar si se encontró el objeto de materias
                if horarios:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(horarios, list):
                        for horario in horarios:
                            if horario.get('Clave') == Horario_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    horario_encontrado =  horario
                
                db.child('profesor').child(profesor_encontrado(id)).child('materia').child(Materia_id).remove()
                db.child('horario').child(horario_encontrado(id)).child('materia').child(Materia_id).remove()            
                
                return redirect(url_for('materia'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('materia'))

@app.route('/materia_updateifno', methods=['POST'])
def materia_updateifno():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            nueva_nombre = request.form['Nombre']
            nueva_clave = request.form['Clave']
            nueva_semestre = request.form['Semestre']
            nueva_fecha_inicio = request.form['FechaInicio']
            nueva_fecha_fin = request.form['FechaFin']
            Materia_id = request.form['Materia_id']

            try:
                db.child('users').child(user_id).child('materia').child(Materia_id).update({
                    'Nombre': nueva_nombre,
                    'Clave': nueva_clave,
                    'Semestre': nueva_semestre,
                    'FechaInicio': nueva_fecha_inicio,
                    'FechaFin': nueva_fecha_fin,
                    'Borrado_Logico': False,
                    'Materia_id': Materia_id,
                })
                return redirect(url_for('materia'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('materia'))

@app.route('/baja_logica_materia', methods=['POST'])
def baja_logica_materia():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            Materia_id = request.form['Materia_id']

            try:
                db.child('materia').child(Materia_id).update({
                    'Borrado_Logico': True,
                    'Materia_id': Materia_id,
                })
                return redirect(url_for('materia'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('materia'))

@app.route('/borrar_materia', methods=['POST'])
def borrar_materia():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        Materia_id = request.form['Materia_id']
        Horario_Clave = request.form['Clave_Horario_Anterior']
        print(Horario_Clave)
        Profesor_Clave = request.form['Clave_Profesor_Anterior']
        print(Profesor_Clave)

        try:
            # Elimina al usuario y sus datos de la base de datos
            materia_node = db.child('materia').child(Materia_id).get().val()
            print(materia_node)
            
            profesores = db.child('profesor').get().val()
            # Verificar si se encontró el objeto de materias
            if profesores:
                # Recorrer cada materia en la lista de materias
                if isinstance(profesores, list):
                    for profesor in profesores:
                        if profesor.get('Clave') == Profesor_Clave:
                        #if materia.get('Borrado_Logico') == False:
                            profesor_encontrado =  profesor
                
            horarios = db.child('horario').get().val()
            # Verificar si se encontró el objeto de materias
            if horarios:
                # Recorrer cada materia en la lista de materias
                if isinstance(horarios, list):
                    for horario in horarios:
                        if horario.get('Clave') == Horario_Clave:
                            #if materia.get('Borrado_Logico') == False:
                            horario_encontrado =  horario
                            
            # Verificar si el nodo de la materia no tiene hijos
            if not materia_node:
                #if horario_encontrado.get('Borrado_Logico') and profesor_encontrado.get('Borrado_Logico') == True:
                # El nodo de la materia está vacío, no tiene hijos
                db.child('materia').child(Materia_id).remove()
                return redirect(url_for('materia'))
                #return 'Usuario eliminado exitosamente.'
            else:
                return redirect(url_for('home'))
        except:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))


@app.route('/plan_estudio')
def plan_estudio():
    try:
        user_id = SESSION.get('user_id')  # Utiliza get para evitar errores si 'user_id' no está en SESSION
        # Obtener las claves de las materias del usuario de la base de datos
        plan_de_estudio = db.child('plan_estudios').get().val()

        materias = db.child('materia').get().val()
        # Obtener las claves de las horarios del usuario de la base de datos
        claves_materias = []
        for materia in materias:
            if not materia['Borrado_Logico']:
                claves_materias.append(materia['Clave'])
        # Pasar las claves de los profesores y materias al template HTML
        return render_template('alta_planestudio.html', claves_materias=claves_materias,plan_de_estudio=plan_de_estudio )
    except Exception as e:
        print(f"Error en la función 'plan_estudio': {str(e)}")
        return redirect(url_for('home'))

@app.route('/alta_plan_estudios', methods=['GET', 'POST'])
def alta_plan_estudios():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            Nombre = request.form['Nombre']
            Clave = request.form['Clave']
            Materia_Clave = request.form['materia']
            borradologico = False

            try:
                # Guardar los datos en la base de datos
                tamano = db.child('plan_estudios').get().val()  # Utiliza push para generar un ID único para cada materia
                if tamano is None:
                    p_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    p_id = ultimo_elemento.get('Plan_Estudios_id')
                    print(type(p_id))         # <class 'int'>
                    p_id = int(p_id)
                    p_id = p_id + 1
                    
                print("Clave Plan de Estudio es:")
                print(p_id)
                data = {
                    'Nombre': Nombre,
                    'Clave': Clave,
                    'Materia_Clave': Materia_Clave,
                    'Borrado_Logico': borradologico,
                    'Plan_Estudios_id': p_id,
                }
                
                
                materias = db.child('materia').get().val()
                
                materia_encontrada = None  # Initialize the variable to store the found materia

                if materias:
                    # Check if 'materias' is a list or a dictionary
                    if isinstance(materias, list):
                        # Recorrer cada materia en la lista de materias
                        for materia in materias:
                            if materia and isinstance(materia, dict):  # Check if 'materia' is a dictionary
                                if materia.get('Clave') == Materia_Clave:
                                    #if materia.get('Borrado_Logico') == False:
                                    materia_encontrada = materia
                                    break  # Exit loop once the materia is found
                    elif isinstance(materias, dict):
                        # If 'materias' is a dictionary, iterate over its values
                        for key, materia in materias.items():
                            if materia and isinstance(materia, dict):  # Check if 'materia' is a dictionary
                                if materia.get('Clave') == Materia_Clave:
                                    #if materia.get('Borrado_Logico') == False:
                                    materia_encontrada = materia
                                    break  # Exit loop once the materia is found

                if materia_encontrada:
                    print(materia_encontrada['Materia_id'])
                else:
                    print("Materia no encontrada")
                    
                print(materia_encontrada['Materia_id'])
                db.child('materia').child(materia_encontrada['Materia_id']).child('plan_estudios').child(p_id).set({'Plan_Estudios_id': p_id})
                
                db.child('plan_estudios').child(p_id).set(data)
                print("Datos guardados exitosamente.")
                #return "Datos guardados exitosamente"
                return redirect(url_for('plan_estudio'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return redirect(url_for('home'))
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
@app.route('/buscar_plan_estudios', methods=['POST'])
def buscar_plan_estudios():
    user_id = SESSION['user_id']
    clave = request.form['Clave']
    try:           
        plan_estudios = db.child('plan_estudios').get().val()
        
        # Verificar si se encontró el objeto de profesores
        if plan_estudios:
            # Recorrer cada materia en la lista de profesores
            if isinstance(plan_estudios, list):
                for plan in plan_estudios:
                    if plan.get('Clave') == clave:
                        plan_encontrado =  plan
    
        if plan_encontrado:
            # Obtener las claves de las materias del usuario de la base de datos
            materias = db .child('materia').get().val()
            claves_materias = [materia.get('Clave') for materia in materias] if materias else []

            return render_template('detalle_planestudio.html', plan_estudio = plan_encontrado, claves_materias=claves_materias)
        else:
            flash('No se encontró el Plan de Estudios con la Clave especificada.', 'danger')
            return redirect(url_for('plan_estudio'))
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        flash('No se encontró el Plan de Estudios con la Clave especificada.', 'danger')
        return redirect(url_for('plan_estudio'))
    
@app.route('/actualiza_plan_estudios', methods=['POST'])
def actualizar_plan_estudios():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            nueva_nombre = request.form['Nombre']
            nueva_clave_materia = request.form['materia']
            p_id = request.form['Plan_Estudios_id']
            Materia_Clave = request.form['Clave_Materia_Anterior']

            # Recibes los datos actualizados del formulario

            try:
                db.child('plan_estudios').child(p_id).update({
                    'Nombre': nueva_nombre,
                    'Materia_Clave': nueva_clave_materia,
                    'Plan_Estudios_id': p_id,
                })
                materias = db.child('materia').get().val()
                # Verificar si se encontró el objeto de materias
                if materias:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(materias, list):
                        for materia in materias:
                            if materia.get('Clave') == nueva_clave_materia:
                                #if materia.get('Borrado_Logico') == False:
                                    materia_encontrada =  materia
                                
                db.child('materia').child(materia_encontrada['Materia_id']).child('plan_estudios').child(p_id).set({'Plan_Estudios_id': p_id})
                if materias:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(materias, list):
                        for materia in materias:
                            if materia.get('Clave') == Materia_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    materia_encontrada =  materia
    
                db.child('materia').child(materia_encontrada['Materia_id']).child('plan_estudios').child(p_id).remove()

                return redirect(url_for('plan_estudio'))
            
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el plan estudio. Inténtalo de nuevo.'
    else:
        return redirect(url_for('plan_estudio'))

@app.route('/baja_logica_plan_estudios', methods=['POST'])
def baja_logica_plan_estudios():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            p_id = request.form['Plan_Estudios_id']

            try:
                db.child('plan_estudios').child(p_id).update({
                    'Borrado_Logico': True
                })
                return redirect(url_for('plan_estudio'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el plan estudio. Inténtalo de nuevo.'
    else:
        return redirect(url_for('plan_estudio'))

@app.route('/borrar_plan_estudios', methods=['POST'])
def borrar_plan_estudios():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        Plan_Estudios_id = request.form['Plan_Estudios_id']
        try:
            # Elimina al usuario y sus datos de la base de datos
            plan_estudio = db.child('plan_estudios').child(Plan_Estudios_id).get().val()

            materias = db.child('materia').get().val()
            # Obtener las claves de las horarios del usuario de la base de datos
            materia_node = []
            for materia in materias:
                if materia['Clave'] == plan_estudio['Materia_Clave']:
                    if materia['Borrado_Logico'] == True:
                        materia_node.append(materia['Clave'])

            # Verificar si el nodo de la materia no tiene hijos
            if not materia_node:
                # El nodo de la materia está vacío, no tiene hijos
                db.child('plan_estudios').child(Plan_Estudios_id).remove()
                return redirect(url_for('plan_estudio'))
                #return 'Usuario eliminado exitosamente.'
            else:
                return 'Error la Materia tiene dependencias'
        except:
            return 'Error al eliminar la profesor.'
    else:
        return redirect(url_for('home'))

    
    
    
    
@app.route('/horario')
def horario():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        if user_id in user_admins:
            horarios = db.child('horario').get().val()

            return render_template('alta_horario.html', horarios=horarios)
        else:
            flash("Usuario no tiene permiso para accesar a esta función", "danger")
            return redirect(url_for('home'))
    else:
        flash("Usuario no tiene permiso para accesar a esta función", "danger")
        return redirect(url_for('home'))

@app.route('/alta_horario', methods=['GET', 'POST'])
def alta_horario():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            
            Nombre = request.form['Nombre']
            Clave = request.form['Clave']
            HoraInicio = request.form['HoraInicio']
            HoraFin = request.form['HoraFin']
            Dia = request.form['Dia']
            borradologico = False

            try:
                # Guardar los datos en la base de datos
                tamano = db.child('horario').get().val()  # Utiliza push para generar un ID único para cada materia
                if tamano is None:
                    m_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    m_id = ultimo_elemento.get('Horario_id')
                    m_id = int(m_id)
                    print(m_id)
                    m_id = m_id + 1
                    
                    
                print(m_id)
                data = {
                    'Nombre': Nombre,
                    'Clave': Clave,
                    'Hora_Inicio': HoraInicio,
                    'Hora_Fin': HoraFin,
                    'Dia': Dia,
                    'Borrado_Logico': borradologico,
                    'Horario_id': m_id,
                }
                
                db.child('horario').child(m_id).set(data)
                
                print("Datos guardados exitosamente.")
                
                return redirect(url_for('horario'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return f'Error en el registro: {str(e)}'
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
@app.route('/buscar_horario', methods=['POST'])
def buscar_horario():
    user_id = SESSION['user_id']
    #clave = request.form['Clave']
    clave = request.form.get('Clave', None)
    print("Clave recibida:", clave)
    
    try:
        horarios = db.child('horario').get().val()
        
        # Verificar si se encontró el objeto de materias
        if horarios:
            # Recorrer cada materia en la lista de materias
            if isinstance(horarios, list):
                for horario in horarios:
                    if horario.get('Clave') == clave:
                        #if materia.get('Borrado_Logico') == False:
                            horario_encontrado =  horario

        H_materias = db.child('horario').child(horario_encontrado['Horario_id']).child('materia').get().val()            
                
        #print(H_materias)
        materias = []
        if H_materias is not None and isinstance(H_materias, OrderedDict):
            for key, value in H_materias.items():
                materia_id = value.get('Materia_id')
                materia_clave = value.get('Materia_Clave')  # Retrieve this value based on your database structure
                horario_nombre = value.get('Horario_nombre')  # Retrieve this value based on your database structure
                horario_clave = value.get('Horario_Clave')  # Retrieve this value based on your database structure           

                materias.append({
                    'Materia_id': materia_id,
                    'Materia_Clave': materia_clave,
                    'Horario_nombre': horario_nombre,
                    'Horario_Clave': horario_clave
                })
        #materia_encontrada = db.child('users').child(user_id).child('materia').order_by_child("Clave").equal_to(clave).get().val()
        if horario_encontrado:
            return render_template('detalle_horario.html', horario=horario_encontrado, materias=materias)
        else:
            flash('No se encontró el Horario con la Clave especificada.', 'danger')
            return redirect(url_for('horario'))
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        flash('No se encontró el Horario con la Clave especificada.', 'danger')
        return redirect(url_for('horario'))    
    
@app.route('/actualizar_horario', methods=['POST'])
def actualizar_horario():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            nueva_nombre = request.form['Nombre']
            nueva_horainicio = request.form['HoraInicio']
            nueva_horafin = request.form['HoraFin']
            nueva_dia = request.form['Dia']
            Horario_id = request.form['Horario_id']

            try:
                db.child('horario').child(Horario_id).update({
                    'Nombre': nueva_nombre,
                    'Hora_Inicio': nueva_horainicio,
                    'Hora_Fin': nueva_horafin,
                    'Dia': nueva_dia,
                    'Borrado_Logico': False,
                    'Horario_id': Horario_id,
                })
                return redirect(url_for('horario'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('horario'))

@app.route('/baja_logica_horario', methods=['POST'])
def baja_logica_horario():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            Horario_id = request.form['Horario_id']

            try:
                db.child('horario').child(Horario_id).update({
                    'Borrado_Logico': True,
                    'Horario_id': Horario_id,
                })
                return redirect(url_for('horario'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el horario. Inténtalo de nuevo.'
    else:
        return redirect(url_for('horario'))

@app.route('/borrar_horario', methods=['GET', 'POST'])
def borrar_horario():
    user_id = SESSION['user_id']
    print(user_id)
    if user_id:
        print("Paso el if")
        if request.method == 'POST':
            # Aquí manejas la lógica para el método POST
            Horario_id = request.args.get('Horario_id')
            print(Horario_id)
            try:
                # Elimina al usuario y sus datos de la base de datos
                horario_node = db.child('horario').child(Horario_id).child('materia').get().val()
                print(horario_node)
                # Verificar si el nodo de la materia no tiene hijos
                if not horario_node:
                    # El nodo de la materia está vacío, no tiene hijos
                    db.child('horario').child(Horario_id).remove()
                    return redirect(url_for('horario'))
                else:
                    return redirect(url_for('home'))
            except:
                return redirect(url_for('home'))
        elif request.method == 'GET':
            # Aquí manejas la lógica para el método GET
            Horario_id = request.args.get('Horario_id')
            print(Horario_id)
            try:
                # Elimina al usuario y sus datos de la base de datos
                horario_node = db.child('horario').child(Horario_id).child('materia').get().val()
                print(horario_node)
                # Verificar si el nodo de la materia no tiene hijos
                if not horario_node:
                    # El nodo de la materia está vacío, no tiene hijos
                    db.child('horario').child(Horario_id).remove()
                    return redirect(url_for('horario'))
                else:
                    return redirect(url_for('home'))
            except:
                return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))




@app.route('/observacion')
def observacion():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        if user_id in user_profes:
            flash("Usuario no tiene permiso para accesar a esta función", "danger")
            return redirect(url_for('home'))
        else:
            try:
                user_id = SESSION.get('user_id')  # Utiliza get para evitar errores si 'user_id' no está en SESSION
                
                materias = db.child('materia').get().val()
                # Obtener las claves de las horarios del usuario de la base de datos
                claves_materias = []
                for materia in materias:
                    if not materia['Borrado_Logico']:
                        claves_materias.append(materia['Clave'])
                
                observaciones = db.child('observacion').get().val()

                # Pasar las claves de los profesores y materias al template HTML
                #return render_template('alta_observaciones.html', claves_materias=claves_materias)
                return render_template('alta_observaciones.html', claves_materias=claves_materias, observaciones=observaciones)

            except Exception as e:
                print(f"Error en la función '/observacion': {str(e)}")
                return redirect(url_for('home'))
            
    else:
        flash("Usuario no tiene permiso para accesar a esta función", "danger")
        return redirect(url_for('home'))

@app.route('/alta_observaciones', methods=['GET', 'POST'])
def alta_observaciones():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            Observacion = request.form['Nombre']
            Clave = request.form['Clave']
            Materia_Clave = request.form['materia']
            borradologico = False

            try:
                # Guardar los datos en la base de datos
                tamano = db.child('observacion').get().val()  # Utiliza push para generar un ID único para cada materia
                if tamano is None:
                    p_id = 0
                else:
                    ultimo_elemento = tamano[-1]
                    # Imprimimos el contenido del último elemento
                    p_id = ultimo_elemento.get('Observacion_id')
                    print(type(p_id))         # <class 'int'>
                    p_id = int(p_id)
                    p_id = p_id + 1
                    
                print(p_id)
                data = {
                    'Observacion': Observacion,
                    'Clave': Clave,
                    'Materia_Clave': Materia_Clave,
                    'Borrado_Logico': borradologico,
                    'Observacion_id': p_id,
                }
    
                
                #materias = db.child('materia').get().val()
                # Verificar si se encontró el objeto de materias
                #if materias:
                    # Recorrer cada materia en la lista de materias
                    #if isinstance(materias, list):
                        #for materia in materias:
                            #if materia.get('Clave') == Materia_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                    #materia_encontrada =  materia

                #print(materia_encontrada['Materia_id'])
                #db.child('materia').child(materia_encontrada['Materia_id']).child('observacion').child(p_id).set({'Observacion_id': p_id})
                
                db.child('observacion').child(p_id).set(data)

                print("Datos guardados exitosamente.")
                return redirect(url_for('observacion'))
            except Exception as e:
                print(f"Error al guardar los datos en la base de datos: {str(e)}")
                return f'Error en el registro: {str(e)}'
    else:
        return 'Usuario no autenticado. Por favor, inicie sesión.'
    
@app.route('/buscar_observacion', methods=['POST'])
def buscar_observacion():
    user_id = SESSION['user_id']
    claveB = request.form['ClaveB']
    
    try:
        observaciones = db.child('observacion').get().val()
        observacion_encontrado = None
        # Verificar si se encontró el objeto de materias
        if observaciones:
            # Recorrer cada materia en la lista de materias
            if isinstance(observaciones, list):
                for observacion in observaciones:
                    if observacion.get('Clave') == claveB:
                        #if materia.get('Borrado_Logico') == False:
                        observacion_encontrado =  observacion
        
        if observacion_encontrado:
            # Obtener las claves de las materias del usuario de la base de datos
            materias = db .child('materia').get().val()
            claves_materias = [materia.get('Clave') for materia in materias] if materias else []
        
        #materia_encontrada = db.child('users').child(user_id).child('materia').order_by_child("Clave").equal_to(clave).get().val()
        if observacion_encontrado:
            return render_template('detalle_observacion.html', observacion=observacion_encontrado, claves_materias=claves_materias)
        else:
            flash('No se encontró la Observacion con la Clave especificada.', 'danger')
            return redirect(url_for('observacion'))
    except Exception as e:
        # Manejar cualquier excepción que pueda ocurrir
        flash('No se encontró al Observacion con la Clave especificada.', 'danger')
        return redirect(url_for('observacion'))

@app.route('/actualizar_observacion', methods=['POST'])
def actualizar_observacion():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            nueva_observacion = request.form['Nombre']
            nueva_clave_materia = request.form['materia']
            o_id = request.form['Observacion_id']
            Materia_Clave = request.form['Clave_Materia_Anterior']

            try:
                db.child('observacion').child(o_id).update({
                    'Observacion': nueva_observacion,
                    'Materia_Clave': nueva_clave_materia,
                })
                
                materias = db.child('materia').get().val()
                # Verificar si se encontró el objeto de materias
                if materias:
                    # Recorrer cada materia en la lista de materias
                    if isinstance(materias, list):
                        for materia in materias:
                            if materia.get('Clave') == nueva_clave_materia:
                                #if materia.get('Borrado_Logico') == False:
                                    materia_encontrada =  materia
                
                #db.child('materia').child(materia_encontrada['Materia_id']).child('observacion').child(o_id).set({'Observacion_id': o_id})
                #if materias:
                    # Recorrer cada materia en la lista de materias
                    #if isinstance(materias, list):
                        #for materia in materias:
                            #if materia.get('Clave') == Materia_Clave:
                                #if materia.get('Borrado_Logico') == False:
                                #materia_encontrada =  materia
    
                #db.child('materia').child(materia_encontrada['Materia_id']).child('observacion').child(o_id).remove()                
                return redirect(url_for('observacion'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el perfil. Inténtalo de nuevo.'
    else:
        return redirect(url_for('horario'))

@app.route('/baja_logica_observacion', methods=['POST'])
def baja_logica_observacion():
    if 'user_id' in SESSION:
        if request.method == 'POST':
            user_id = SESSION['user_id']
            # Recibes los datos actualizados del formulario
            Observacion_id = request.form['Observacion_id']

            try:
                db.child('observacion').child(Observacion_id).update({
                    'Borrado_Logico': True,
                    'Observacion_id': Observacion_id,
                })
                return redirect(url_for('observacion'))
                #return 'Perfil actualizado exitosamente.'
            except:
                return 'Error al actualizar el horario. Inténtalo de nuevo.'
    else:
        return redirect(url_for('observacion'))

@app.route('/borrar_observacion', methods=['POST'])
def borrar_observacion():
    if 'user_id' in SESSION:
        user_id = SESSION['user_id']
        Observacion_id = request.form['Observacion_id']
        try:
            db.child('observacion').child(Observacion_id).remove()
            print('Observacion eliminada')
            return redirect(url_for('plan_estudio'))            
        except:
            return 'Error al eliminar la Observacion.'
    else:
        return redirect(url_for('home'))



@app.route('/reporte')
def reporte():
    try:
        # Obtener datos de la tabla "horario" en Realtime Database
        horarios = db.child('horario').get().val()
        usuarios = db.child('users').get().val()
        materias = db.child('materia').get().val()
        observaciones = db.child('observacion').get().val()
        profesores = db.child('profesor').get().val()
        plan_de_estudio = db.child('plan_estudios').get().val()
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        horarios = None
    # Pasar los datos a la plantilla HTML
    return render_template('reporte.html', horarios=horarios, usuarios=usuarios, materias=materias,
                           observaciones=observaciones, profesores=profesores, plan_de_estudio=plan_de_estudio )


if __name__ == '__main__':
    app.run(debug=True)

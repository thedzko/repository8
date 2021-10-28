from sqlite3.dbapi2 import connect
from flask import Flask, render_template, url_for, request, redirect, session
from datetime import date, datetime
# Importación SQLite
import sqlite3
import os
from werkzeug.utils import escape, secure_filename
import hashlib

from flask.helpers import flash

app = Flask (__name__)
app.secret_key=os.urandom(24)
app.config['USER_IMAGE_UPLOADS'] = "static/img/uploads/user"
app.config['PRODUCT_IMAGE_UPLOADS'] = "static/img/uploads/product"
app.config['PROVIDER_IMAGE_UPLOADS'] = "static/img/uploads/provider"


# Conectar base de datos SQLite
def sql_connection():
    connectDB = sqlite3.connect('inventory.db')
    return connectDB
# Rutas y Funciones

# REGISTRO - USER
#@app.route('/register', methods=['GET','POST'])
#def registro():
#    if request.method == 'POST':
#        usuario = request.form['usuario']
#       lastname = request.form['lastname']
#      email = request.form['email']
#        password = request.form['password']
#        enc=hashlib.sha256(password.encode())
#        pass_enc= enc.hexdigest()
#        user_join = datetime.now()
#        user_age = datetime.now()
#        connectDB = sql_connection()
#        cur = connectDB.cursor()
#        statement = "INSERT INTO users (usuario, lastname,  email, password, user_join, user_age ) VALUES (?, ?, ?, ?, ?, ?)"
#        cur.execute(statement, [usuario, lastname, email, pass_enc, user_join, user_age])
#        connectDB.commit()
#        cur.close
#        return redirect(url_for('panelUsuarios'))
#    else:
#        return render_template('registro.html')


## USUARIOS
# LOGIN- USER
@app.route('/login')
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = escape(request.form['usuario'])
        password = escape(request.form['password'])
        enc= hashlib.sha256(password.encode())
        pass_enc= enc.hexdigest()
        connectDB = sql_connection()
        connectDB.row_factory= sqlite3.Row
        cur = connectDB.cursor()
        statement = "SELECT *FROM users WHERE username = ? AND password =?" 
        cur.execute(statement, [username, pass_enc])
        row=cur.fetchone()
        if row:
            session['usuario'] = username
            session["role"] =row['role']
            if session["role"] == "Superadministrador":
                return redirect ("/usuarios")
            elif session["role"] == "Administrador":
                return redirect ("/usuariosAdmin")
            elif session["role"] == "Empleado":
                return redirect ("/productosUsu")
        else:
            flash("usuario no valido")
        
    else:
        flash ("usuario no valido")
        
    return render_template('login.html')


#@app.route('/usuarios/', methods=['GET'])
#def cantidad_usuarios():
    #connectDB = sql_connection()
    #cur = connectDB.cursor()
   # cur.execute("SELECT * FROM users")
    #user_cant= len(cur.fetchall())

    #return render_template('panelUsuarios.html', cant = user_cant)
    
#print("cantidad usuarios:", cantidad_usuarios())


## USUARIOS
# GET (LIST) - USER
@app.route('/usuarios/', methods=['GET'])
def panelUsuarios():
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM users")
        #Nueva variable para que traiga todo lo de la tabla
        user_data = cur.fetchall()
       #user_cant = len(cur.fetchall())

        return render_template('panelUsuarios.html', users = user_data, UsersCant = len(user_data))

    return redirect("/")


# POST - USER
@app.route('/newUser', methods=['GET','POST'])
def crearUsuario():
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            username = escape(request.form['username'])
            role = escape(request.form['role'])
            password = escape(request.form['password'])
            enc= hashlib.sha256(password.encode())
            pass_enc= enc.hexdigest()
            user_join = escape(datetime.now())
            user_age = escape(datetime.now())
            user_img = request.files['user_img']            
            user_img_path = os.path.join(app.config['USER_IMAGE_UPLOADS'], user_img.filename)
            user_img.save(user_img_path)
            connectDB = sql_connection()
            cur = connectDB.cursor()
            statement = "INSERT INTO users (username, role, password, user_join, user_age, user_img) VALUES (?, ?, ?, ?, ?, ?)"
            cur.execute(statement, [username, role, pass_enc, user_join, user_age, user_img.filename])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelUsuarios'))
        else:
            return render_template('crearUsuario.html')
    return redirect("/")

# GET(SHOW) - USER
@app.route('/showuser/<int:user_id>', methods=['GET'])
def verUsuario(user_id):
    connectDB = sql_connection()
    connectDB.row_factory = sqlite3.Row
    cur = connectDB.cursor()
    consulta = "SELECT * FROM users WHERE user_id=?"
    cur = cur.execute(consulta, [user_id])
    user_data = cur.fetchone()
    cur.close
    return render_template('verUsuario.html', users = user_data)

# EDIT - USER
@app.route('/edituser/<int:user_id>', methods=['GET', 'POST'])
def editarUsuario(user_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM users WHERE user_id=?"
        cur = cur.execute(consulta, [user_id])
        user_data = cur.fetchone()
        cur.close
        return render_template('editarUsuario.html', users = user_data)
    return redirect("/")

# UPDATE - USER
@app.route('/updateuser/<int:user_id>', methods=['GET', 'POST'])
def actualizarUsuario(user_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            connectDB = sql_connection()
            username = escape(request.form['username'])
            role = escape(request.form['role'])
            password = escape(request.form['password'])
            enc= hashlib.sha256(password.encode())
            pass_enc= enc.hexdigest()
            user_img = request.files['user_img']
            user_img_path = os.path.join(app.config['USER_IMAGE_UPLOADS'], user_img.filename)
            user_img.save(user_img_path)
            cur = connectDB.cursor()
            consulta = "UPDATE users SET username = ?, role = ?, password = ?, user_img = ? WHERE user_id = ?"
            cur.execute(consulta, [username, role, pass_enc, user_img.filename, user_id])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelUsuarios'))
        return redirect("/")

# DELETE - USER
@app.route('/deleteuseruser/<int:user_id>', methods=['GET', 'POST'])
def borrarUsuario(user_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute('DELETE FROM users WHERE user_id={0}'.format(user_id))
        connectDB.commit()
        return redirect(url_for('panelUsuarios'))
    return redirect("/")


## PRODUCTOS
# GET (LIST) - PRODUCT
@app.route('/productos/', methods=['GET'])
def panelProductos():
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM products")
        product_data = cur.fetchall()
        return render_template('panelProductos.html', products = product_data,  ProductCant = len(product_data))
    return redirect("/")

# POST - PRODUCT
@app.route('/newProduct/', methods=['GET','POST'])
def crearProducto():
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            productname = escape(request.form['productname'])
            providers = escape(request.form['providers'])
            available_amount = escape(request.form['available_amount'])
            least_amount = escape(request.form['least_amount'])
            product_description = escape(request.form['product_description'])
            product_retail = escape(request.form['product_retail'])
            product_trade = escape(request.form['product_trade'])
            product_img = request.files['product_img']
            product_img_path = os.path.join(app.config['PRODUCT_IMAGE_UPLOADS'], product_img.filename)
            product_img.save(product_img_path)
            connectDB = sql_connection()
            cur = connectDB.cursor()
            statement = "INSERT INTO products (productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, [productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img.filename])
            connectDB.commit()
            cur.close

            return redirect(url_for('panelProductos'))
        else:
            return render_template('crearProducto.html')
    return redirect("/")

# GET(SHOW) - PRODUCT
@app.route('/showproduct/<int:product_id>', methods=['GET'])
def verProducto(product_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM products WHERE product_id=?"
        cur = cur.execute(consulta, [product_id])
        product_data = cur.fetchone()
        cur.close
        return render_template('verProducto.html', products = product_data)
    return redirect("/")

# EDIT - PRODUCT
@app.route('/editproduct/<int:product_id>', methods=['GET', 'POST'])
def editarProducto(product_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM products WHERE product_id=?"
        cur = cur.execute(consulta, [product_id])
        product_data = cur.fetchone()
        cur.close
        return render_template('editarProducto.html', products = product_data)
    return redirect("/")

# UPDATE - PRODUCT
@app.route('/updateproduct/<int:product_id>/', methods=['GET', 'POST'])
def actualizarProducto(product_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            connectDB = sql_connection()
            productname = escape(request.form['productname'])
            providers = escape(request.form['providers'])
            available_amount = escape(request.form['available_amount'])
            least_amount = escape(request.form['least_amount'])
            product_description = escape(request.form['product_description'])
            product_retail = escape(request.form['product_retail'])
            product_trade = escape(request.form['product_trade'])
            product_img = request.files['product_img']
            product_img_path = os.path.join(app.config['PRODUCT_IMAGE_UPLOADS'], product_img.filename)
            product_img.save(product_img_path)
            cur = connectDB.cursor()
            consulta = "UPDATE products SET productname = ?, providers = ?, available_amount = ?, least_amount = ?, product_description = ?, product_retail = ?, product_trade = ?, product_img = ? WHERE product_id = ?"
            cur.execute(consulta, [productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img.filename, product_id])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProductos'))

    return redirect("/")

# DELETE - PRODUCT
@app.route('/deleteproduct/<int:product_id>/', methods=['GET', 'POST'])
def borrarProducto(product_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute('DELETE FROM products WHERE product_id={0}'.format(product_id))
        connectDB.commit()
        return redirect(url_for('panelProductos'))
    return redirect("/")


## PROVEEDORES
# GET (LIST) - PROVIDER
@app.route('/proveedores/', methods=['GET'])
def panelProveedores():
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM providers")
        provider_data = cur.fetchall()
        return render_template('panelProveedores.html', providers = provider_data,  ProvidersCant = len(provider_data))
    return redirect("/")

# POST - PROVIDER
@app.route('/newProvider/', methods=['GET','POST'])
def crearProveedor():
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            providername = escape(request.form['providername'])
            products = escape(request.form['products'])
            phone = escape(request.form['phone'])
            celular = escape(request.form['celular'])
            email = escape(request.form['email'])
            location = escape(request.form['location'])        
            provider_img = request.files['provider_img']
            provider_img_path = os.path.join(app.config['PROVIDER_IMAGE_UPLOADS'], provider_img.filename)
            provider_img.save(provider_img_path)
            connectDB = sql_connection()
            cur = connectDB.cursor()
            statement = "INSERT INTO providers (providername, products, phone, celular, email, location, provider_img) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, [providername, products, phone, celular, email, location, provider_img.filename])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProveedores'))
        else:
            return render_template('crearProveedor.html')
    return redirect("/")

# GET(SHOW) - PROVIDER
@app.route('/showprovider/<int:provider_id>', methods=['GET'])
def verProveedor(provider_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM providers WHERE provider_id=?"
        cur = cur.execute(consulta, [provider_id])
        provider_data = cur.fetchone()
        cur.close
        return render_template('verProveedor.html', providers = provider_data)
    return redirect("/")

# EDIT - PROVIDER
@app.route('/editprovider/<int:provider_id>', methods=['GET', 'POST'])
def editarProveedor(provider_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM providers WHERE provider_id=?"
        cur = cur.execute(consulta, [provider_id])
        provider_data = cur.fetchone()
        cur.close
        return render_template('editarProveedor.html', providers = provider_data)
    return redirect("/")

# UPDATE - PROVIDER
@app.route('/updateprovider/<int:provider_id>', methods=['GET', 'POST'])
def actualizarProveedor(provider_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        if request.method == 'POST':
            connectDB = sql_connection()
            providername = escape(request.form['providername'])
            products = escape(request.form['products'])
            phone = escape(request.form['phone'])
            celular = escape(request.form['celular'])
            email = escape(request.form['email'])
            location = escape(request.form['location'])
            provider_img = request.files['provider_img']
            provider_img_path = os.path.join(app.config['PROVIDER_IMAGE_UPLOADS'], provider_img.filename)
            provider_img.save(provider_img_path)
            cur = connectDB.cursor()
            consulta = "UPDATE providers SET providername = ?, products = ?, phone = ?, celular = ?, email = ?, location = ?, provider_img = ? WHERE provider_id = ?"
            cur.execute(consulta, [providername, products, phone, celular, email, location, provider_img.filename, provider_id])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProveedores'))
    return redirect("/")

# DELETE - PROVIDER
@app.route('/deleteprovider/<int:provider_id>/', methods=['GET', 'POST'])
def borrarProveedor(provider_id):
    if 'usuario' in session and session["role"]== "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute('DELETE FROM providers WHERE provider_id={0}'.format(provider_id))
        connectDB.commit()
        return redirect(url_for('panelProveedores'))
    return redirect("/")

### ADMINISTRADOR 

## ADMIN - USUARIOS
# GET (LIST) - USER
@app.route('/usuariosAdmin/', methods=['GET'])
def panelUsuariosAdmin():
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM users")
        #Nueva variable para que traiga todo lo de la tabla
        user_data = cur.fetchall()
        return render_template('panelUsuariosAdministrador.html', users = user_data,  UserAdCant = len(user_data))
    return redirect("/")

#ADMIN - PRODUCTOS
@app.route('/productosAdmin/', methods=['GET'])
def panelProductosAdmin():
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM products")
        product_data = cur.fetchall()
        return render_template('panelProductosAdministrador.html', products = product_data,  ProductAdCant = len(product_data))
    return redirect("/")

#ADMIN - PROVEEDORES
@app.route('/proveedoresAdmin/', methods=['GET'])
def panelProveedoresAdmin():
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM providers")
        provider_data = cur.fetchall()
        return render_template('panelProveedoresAdministrador.html', providers = provider_data,  ProvidersAdCant = len(provider_data))
    return redirect("/")
#--------------------------------------------------------------------------------------

#ADMIN
# GET(SHOW) - USER
@app.route('/showuserAdmin/<int:user_id>', methods=['GET'])
def verUsuarioAdmin(user_id):
    if 'usuario' in session and session["role"]== "Administrador" or "Superadministrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM users WHERE user_id=?"
        cur = cur.execute(consulta, [user_id])
        user_data = cur.fetchone()
        cur.close
        return render_template('verUsuarioAdministrador.html', users = user_data)
    return redirect("/")

#---------Producto-----------------------------------------------------------------------------------------
#ADMIN
# POST - PRODUCT
@app.route('/newProductAdmin/', methods=['GET','POST'])
def crearProductoAdmin():
    if 'usuario' in session and session["role"]== "Administrador":
        if request.method == 'POST':
            productname = escape(request.form['productname'])
            providers = escape(request.form['providers'])
            available_amount = escape(request.form['available_amount'])
            least_amount = escape(request.form['least_amount'])
            product_description = escape(request.form['product_description'])
            product_retail = escape(request.form['product_retail'])
            product_trade = escape(request.form['product_trade'])
            product_img = request.files['product_img']
            product_img_path = os.path.join(app.config['PRODUCT_IMAGE_UPLOADS'], product_img.filename)
            product_img.save(product_img_path)
            connectDB = sql_connection()
            cur = connectDB.cursor()
            statement = "INSERT INTO products (productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, [productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img.filename])
            connectDB.commit()
            cur.close

            return redirect(url_for('panelProductosAdmin'))
        else:
            return render_template('crearProductoAdministrador.html')
    return redirect("/")

# GET(SHOW) - PRODUCT
@app.route('/showproductAdmin/<int:product_id>', methods=['GET'])
def verProductoAdmin(product_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM products WHERE product_id=?"
        cur = cur.execute(consulta, [product_id])
        product_data = cur.fetchone()
        cur.close
        return render_template('verProductoAdministrador.html', products = product_data)
    return redirect("/")

# EDIT - PRODUCT
@app.route('/editproductAdmin/<int:product_id>', methods=['GET', 'POST'])
def editarProductoAdmin(product_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM products WHERE product_id=?"
        cur = cur.execute(consulta, [product_id])
        product_data = cur.fetchone()
        cur.close
        return render_template('editarProductoAdministrador.html', products = product_data)
    return redirect("/")

# UPDATE - PRODUCT
@app.route('/updateproductAdmin/<int:product_id>', methods=['GET', 'POST'])
def actualizarProductoAdmin(product_id):
    if 'usuario' in session and session["role"]== "Administrador":
        if request.method == 'POST':
            connectDB = sql_connection()
            productname = escape(request.form['productname'])
            providers = escape(request.form['providers'])
            available_amount = escape(request.form['available_amount'])
            least_amount = escape(request.form['least_amount'])
            product_description = escape(request.form['product_description'])
            product_retail = escape(request.form['product_retail'])
            product_trade = escape(request.form['product_trade'])
            product_img = request.files['product_img']
            product_img_path = os.path.join(app.config['PRODUCT_IMAGE_UPLOADS'], product_img.filename)
            product_img.save(product_img_path)
            cur = connectDB.cursor()
            consulta = "UPDATE products SET productname = ?, providers = ?, available_amount = ?, least_amount = ?, product_description = ?, product_retail = ?, product_trade = ?, product_img = ? WHERE product_id = ?"
            cur.execute(consulta, [productname, providers, available_amount, least_amount, product_description, product_retail, product_trade, product_img.filename, product_id])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProductosAdmin'))
    return redirect ("/")

# DELETE - PRODUCT
@app.route('/deleteproductAdmin/<int:product_id>/', methods=['GET', 'POST'])
def borrarProductoAdmin(product_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute('DELETE FROM products WHERE product_id={0}'.format(product_id))
        connectDB.commit()
        return redirect(url_for('panelProductosAdmin'))
    return redirect("/")

#-----proveedor-----------------------------------------------------------------------------

#ADMIN
# GET(SHOW) - PROVIDER
@app.route('/showproviderAdmin/<int:provider_id>', methods=['GET'])
def verProveedorAdmin(provider_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM providers WHERE provider_id=?"
        cur = cur.execute(consulta, [provider_id])
        provider_data = cur.fetchone()
        cur.close
        return render_template('verProveedorAdministrador.html', providers = provider_data)
    return redirect("/")

# POST - PROVIDER
@app.route('/newProviderAdmin/', methods=['GET','POST'])
def crearProveedorAdmin():
    if 'usuario' in session and session["role"]== "Administrador":
        if request.method == 'POST':
            providername = escape(request.form['providername'])
            products = escape(request.form['products'])
            phone = escape(request.form['phone'])
            celular = escape(request.form['celular'])
            email = escape(request.form['email'])
            location = escape(request.form['location'])        
            provider_img = request.files['provider_img']
            provider_img_path = os.path.join(app.config['PROVIDER_IMAGE_UPLOADS'], provider_img.filename)
            provider_img.save(provider_img_path)
            connectDB = sql_connection()
            cur = connectDB.cursor()
            statement = "INSERT INTO providers (providername, products, phone, celular, email, location, provider_img) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cur.execute(statement, [providername, products, phone, celular, email, location, provider_img.filename])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProveedoresAdmin'))
        else:
            return render_template('crearProveedorAdministrador.html')
    return redirect("/")

#ADMIN
# EDIT - PROVIDER
@app.route('/editproviderAdmin/<int:provider_id>', methods=['GET', 'POST'])
def editarProveedorAdmin(provider_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM providers WHERE provider_id=?"
        cur = cur.execute(consulta, [provider_id])
        provider_data = cur.fetchone()
        cur.close
        return render_template('editarProveedorAdministrador.html', providers = provider_data)
    return redirect("/")

#ADMIN
# UPDATE - PROVIDER
@app.route('/updateproviderAdmin/<int:provider_id>', methods=['GET', 'POST'])
def actualizarProveedorAdmin(provider_id):
    if 'usuario' in session and session["role"]== "Administrador":
        if request.method == 'POST':
            connectDB = sql_connection()
            providername = escape(request.form['providername'])
            products = escape(request.form['products'])
            phone = escape(request.form['phone'])
            celular = escape(request.form['celular'])
            email = escape(request.form['email'])
            location = escape(request.form['location'])
            provider_img = request.files['provider_img']
            provider_img_path = os.path.join(app.config['PROVIDER_IMAGE_UPLOADS'], provider_img.filename)
            provider_img.save(provider_img_path)
            cur = connectDB.cursor()
            consulta = "UPDATE providers SET providername = ?, products = ?, phone = ?, celular = ?, email = ?, location = ?, provider_img = ? WHERE provider_id = ?"
            cur.execute(consulta, [providername, products, phone, celular, email, location, provider_img.filename, provider_id])
            connectDB.commit()
            cur.close
            return redirect(url_for('panelProveedoresAdmin'))
    return redirect("/")

# DELETE - PROVIDER
@app.route('/deleteproviderAdmin/<int:provider_id>/', methods=['GET', 'POST'])
def borrarProveedorAdmin(provider_id):
    if 'usuario' in session and session["role"]== "Administrador":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute('DELETE FROM providers WHERE provider_id={0}'.format(provider_id))
        connectDB.commit()
        return redirect(url_for('panelProveedoresAdmin'))
    return redirect("/")


#----Usuario------------------------------------------------------------------------------------------

## USUARIO- PRODUCTOS
# GET (LIST) - PRODUCT
@app.route('/productosUsu/', methods=['GET'])
def panelProductosusu():
    if 'usuario' in session and session["role"]== "Empleado":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM products")
        product_data = cur.fetchall()
        return render_template('panelProductosUsuario.html', products = product_data,  ProductUsCant = len(product_data))
    return redirect("/")

## USUARIO - PROVEEDORES
# GET (LIST) - PROVIDER
@app.route('/proveedoresUsu/', methods=['GET'])
def panelProveedoresusu():
    if 'usuario' in session and session["role"]== "Empleado":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        cur.execute("SELECT * FROM providers")
        provider_data = cur.fetchall()
        return render_template('panelProveedoresUsuario.html', providers = provider_data,  ProvidersUsCant = len(provider_data))
    return redirect("/")

#USUARIO - VER PRODUCTO
# GET(SHOW) - PRODUCT
@app.route('/showproductusu/<int:product_id>', methods=['GET'])
def verProductousu(product_id):
    if 'usuario' in session and session["role"]== "Empleado":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM products WHERE product_id=?"
        cur = cur.execute(consulta, [product_id])
        product_data = cur.fetchone()
        cur.close
        return render_template('verProductoUsuario.html', products = product_data)
    return redirect("/")

# GET(SHOW) - PROVIDER
@app.route('/showproviderusu/<int:provider_id>', methods=['GET'])
def verProveedorusu(provider_id):
    if 'usuario' in session and session["role"]== "Empleado":
        connectDB = sql_connection()
        connectDB.row_factory = sqlite3.Row
        cur = connectDB.cursor()
        consulta = "SELECT * FROM providers WHERE provider_id=?"
        cur = cur.execute(consulta, [provider_id])
        provider_data = cur.fetchone()
        cur.close
        return render_template('verProveedorUsuario.html', providers = provider_data)
    return redirect("/")
#------------------------------------------------------------------------------------------
@app.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect ("/")


if __name__ == '__main__':
    app.debug = True
    app.run()
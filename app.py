from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/s_almacen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo para los productos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    precio = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Producto {self.nombre}>'

# Crear la base de datos si no existe
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    print(f'Error al crear la base de datos: {e}')

@app.route('/')
def ventas():
    productos = Producto.query.all()  # Obtener todos los productos de la base de datos
    return render_template('index.html', productos=productos)  # Utilizar index.html para ventas

@app.route('/comprar/<int:id>', methods=['POST'])
def comprar_producto(id):
    # Obtener el producto a comprar
    producto = Producto.query.get_or_404(id)

    # Obtener la cantidad comprada desde el formulario
    cantidad_comprada = int(request.form['cantidad'])

    # Verificar si hay suficiente stock
    if producto.stock >= cantidad_comprada:
        # Actualizar el stock restando la cantidad comprada
        producto.stock -= cantidad_comprada
        db.session.commit()
        return redirect(url_for('index'))  # Redirigir al módulo de ventas
    else:
        # Si no hay suficiente stock, mostrar un error (podrías manejar esto de forma más visual)
        return "No hay suficiente stock disponible", 400


@app.route('/stock')
def index():
    productos = Producto.query.all()
    return render_template('stock.html', productos=productos)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_producto(id):
    producto = Producto.query.get_or_404(id)  # Obtener el producto por ID

    if request.method == 'POST':
        producto.nombre = request.form['nombre']
        producto.stock = request.form['stock']
        producto.precio = request.form['precio']
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('update_product.html', producto=producto)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/create', methods=['GET', 'POST'])
def create_producto():
    if request.method == 'POST':
        nombre = request.form['nombre']
        stock = request.form['stock']
        precio = request.form['precio']
        
        # Crear una nueva instancia de Producto
        nuevo_producto = Producto(nombre=nombre, stock=stock, precio=precio)
        
        # Agregar y guardar en la base de datos
        db.session.add(nuevo_producto)
        db.session.commit()
        
        return redirect(url_for('index'))  # Redirigir a la lista de productos

    return render_template('create_producto.html')  # Renderizar el formulario si es un GET

if __name__ == '__main__':
    app.run(debug=True)


from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///menu.db'
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Initialize the database when the application starts
with app.app_context():
    db.create_all()


@app.route('/products', methods=['POST'])
def create_product():
    data = request.get_json()
    new_product = Product(name=data['name'], price=data['price'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"message": "Product created", "product": {"id": new_product.id, "name": new_product.name, "price": new_product.price}}), 201

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({"id": product.id, "name": product.name, "price": product.price})
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/products', methods=['GET'])
def get_all_products():
    products = Product.query.all()
    products_list = [{"id": p.id, "name": p.name, "price": p.price} for p in products]
    return jsonify(products_list)

@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.get_json()
    product = Product.query.get(product_id)
    if product:
        product.name = data.get('name', product.name)
        product.price = data.get('price', product.price)
        db.session.commit()
        return jsonify({"message": "Product updated", "product": {"id": product.id, "name": product.name, "price": product.price}})
    else:
        return jsonify({"error": "Product not found"}), 404

@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted", "product": {"id": product.id, "name": product.name, "price": product.price}})
    else:
        return jsonify({"error": "Product not found"}), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

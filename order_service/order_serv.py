from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from requests import get

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'  # Adjust the name as needed
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product = db.relationship('Product', backref=db.backref('orders', lazy=True))
    
    # Add other fields as needed

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)

# Initialize the database when the application starts
with app.app_context():
    db.create_all()

# Routes for the Order Service

@app.route('/orders', methods=['GET'])
def get_all_orders():
    orders = Order.query.all()
    order_list = [{"id": order.id, "product_id": order.product_id, "product_name": order.product.name} for order in orders]
    return jsonify(order_list)

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify({"id": order.id, "product_id": order.product_id, "product_name": order.product.name})
    else:
        return jsonify({"error": "Order not found"}), 404

@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        product_id = data.get('product_id')

        # Ensure product_id is provided
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400

        # Check if the product exists in the Product Service
        product_response = get(f"http://menu_serv:5001/products/{product_id}")

        if product_response.status_code == 200:
            product_data = product_response.json()
            order = Order(product_id=product_id, product=Product(name=product_data['name'], price=product_data['price']))
            db.session.add(order)
            db.session.commit()
            return jsonify({"message": "Order created", "order": {"id": order.id, "product_id": order.product_id, "product_name": order.product.name}}), 201
        else:
            return jsonify({"error": "Product not found"}), 404

    except Exception as e:
        db.session.rollback()  # Rollback changes in case of an error
        print(f"Exception: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)
    if order:
        data = request.get_json()
        product_id = data.get('product_id', order.product_id)
        
        # Check if the product exists in the Product Service
        product_response = get(f"http://menu_serv:5001/products/{product_id}")
        
        if product_response.status_code == 200:
            product_data = product_response.json()
            order.product_id = product_id
            order.product = Product(name=product_data['name'], price=product_data['price'])
            db.session.commit()
            return jsonify({"message": "Order updated", "order": {"id": order.id, "product_id": order.product_id, "product_name": order.product.name}}), 200
        else:
            return jsonify({"error": "Product not found"}), 404
    else:
        return jsonify({"error": "Order not found"}), 404

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    order = Order.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({"message": "Order canceled", "order": {"id": order.id, "product_id": order.product_id, "product_name": order.product.name}}), 200
    else:
        return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)

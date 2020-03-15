from flask import Flask, request, jsonify
from flask_restplus import Api, Resource, fields
from werkzeug.contrib.fixers import ProxyFix
from db import connection, execute_query, execute_read_query
app = Flask(__name__)

import os
import json

# init app 
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.0', title='Product Management API',
    description='A Product Management API',
)


basedir = os.path.abspath(os.path.dirname(__file__))





productRoutes = api.namespace('product-management/api', description='Product operations')


class ProductModel:
  def __init__(self, name, description, price, qty):
    self.name = name
    self.description = description
    self.price = price
    self.qty = qty


product = api.model('Product', {
    'id': fields.Integer(readonly=True, description='The Product unique identifier'),
    'name': fields.String(required=True, description='The name of the product'),
    'description': fields.String(required=True, description='The description of the product'),
    'price': fields.Float(required=True, description='The price of the product'),
    'qty': fields.Integer(required=True, description='the quantity of the product'),
})



@productRoutes.route('/products')
class ProductsList(Resource):
	def get(self):
		''' Get All Products'''
		all_products_query = "SELECT * from products"
		products = execute_read_query(all_products_query)
		productsList = []
		for product in products:
			print(products)
			productsList.append(vars(ProductModel(product[1],product[2],product[3],product[4])))
		return productsList, 200


@productRoutes.route('/product/<int:id>')
class Products(Resource):
	def get(self,id):
		single_product_query = f"SELECT * FROM products WHERE id={id}"
		product = execute_read_query(single_product_query)
		if(product == []):
			return ("ID {} does not exist".format(id), 404)
		else:	
			return product, 200
	
	def delete(self,id):
		single_product_query = f"SELECT * FROM products WHERE id={id}"
		product = execute_read_query(single_product_query)
		if(product == []):
			return ("ID {} does not exist".format(id), 404)
		else:	
			cursor = connection.cursor(buffered=True)
			cursor.execute(f"DELETE FROM products WHERE id={id}")
			return ("ID {} deleted".format(id), 204)

	@productRoutes.expect(product)
	def put(self,id):
		name = request.json.get("name")
		description = request.json.get("description")
		price = request.json.get("price")
		qty = request.json.get("qty")

		single_product_query = f"SELECT * FROM products WHERE id={id}"
		product = execute_read_query(single_product_query)
		if(product == []):
			return ("ID {} does not exist".format(id), 404)
		else:
			cursor = connection.cursor(buffered=True)
			cursor.execute(f"""
				UPDATE products 
				SET 
					name = '{name}',
					description = '{description}',
					price = '{price}',
					qty = '{qty}'
				WHERE id = {id}
				""")
			cursor.execute(f"SELECT * FROM products WHERE id={id}")
			product = cursor.fetchone()
			return product, 200


@productRoutes.route('/product')
@productRoutes.expect(product)
class Products(Resource):
 	def post(self):
 		name = request.json.get("name")
 		description = request.json.get("description")
 		price = request.json.get("price")
 		qty = request.json.get("qty")

 		insert_product_query = f"INSERT INTO products(name, description, price, qty) VALUES ('{name}', '{description}', '{price}', '{qty}')"
 		product = execute_read_query(insert_product_query)
 		return ("Product added successfully", 200)



# Run Server
if __name__ == '__main__':
	app.run(debug=True)

import os
import random

from flask import (
	Flask,
	redirect,
	request,
	render_template,
	url_for,
	session
)


app = Flask(__name__)
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'


class Product:
	def __init__(self):
		self.id = random.random()
		self.title = random.random()
		self.vendor = "fromairstore"
		self.product_type = "art"

	def price_range(self):
		return 100


@app.route("/")
def hello():
	products = []
	for _ in range(3):
		products.append(Product())
	
	session["products_count"] = len(products)
	session["product_1_title"] = products[0].title
	session["product_2_title"] = products[1].title
	session["product_3_title"] = products[2].title

	return render_template('products.html', products=products)


@app.route('/logout')
def shopify_app_logout():
    return redirect(url_for('hello'))


@app.route('/root')
def root_path():
    return redirect(url_for('hello'))


@app.route('/send_email')
def send_email():
    return redirect(url_for('hello'))


if __name__ == "__main__":
	app.run(
		host=os.getenv('IP', '0.0.0.0'), 
		port=int(os.getenv('PORT', 4444))
	)
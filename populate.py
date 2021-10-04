# Mock method to populate data to a Shopify store
# This is used only for development purpose
import io
import requests
import random
from typing import List
from time import sleep

import shopify
from faker import Faker


ACCESS_TOKEN = "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"  # Temporary use only
API_VERSION = "2020-10"
SHOP_URL = "fromairstore.myshopify.com"


class Populate:
	def __init__(self, access_token: str, shop_url: str, api_version: str):
		"""
		Initialize a populate object

		Args:
			access_token (str): shopify API access token
			shop_url (str): shopify shop URL
			api_version (str): shopify API version
		"""
		self.token = access_token
		self.shop_url = shop_url
		self.api_version = api_version

		random.seed(42)

		session = shopify.Session(shop_url, api_version, access_token)
		shopify.ShopifyResource.activate_session(session)

		self.existing_customers = None
		self.existing_products = None

	def get_customers(self) -> List:
		if not self.existing_customers:
			self.existing_customers = shopify.Customer.find()

		return self.existing_customers

	def get_products(self) -> List:
		if not self.existing_products:
			self.existing_products = shopify.Product.find()

		return self.existing_products

	def generate_customer(self):
		"""Add customers with random fake information to the shop
		"""
		fake = Faker()
		names = fake.name().split(' ')

		customer = shopify.Customer()
		customer.first_name = names[0]
		customer.last_name = names[1]
		customer.email = "{0}{1}@gmail.com".format(names[0], names[1])
		customer.save()

	def generate_products(self):
		"""Generate fake products
		"""
		NotImplemented

	def generate_order(self):
		"""Generate an order for a customer to purchase a product
		"""
		customer = random.choice(self.get_customers())
		product = random.choice(self.get_products())

		order = shopify.Order()
		order.customer = {
			"first_name": customer.first_name,
			"last_name": customer.last_name,
			"email": customer.email
		}
		order.fulfillment_status = "fulfilled"
		order.line_items = [
			{
				"title": product.title,
				"quantity": 1,
				"price": product.price_range()
			}
		]
		order.save()


if __name__ == "__main__":
	populator = Populate(access_token=ACCESS_TOKEN, shop_url=SHOP_URL, api_version=API_VERSION)

	# generate 5 fake customers
	for _ in range(5):
		populator.generate_customer()
		sleep(0.5)
	
	# generate 10 fake orders with random customer and product
	for _ in range(5):
		populator.generate_order()
		sleep(1)


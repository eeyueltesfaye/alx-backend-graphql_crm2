from crm.models import Customer, Product
import random

def seed_data():
    customers = [
        {"name": "John Doe", "email": "john@example.com"},
        {"name": "Jane Doe", "email": "jane@example.com"},
    ]
    for c in customers:
        Customer.objects.get_or_create(name=c["name"], email=c["email"])

    products = [
        {"name": "Phone", "price": 299.99, "stock": 50},
        {"name": "Tablet", "price": 199.99, "stock": 30},
    ]
    for p in products:
        Product.objects.get_or_create(name=p["name"], price=p["price"], stock=p["stock"])

    print("Seeded initial data.")

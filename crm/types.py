# crm/types.py

import graphene
from graphene_django import DjangoObjectType
from crm.models import Customer, Product, Order


class CustomerNode(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"  # includes name, email, phone, created_at
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "email": ["exact", "icontains"],
        }
        interfaces = (graphene.relay.Node,)


class ProductNode(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"  # includes name, price, stock
        filter_fields = {
            "name": ["exact", "icontains", "istartswith"],
            "price": ["exact", "lte", "gte"],
        }
        interfaces = (graphene.relay.Node,)


class OrderNode(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"  # includes customer, products, order_date, total_amount
        filter_fields = {
            "customer__name": ["icontains"],
            "order_date": ["exact", "gte", "lte"],
            "total_amount": ["exact", "gte", "lte"],
        }
        interfaces = (graphene.relay.Node,)

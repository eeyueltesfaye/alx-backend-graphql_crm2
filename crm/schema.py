import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from decimal import Decimal

# GraphQL types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    totalAmount = graphene.Float()  # override to use Float

    class Meta:
        model = Order
        fields = "__all__"

    def resolve_totalAmount(self, info):
        return float(self.total_amount)  # convert Decimal to float

# Define an Input Type Outside the Mutation
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


# CreateCustomer Mutation
class CreateCustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CreateCustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        customer = Customer(
            name=input.name,
            email=input.email,
            phone=input.phone or ""
        )
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")


# BulkCreateCustomers Mutation
class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        customers = []
        errors = []

        for data in input:
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise ValidationError(f"Email '{data.email}' already exists.")
                customer = Customer(name=data.name, email=data.email, phone=data.phone or "")
                customer.full_clean()
                customer.save()
                customers.append(customer)
            except Exception as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=customers, errors=errors)


# CreateProduct Mutation
class CreateProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = CreateProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")
        product = Product(name=input.name, price=Decimal(input.price), stock=input.stock)
        product.save()
        return CreateProduct(product=product)

# CreateOrder Mutation
class CreateOrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()

class CreateOrder(graphene.Mutation):
    class Arguments:
        input = CreateOrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product must be selected")

        products = []
        total = Decimal('0.00')  # Start with Decimal
        for pid in input.product_ids:
            try:
                product = Product.objects.get(id=pid)
                products.append(product)
                total += product.price  # Leave it as Decimal
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order(customer=customer, order_date=input.order_date or timezone.now(), total_amount=total)
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)


# Combine Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()

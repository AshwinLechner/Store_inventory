from collections import OrderedDict
import datetime
import csv
import os

from peewee import *


db = SqliteDatabase("inventory.db")


class Product(Model):
    product_id = IntegerField(primary_key=True)
    product_name = CharField(max_length=255, unique=True)
    product_quantity = IntegerField()
    product_price = IntegerField()
    date_updated = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = db


def show_menu():
    choise = None

    while choise != 'q':
        print("Enter 'q'to quit. ")
        for key, value in menu.items():
            print('{}) {}'.format(key, value.__doc__))
        choise = input("Action: ").lower().strip()
        if choise in menu:
            menu[choise]()


def read_csv():
    """Reads the csv and adds it to Product"""
    with open("inventory.csv", newline="") as csvfile:
        inventory_reader = csv.DictReader(csvfile, delimiter=',')
        rows = list(inventory_reader)
        for row in rows:
            row['product_quantity'] = int(row['product_quantity'])
            row['product_price'] = int(
                row['product_price'].replace('$', '').replace('.', ''))
            row['date_updated'] = datetime.datetime.strptime(
                row['date_updated'], '%m/%d/%Y')
        for row in rows:
            try:
                Product.create(
                    product_name=row['product_name'],
                    product_quantity=row['product_quantity'],
                    product_price=row['product_price'],
                    date_updated=row['date_updated'],).save()
            except IntegrityError:
                product_record = Product.get(product_name=row['product_name'])
                product_record.product_quantity = row['product_quantity']
                product_record.product_price = row['product_price']
                product_record.date_updated = row['date_updated']
                product_record.save()


def view_product():
    """View product"""

    while True:
        clear()
        try:
            product_choise = int(input("Please select a product by id "))
        except ValueError:
            print('Please select a number')
        product_by_id = Product.select().where(Product.product_id == product_choise)
        if product_by_id:
            clear()
            for product in product_by_id:
                print(
                    f'{product.product_name} has a cost of ${float(product.product_price / 100)} and currently there are {product.product_quantity} left')
        else:
            print('Sorry, that is nor a valid product id')

        next_action = input(
            'Do you want to view another product? If not enter "Q"').lower().strip()
        if next_action == 'q':
            clear()
            break


def add_product():
    """Add product to list """
    clear()
    name = input('What is the name of the product? ')
    while True:
        try:
            price = float((input('how much does it cost? $')))
            price = int(price * 100)
            break
        except ValueError:
            print('Please enter a number')
    while True:
        try:
            quantity = int(input('How much units are there of the product? '))
            break
        except ValueError:
            print('please select a number')

    if name and quantity and price:
        if input('Are you sure you want to save? [Y/N]? ').lower() != 'n':
            try:
                Product.create(
                    product_name=name,
                    product_price=price,
                    product_quantity=quantity)
            except IntegrityError:
                new_product = Product.get(product_name=name)
                new_product.product_quantity = quantity
                new_product.product_price = price
                new_product.date_updated = datetime.datetime.now()
                new_product.save()
            print('Product saved succesfuly!')
        else:
            print('Product not saved.')


def make_backup():
    """Make a backup"""
    clear()
    with open('backup.csv', 'w', newline='') as csvfile:
        products = Product.select()
        fieldnames = [
            'product_name',
            'product_price',
            'product_quantity',
            'date_updated']
        productwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)

        productwriter.writeheader()
        for product in products:
            productwriter.writerow({
                'product_name': product.product_name,
                'product_quantity': product.product_quantity,
                'product_price': product.product_price,
                'date_updated': product.date_updated
            })
    print('Backup succusfull')


menu = OrderedDict([
    ('v', view_product),
    ('a', add_product),
    ('b', make_backup),
])


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def initialize():
    db.connect()
    db.create_tables([Product], safe=True)
    read_csv()
    show_menu()


if __name__ == "__main__":
    clear()
    initialize()

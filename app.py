# postgres://ekhvxozlzadlsj:w9UAwkNF6VAPB7esKYIa_YIZCV@ec2-54-163-238-73.compute-1.amazonaws.com:5432/d8jq3vd1qcp65s
# postgres://ekhvxozlzadlsj:w9UAwkNF6VAPB7esKYIa_YIZCV@ec2-54-163-238-73.compute-1.amazonaws.com:5432/d8jq3vd1qcp65s
# psql postgres://manuelsolorzano:qwe123@localhost:5432/angelhackinvoicebot

# drop schema public cascade;
# create schema public;


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import json

from xmlparser import parse_xml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://manuelsolorzano:qwe123@localhost:5432/angelhackinvoicebot'
db = SQLAlchemy(app)


class Flag(db.Model):
    __tablename__ = 'flag'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(100))
    flag = db.Column(db.String(100))


class UploadInvoiceTmp(db.Model):
    __tablename__ = 'upload_invoice_tmp'
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.String(100))
    invoice_id = db.Column(db.String(100))
    invoice_price = db.Column(db.String(100))
    invoice_date = db.Column(db.String(100))


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))
    description = db.Column(db.String(100))

    # retail_id = db.Column(db.String(100)) # plazavea

    # store_id = db.Column(db.String(100))
    # store_name = db.Column(db.String(100))

    # store_lat = db.Column(db.String(100))
    # store_lot = db.Column(db.String(100))

    product_id = db.Column(db.String(100))

    price = db.Column(db.String(100))
    unit_code = db.Column(db.String(100))

    default_uc = db.Column(db.Boolean)

    fb_id = db.Column(db.String(100))
    invoice_id = db.Column(db.String(100))


db.create_all()
db.session.commit()


def get_products_by_query(product_name, unit_code, quantity):
    q = (
        db
        .session
        .query(Product.price.label('price'))
        .filter(Product.name.contains(product_name))
        .filter(Product.unit_code == unit_code)
        .first()
    )

    if q is None:
        return None

    return q.price * quantity


def print_insert_sql_from_xml_file(file_path):
    data = parse_xml(file_path=file_path)
    invoice_id = data['invoice_id']
    invoice_date = data['invoice_date']
    invoice_amount = data['invoice_amount']
    for p in data['products']:
        sql = """
            INSER INTO product (name, description, product_id, price, unit_code, default_uc, invoice_id, fb_id)
            values ('{}', '{}', '{}', '{}', '{}', {}, '{}', '{}');
        """

        sql = sql.format(
            "''",
            p['description'],
            p['retail_prod_id'],
            p['price'],
            p['unit_code'],
            'false',
            invoice_id,
            'apsdjpasd'
        )
        print sql


def insert_products_from_xml_file(file_path):
    data = parse_xml(file_path=file_path)
    invoice_id = data['invoice_id']
    invoice_date = data['invoice_date']
    invoice_amount = data['invoice_amount']
    for p in data['products']:
        tmp = Product(
            description=p['description'],
            price=p['price'],
            product_id=p['retail_prod_id'],
            unit_code=p['unit_code'],
            invoice_id=invoice_id,
        )
        db.session.add(tmp)
        db.session.commit()


def insert_products_from_url(url_path):
    data = parse_xml(url_path=url_path)
    invoice_id = data['invoice_id']
    invoice_date = data['invoice_date']
    invoice_amount = data['invoice_amount']
    for p in data['products']:
        tmp = Product(
            description=p['description'],
            price=p['price'],
            product_id=p['retail_prod_id'],
            unit_code=p['unit_code'],
            invoice_id=invoice_id,
        )
        db.session.add(tmp)
        db.session.commit()


@app.route('/')
def hello_world():

    print_insert_sql_from_xml_file(file_path='xml/BA46-1183868.xml')
    print_insert_sql_from_xml_file(file_path='xml/BA50-3376938.xml')
    print_insert_sql_from_xml_file(file_path='xml/BA55-2081122.xml')
    print_insert_sql_from_xml_file(file_path='xml/BA55-2359138.xml')
    print_insert_sql_from_xml_file(file_path='xml/BA55-2381584.xml')
    print_insert_sql_from_xml_file(file_path='xml/BA63-3069121.xml')

    insert_products_from_xml_file(file_path='xml/BA46-1183868.xml')
    insert_products_from_xml_file(file_path='xml/BA50-3376938.xml')
    insert_products_from_xml_file(file_path='xml/BA55-2081122.xml')
    insert_products_from_xml_file(file_path='xml/BA55-2359138.xml')
    insert_products_from_xml_file(file_path='xml/BA55-2381584.xml')
    insert_products_from_xml_file(file_path='xml/BA63-3069121.xml')

    return 'Hello, World!'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

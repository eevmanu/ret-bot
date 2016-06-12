#!/usr/bin/python
# coding=utf-8

# postgres://ekhvxozlzadlsj:w9UAwkNF6VAPB7esKYIa_YIZCV@ec2-54-163-238-73.compute-1.amazonaws.com:5432/d8jq3vd1qcp65s
# postgres://ekhvxozlzadlsj:w9UAwkNF6VAPB7esKYIa_YIZCV@ec2-54-163-238-73.compute-1.amazonaws.com:5432/d8jq3vd1qcp65s
# psql postgres://manuelsolorzano:qwe123@localhost:5432/angelhackinvoicebot

# drop schema public cascade;
# create schema public;


from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
import json
import requests
from xmlparser import parse_xml
from arm import get_recommended_product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://manuelsolorzano:qwe123@localhost:5432/angelhackinvoicebot'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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


def get_price_from_human_query(product_name, unit_code, quantity):

    product_name = product_name.upper()
    print '*' * 100
    print product_name
    print unit_code
    print quantity
    q = (
        db
        .session
        .query(Product.price.label('price'))
        .filter(Product.name.contains(product_name))
        .filter(Product.unit_code == unit_code)
    )
    # print q
    q = q.first()
    # print q

    if q is None:
        return 0

    return float(q.price) * float(quantity)


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


API_ROOT = '/api/'
FB_WEBHOOK = 'fb_webhook'

access_token = 'EAAPO2JRJUlgBAC1bYkUPZBnePZA9ta1EsEvi7I6FKvNcU5EmYvQ5dAe7aN0l8zcnhDkW3wl3xaCP6aZB6sqbveG7FgPtZBvaT2isaHjQnjaqs0XA0GhKw6TAovQOeZCfwSp6XMYCxmzAEeYJtw8JZAuDkf63QPEmM3vW4nfJVf5gZDZD'
url_base = 'https://graph.facebook.com/v2.6/me/messages?access_token={}'.format(access_token)
url_parser_price = 'https://www.wolframcloud.com/objects/user-6a1f03ec-fe00-4993-ae56-6d3117a9bd99/retbot/parser'
url_parser_almacenar = 'https://www.wolframcloud.com/objects/user-6a1f03ec-fe00-4993-ae56-6d3117a9bd99/retbot/parserinfo'

image_codigo = 'http://beanimalheroes.org/es/wp-content/uploads/2016/03/foca-arpa-bebe.jpg'

MENSAJE_NO_ENTIENDO = u'Habla bien'
CUAL_MONTO = u'¿Cuál fue el monto total?'
CUAL_FECHA = u'Envíanos primero la fecha de tu compra'
CUAL_CODIGO = u'Envíenos el código de la boleta (guíese de la imagen)'


@app.route(API_ROOT + FB_WEBHOOK, methods=["GET"])
def fb_webhook():
    verification_code = 'ret_bot'
    verify_token = request.args.get('hub.verify_token')
    if verification_code == verify_token:
        return request.args.get('hub.challenge')


FLAG_N = '1'
FLAG_P = '2'
FLAG_A = '3'


@app.route(API_ROOT + FB_WEBHOOK, methods=['POST'])
def fb_receive_message():
    tmp = json.loads(request.data.decode('utf8'))
    # print json.dumps(tmp, indent=4, sort_keys=True)

    message_entries = tmp['entry']

    for entry in message_entries:

        messagings = entry['messaging']

        for message in messagings:

            sender = message['sender']['id']
            recipient = message['recipient']['id']

            # sender == user_id == fb_id

            if message.get('postback'):

                option = message['postback']['payload']
                if option == 'Precio':

                    send_message(sender, u'¿De qué producto deseas saber el precio?')
                    flag = db.session.query(Flag).filter(Flag.user_id == sender).first()
                    if flag is None:
                        flag = Flag(user_id=sender, flag=FLAG_P)
                        db.session.add(flag)
                        db.session.commit()
                    else:
                        flag.flag = FLAG_P
                        db.session.commit()

                elif option == 'Compartir':

                    send_message(sender, CUAL_FECHA)
                    flag = db.session.query(Flag).filter(Flag.user_id == sender).first()
                    if flag is None:
                        flag = Flag(user_id=sender, flag=FLAG_A)
                        db.session.add(flag)
                        db.session.commit()
                    else:
                        flag.flag = FLAG_A
                        db.session.commit()

                    tmp = db.session.query(UploadInvoiceTmp).filter(UploadInvoiceTmp.user_id == sender).first()
                    if tmp is None:
                        tmp = UploadInvoiceTmp(user_id=sender)
                        db.session.add(tmp)
                        db.session.commit()
                    else:
                        tmp.invoice_date = ''
                        tmp.invoice_id = ''
                        tmp.invoice_price = ''
                        db.session.commit()

                elif option == 'Precio2':
                    q = (
                        db
                        .session
                        .query(
                            Product.invoice_id.label('invoice_id'),
                            Product.name.label('name'),
                            Product.price.label('price')
                        )
                        .all()
                    )
                    transaction_ids = list(set([x.invoice_id for x in q]))
                    l = []
                    for t_id in transaction_ids:
                        l.append([(x.name, x.price) for x in q if x.invoice_id == t_id])
                    p = get_recommended_product(transactions=l)
                    send_message(sender, 'el producto sugerido es {} y su precio es {}'.format(p[0], p[1]))

                return 'chau postback'

            if message.get('message'):
                # return 'Hi'

                if 'message' not in message:
                    send_message(sender, 'habla bien causa! en que producto te podemos ayudar')
                    return 'Hi'

                if 'text' not in message['message']:
                    send_message(sender, 'habla bien causa! en que producto te podemos ayudar')
                    return 'Hi'

                text = message['message']['text']
                text = text.lower()

                flag = db.session.query(Flag).filter(Flag.user_id == sender).first()
                if flag is None:

                    flag = Flag(user_id=sender, flag=FLAG_N)
                    db.session.add(flag)
                    db.session.commit()

                if flag.flag == FLAG_N:

                    parse_list = parse(url_parser_price, text)
                    status = parse_list['status']
                    if status == 'failed':

                        send_fb_cart(sender, '¿Te podemos ayudar en algo de un producto?', 'Precio')
                        # send_fb_cart(sender, 'Si te fuimos útil, sería de gran ayuda que nos compartas tus compras', 'Compartir')

                    else:
                        # Integracion codigo Hector
                        for element in parse_list['mult']:
                            count = element['count']
                            unit = element['presentation']
                            product = element['object']
                            print count
                            print unit
                            print product
                            if unit == 'kg':
                                unit = 'KGM'
                            total_price = get_price_from_human_query(
                                product_name=product,
                                unit_code=unit,
                                quantity=count,
                            )
                            print total_price
                            send_message(sender, 'el producto {} cuesta {} soles'.format(product, total_price))

                        q = (
                            db
                            .session
                            .query(
                                Product.invoice_id.label('invoice_id'),
                                Product.name.label('name'),
                                Product.price.label('price')
                            )
                            .all()
                        )
                        transaction_ids = list(set([x.invoice_id for x in q]))
                        l = []
                        for t_id in transaction_ids:
                            l.append([(x.name, x.price) for x in q if x.invoice_id == t_id])
                        p = get_recommended_product(transactions=l)

                        if p is None:
                            send_fb_cart(sender, 'Si te fuimos útil, sería de gran ayuda que nos compartas tus compras', 'Compartir')
                        else:
                            # print 'estamos de carusel!'
                            send_carrousel(sender, p[0], p[1])

                elif flag.flag == FLAG_P:

                    parse_list = parse(url_parser_price, text)
                    status = parse_list['status']
                    if status == 'failed':
                        send_message(sender, 'habla bien causa! en que producto te podemos ayudar')
                    else:

                        # Integracion codigo Hector
                        for element in parse_list['mult']:
                            count = element['count']
                            presentation = element['presentation']
                            if presentation == 'kg':
                                presentation = 'KGM'
                            product = element['object']
                            total_price = get_price_from_human_query(
                                product_name=product,
                                unit_code=presentation,
                                quantity=count,
                            )
                            send_message(sender, 'el producto {} cuesta {} soles'.format(product, total_price))

                        flag.flag = FLAG_N
                        db.session.commit()

                        q = (
                            db
                            .session
                            .query(
                                Product.invoice_id.label('invoice_id'),
                                Product.name.label('name'),
                                Product.price.label('price')
                            )
                            .all()
                        )
                        transaction_ids = list(set([x.invoice_id for x in q]))
                        l = []
                        for t_id in transaction_ids:
                            l.append([(x.name, x.price) for x in q if x.invoice_id == t_id])
                        # print get_recommended_product(transactions=l)

                        send_fb_cart(sender, 'Si te fuimos útil, sería de gran ayuda que nos compartas tus compras', 'Compartir')

                elif flag.flag == FLAG_A:

                    tmp = db.session.query(UploadInvoiceTmp).filter(UploadInvoiceTmp.user_id == sender).first()
                    if tmp is None:
                        tmp = UploadInvoiceTmp(user_id=sender)
                        db.session.add(tmp)
                        db.session.commit()

                    if tmp.invoice_date is None:

                        parse_list = parse(url_parser_almacenar, text)
                        if parse_list['status'] == 'failed':
                            send_message(sender, MENSAJE_NO_ENTIENDO)
                            send_message(sender, CUAL_FECHA)
                        else:
                            send_message(sender, CUAL_MONTO)
                            year = parse_list['response'][0]
                            month = parse_list['response'][1]
                            day = parse_list['response'][2]
                            full_date = '{}-{}-{}'.format(day, month, year)

                            tmp.invoice_date = full_date
                            db.session.commit()

                    elif tmp.invoice_price is None:

                        parse_list = parse(url_parser_almacenar, text)
                        if parse_list['status'] == 'failed':
                            send_message(sender, MENSAJE_NO_ENTIENDO)
                            send_message(sender, CUAL_MONTO)
                        else:
                            # send_message(sender, CUAL_CODIGO)
                            send_image(sender, CUAL_CODIGO, 'https://i.imgur.com/5Ydcva3.png')
                            # send_image(sender, 'https://i.imageur.com/dK2PxKM.png')
                            # send_image(sender, 'https://i.imgur.com/ZDkbcsb.png')
                            price = parse_list['response'][0]

                            tmp.invoice_price = price
                            db.session.commit()
                    elif tmp.invoice_id is None:

                        parse_list = parse(url_parser_almacenar, text)
                        if parse_list['status'] == 'failed':
                            send_message(sender, MENSAJE_NO_ENTIENDO)
                            # send_message(sender, CUAL_CODIGO)
                            send_image(sender, CUAL_CODIGO, 'https://i.imgur.com/5Ydcva3.png')
                        else:
                            send_message(sender, 'Gracias')

                            inv_id = parse_list['response'][0]
                            inv_date = tmp.invoice_date
                            inv_price = tmp.invoice_price

                            # hacer el request

                            tmp.invoice_date = None
                            tmp.invoice_price = None
                            tmp.invoice_id = None
                            db.session.commit()

                            flag.flag = FLAG_N
                            db.session.commit()


    return "Hi"


def parse(url, text):
    url = url + u"?query={}".format(text)
    response = requests.get(url)
    return json.loads(response.text)


def send_message(sender, text):
    data = {
        'recipient': {
            'id': sender,
        },
        'message': {
            'text': text,
        },
    }
    response = requests.post(url=url_base, headers={'Content-Type': 'application/json'}, data=json.dumps(data))


def send_fb_cart(sender, text, title):
    data = {
        'recipient': {
            'id': sender,
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': text,
                    'buttons': [
                        {
                            "type": "postback",
                            "title": title,
                            "payload": title,
                        }
                    ]
                }
            }
        }
    }
    response = requests.post(url=url_base, headers={'Content-Type': 'application/json'}, data=json.dumps(data))


def send_carrousel(sender, product_name, product_pric):
    data = {
        "message": {
            "attachment": {
                "payload": {
                    "elements": [
                        {
                            "buttons": [
                                {
                                    "payload": "Compartir",
                                    "title": "Compartir",
                                    "type": "postback"
                                }
                            ],
                            "title": "Si te fuimos útil, sería de gran ayuda que nos compartas tus compras"
                        },
                        {
                            "buttons": [
                                {
                                    "payload": "Precio2",
                                    "title": "Precio",
                                    "type": "postback"
                                }
                            ],
                            "title": "Deseas saber el precio del producto {}".format(product_name)
                        }
                    ],
                    "template_type": "generic"
                },
                "type": "template"
            }
        },
        "recipient": {
            "id": sender
        }
    }
    response = requests.post(url=url_base, headers={'Content-Type': 'application/json'}, data=json.dumps(data))


def send_map(sender):
    data = {
        'recipient': {
            'id': sender,
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': [
                        {
                            'title': 'hola mapa',
                            'item_url': 'https://www.google.com.pe/maps/search/-12.0712781,-77.0852257',
                            'image_url': 'https://www.google.com.pe/maps/search/-12.0712781,-77.0852257'
                        }
                    ]
                }
            }
        }
    }
    response = requests.post(url=url_base, headers={'Content-Type': 'application/json'}, data=json.dumps(data))


def send_image(sender, text, url):
    data = {
        'recipient': {
            'id': sender,
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'elements': [
                        {
                            'title': text,
                            'image_url': url
                        }
                    ]
                }
            }
        }
    }
    # print data
    response = requests.post(url=url_base, headers={'Content-Type': 'application/json'}, data=json.dumps(data))
    # print response.text


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

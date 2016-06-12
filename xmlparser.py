#!/usr/bin/python
# coding=utf-8

import xml.etree.ElementTree as ET
from datetime import datetime
import urllib2


ns = {
    'xmlns': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
    'sac': 'urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1',
    'cac': 'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc': 'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'udt': 'urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2',
    'ccts': 'urn:un:unece:uncefact:documentation:2',
    'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2',
    'qdt': 'urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2',
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    # 'schemaLocation': 'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2 ..\xsd\maindoc\UBLPE-Invoice-2.0.xsd',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
}


def get_all_used_namespaces(root):
    import re
    ns_values = set()
    for ele in root.iter():
        m = re.match('\{.*\}', ele.tag)
        ns_value = m.group(0)[1:-1]
        ns_values.add(ns_value)
    print ns_values


def parse_xml(url_path=None, file_path=None):
    if url_path is None and file_path is None:
        return

    f = None
    if url_path is not None:
        f = urllib2.urlopen(url_path)
    elif file_path is not None:
        f = open(file_path)

    if f is None:
        return

    tree = ET.ElementTree(file=f)
    f.close()
    root = tree.getroot()
    return parse_xml_from_root(root)


def parse_xml_from_root(root):

    invoice = None
    if 'PPLDocument' in root.tag:
        tmp = root.find('ClientDocument')
        invoice = tmp[0]
    elif 'Invoice' in root.tag:
        invoice = root

    invoice_id = (
        invoice
        .find('cbc:ID', ns)
        .text
    )
    invoice_date = (
        datetime
        .strptime(
            invoice
            .find('cbc:IssueDate', ns)
            .text,
            '%Y-%m-%d'
        )
        .strftime('%d-%m-%Y')
    )
    invoice_amount = (
        invoice
        .find('cac:LegalMonetaryTotal', ns)
        .find('cbc:PayableAmount', ns)
        .text
    )

    invoice_items = invoice.findall('cac:InvoiceLine', ns)
    products_list = []
    for invoice_item in invoice_items:

        unit_code = (
            invoice_item.find('cbc:InvoicedQuantity', ns)
            .attrib
            .get('unitCode', '')
        )

        retail_prod_id = (
            invoice_item
            .find('cac:Item', ns)
            .find('cac:SellersItemIdentification', ns)
            .find('cbc:ID', ns)
            .text
        )

        price = (
            invoice_item
            .find('cac:PricingReference', ns)
            .find('cac:AlternativeConditionPrice', ns)
            .find('cbc:PriceAmount', ns)
            .text
        )

        description = (
            invoice_item
            .find('cac:Item', ns)
            .find('cbc:Description', ns)
            .text
            .strip()
            .split('@@')
            [1]
        )

        product = {
            'unit_code': unit_code,
            'retail_prod_id': retail_prod_id,
            'price': price,
            'description': description,
        }
        products_list.append(product)

    x = {
        'invoice_id': invoice_id,
        'invoice_date': invoice_date,
        'invoice_amount': invoice_amount,
        'products': products_list,
    }
    return x


# if __name__ == '__main__':
#     url_path = 'http://asp401r.paperless.com.pe/Facturacion/XMLServlet?id=Af0kzJDiiBRtmh3b3YDH3Q(IgU)(IgU)&cl=true'
    # import json
#     file_path = 'tmp.invoice.xml'
#     x = parse_xml(file_path=file_path)
#     print json.dumps(x, indent=4, sort_keys=True)
#     x = parse_xml(url_path=url_path)
#     print json.dumps(x, indent=4, sort_keys=True)
#     x = parse_xml(url_path=url_path)

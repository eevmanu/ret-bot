#!/usr/bin/python
# coding=utf-8


from selenium.webdriver import PhantomJS
from selenium.webdriver.support.ui import Select
import time
from vision import VisionApi


RETAIL_INVOICE_URL = {
    'plazavea': 'http://asp401r.paperless.com.pe/BoletaSPSA/',
    'metro': '',
    'wong': '',
    'tottus': '',
    'vivanda': '',
    'makro': '',
    'minka': '',
}


RETAIL_INVOICE_DOC_TYPES = {
    'plazavea': {
        'b': {
            'name': 'Boleta',
            'value': '03',
        },
        'f': {
            'name': 'Factura',
            'value': '01',
        },
        'nc': {
            'name': 'Nota Credito',
            'value': '07',
        },
        'nd': {
            'name': 'Nota Debito',
            'value': '08',
        },
    },
    'metro': {},
    'wong': {},
    'tottus': {},
    'vivanda': {},
    'makro': {},
    'minka': {},
}


def get_url_files(retail, invoice_doc_type, invoice_id, invoice_date, invoice_amount):
    retail_invoice_url = RETAIL_INVOICE_URL[retail]

    driver = PhantomJS()
    driver.get(retail_invoice_url)

    # 1 Set doc_type 'select'
    try:
        select_doc_type = Select(driver.find_element_by_name('txtTipoDte'))
        value = RETAIL_INVOICE_DOC_TYPES[retail][invoice_doc_type]['value']
        select_doc_type.select_by_value(value)
        # name = RETAIL_INVOICE_DOC_TYPES[retail][invoice_doc_type]['name']
        # select_doc_type.select_by_visible_text(name)
    except Exception:
        print 'ERROR: set doc_type select as Boleta'
        driver.save_screenshot('screen.png')
        return '', ''

    time.sleep(5)

    # 2 Get recaptcha img url
    try:
        recaptcha_img = driver.find_element_by_id('recaptcha_challenge_image')
        recaptcha_img_url = recaptcha_img.get_attribute('src')
    except Exception:
        print 'ERROR: get recaptcha image url'
        driver.save_screenshot('screen.png')
        return '', ''

    # 3 Solve recaptcha
    v = VisionApi()
    recaptcha_value = v.detect_text_from_url(recaptcha_img_url)

    if recaptcha_value is None:
        print 'ERROR: solving recaptcha image'
        driver.save_screenshot('screen.png')
        return '', ''

    # 4 Fill form
    script = u"""
        document.getElementsByName('txtFolio')[0].value = '{invoice_id}';
        document.getElementsByName('txtFechaEmision')[0].value = '{invoice_date}';
        document.getElementsByName('txtMontoTotal')[0].value = '{invoice_amount}';
        document.getElementsByName('recaptcha_response_field')[0].value = '{recaptcha_value}';
    """.format(
        invoice_id=invoice_id,
        invoice_date=invoice_date,
        invoice_amount=invoice_amount,
        recaptcha_value=recaptcha_value,
    )
    driver.execute_script(script)

    # 5 Submit form
    try:
        driver.find_element_by_name('frmDatos').submit()
    except Exception:
        print 'ERROR: submitting form'
        driver.save_screenshot('screen.png')
        return '', ''

    # 6 Get url files
    try:
        xml_a_tag = driver.find_element_by_xpath('//*[@id="Tabla_01"]/tbody/tr[1]/td[2]/p/a[2]')
        pdf_a_tag = driver.find_element_by_xpath('//*[@id="Tabla_01"]/tbody/tr[1]/td[2]/p/a[1]')

        xml_url = xml_a_tag.get_attribute('href')
        pdf_url = pdf_a_tag.get_attribute('href')
    except Exception:
        print 'ERROR: getting url files'
        driver.save_screenshot('screen.png')
        return '', ''

    # 8 Delete driver session
    driver.close()
    driver.quit()

    return xml_url, pdf_url

if __name__ == '__main__':

    xml_url, pdf_url = get_url_files(
        retail='plazavea',
        invoice_doc_type='b',
        # invoice_id='BA55-02381584',
        # invoice_date='25-05-2016',
        # invoice_amount='154.00',
        invoice_id='BA63-03069121',
        invoice_date='25-05-2016',
        invoice_amount='68.27',
    )

    print xml_url, pdf_url

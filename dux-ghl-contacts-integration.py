#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
from datetime import timedelta, datetime
import os
from dotenv import load_dotenv
import requests
import json
import traceback
import logging
from logging.handlers import RotatingFileHandler
import csv
import re
import sys
import platform
import socket


def is_valid_email(email):
    """
    Checks if the email format is valid using regex.
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None


def send_error_email(error_message):
    """
    Send an email when an error occurs using SSL connection
    """
    try:
        logger.info("Attempting to send error notification email")
        smtp_server = os.getenv("SMTP_SERVER")
        smtp_port = int(os.getenv("SMTP_PORT"))
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")
        receiver_email = os.getenv("NOTIFICATION_EMAIL")

        # Create email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email.join(receiver_email)
        message["Subject"] = "Error Integración DUX - Drive"

        # Add error to email body with more details
        body = f"""
        Se ha producido un error durante la ejecución del script DUX:

        Timestamp: {datetime.now()}
        
        Error Details:
        {error_message}
        
        System Information:
        - Python Version: {sys.version}
        - Operating System: {platform.system()} {platform.release()}
        - Hostname: {socket.gethostname()}
        
        Please check the logs for more detailed information.
        Log file location: {os.path.abspath('logs/dux_script.log')}
        """

        message.attach(MIMEText(body, "plain"))

        # Create SMTP session with SSL
        logger.debug(f"Establishing SSL connection to {smtp_server}:{smtp_port}")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.login(sender_email, sender_password)

        # Send email
        server.send_message(message)
        server.quit()
        logger.info("Error notification email sent successfully")

    except Exception as e:
        logger.error(f"Failed to send error email: {str(e)}")
        logger.debug(
            f"SMTP connection details: server={smtp_server}, port={smtp_port}, from={sender_email}, to={receiver_email}")
        # Don't raise the exception here to avoid infinite recursion


def setup_logging():
    """Configure logging to both file and console"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Create logger
    logger = logging.getLogger('DUXScript')
    logger.setLevel(logging.DEBUG)

    # Create formatters
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler (daily rotating log files, keep 7 days)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename='logs/dux_script.log',
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    file_handler.suffix = "%Y-%m-%d.log"  # Add date to the log file name

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = setup_logging()
load_dotenv()

csv_clients_dictionary = {
    "id": 0,
    "fecha_creacion": 1,
    "cliente": 2,
    "categoria_fiscal": 3,
    "tipo_documento": 4,
    "numero_documento": 5,
    "cuit/cuil": 6,
    "cobrador": 7,
    "tipo_cliente": 8,
    "persona_contacto": 9,
    "no_editable": 10,
    "lugar_entrega_por_defecto": 11,
    "tipo_comprobante_por_defecto": 12,
    "lista_precio_por_defecto": 13,
    "habilitado": 14,
    "nombre_de_fantasia": 15,
    "codigo": 16,
    "correo_electronico": 17,
    "vendedor": 18,
    "provincia": 19,
    "localidad": 20,
    "barrio": 21,
    "domicilio": 22,
    "telefono": 23,
    "celular": 24,
    "zona": 25,
    "condicion_pago": 26
}


def main():
    driver = None
    try:
        logger.info("Starting DUX script execution")
        all_clients_list = []

        # Configurar Selenium con Chrome
        logger.debug("Initializing Chrome WebDriver")
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--disable-blink-features=AutomationControlled")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

        # Paso 1: Ir a la página de login
        logger.info("Navigating to DUX login page")
        driver.get("https://erp.duxsoftware.com.ar/")

        # Paso 2: Ingresar credenciales
        logger.debug("Entering login credentials")
        driver.find_element(By.ID, "formLogin:inputUsuario").send_keys(os.getenv("DUX_USERNAME"))
        driver.find_element(By.ID, "formLogin:inputPassword").send_keys(os.getenv("DUX_PASSWORD"), Keys.RETURN)

        logger.debug("Waiting for page load after login")
        time.sleep(5)

        # Paso 3: Aceptar select de sucursal
        logger.debug("Selecting branch office")
        driver.find_element(By.ID, "formInicio:j_idt909").click()
        time.sleep(5)

        # Paso 4: Navegar a pagina de clientes
        logger.info("Navigating to clients page")
        driver.get("https://erp.duxsoftware.com.ar/pages/configuracion/cliente/listaClienteBeta.faces")
        time.sleep(7)

        # Paso 5 y 6: Configurar fecha
        driver.find_element(By.CLASS_NAME, "announcekit-booster-modal-close").click()
        logger.debug("Configuring date filters")
        driver.find_element(By.ID, "formCabecera:j_idt1030_label").click()
        driver.find_element(By.ID, "formCabecera:j_idt1030_3").click()

        time.sleep(10)

        # Paso 7: Escribir fecha y dar enter
        yesterday = datetime.now()
        yesterday_string_dux = datetime.strftime(yesterday, "%d%m%y")
        logger.debug(f"Setting date filter to: {yesterday_string_dux}")
        wait = WebDriverWait(driver, 10)
        input_element = wait.until(EC.presence_of_element_located((By.ID, "formCabecera:j_idt1040_input")))
        input_element.click()
        input_element.send_keys(yesterday_string_dux)
        input_element = wait.until(EC.presence_of_element_located((By.ID, "formCabecera:j_idt1046_input")))
        input_element.click()
        input_element.send_keys(yesterday_string_dux, Keys.RETURN)

        time.sleep(5)

        # Paso 8: Extraer datos de la tabla
        button_next_page_disabled = False
        page_number = 1

        logger.info("Starting data extraction from table")
        while not button_next_page_disabled:
            logger.debug(f"Processing page {page_number}")
            iterate_table(driver, all_clients_list)
            button_next_page = driver.find_element(By.XPATH,
                                                   "/html/body/div[2]/div[4]/div/div[2]/div/form/div/div[5]/a[3]")
            button_next_page_class = button_next_page.get_attribute("class")
            button_next_page_classes = button_next_page_class.split(" ")
            button_next_page_disabled = "ui-state-disabled" in button_next_page_classes

            if not button_next_page_disabled:
                logger.debug(f"Moving to page {page_number + 1}")
                button_next_page.click()
                time.sleep(10)
                page_number += 1
            else:
                logger.info("Reached last page of results")
                button_next_page_disabled = True

        logger.info("Script execution completed successfully")

    except NoRowsFoundException:
        logger.info("Script finished: No rows found to process")
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
    finally:
        if driver:
            logger.debug("Closing Chrome WebDriver")
            driver.quit()


def upsert_contacts():
    try:
        logger.info("Starting contact upsert process")
        location_id = os.getenv("GHL_LOCATION_ID")
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Version': '2021-07-28',
            'Authorization': f'Bearer {os.getenv("GHL_PRIVATE_INTEGRATION_KEY")}'
        }
        url = "https://services.leadconnectorhq.com/contacts/upsert"

        logger.debug("Reading clients.csv file")
        with open("clients.csv", "r") as file:
            csvreader = csv.reader(file)
            total_contacts = 0
            successful_upserts = 0

            for row in csvreader:
                total_contacts += 1
                try:
                    logger.debug(f"Processing contact {total_contacts}: {row[csv_clients_dictionary['cliente']]}")
                    payload = {
                        "locationId": location_id,
                        "firstName": row[csv_clients_dictionary["cliente"]],
                        "phone": row[csv_clients_dictionary["telefono"]] if not row[
                            csv_clients_dictionary["celular"]] else row[
                            csv_clients_dictionary["celular"]],
                        "customFields": [
                            {
                                "key": "id_cliente_dux",
                                "field_value": row[csv_clients_dictionary["id"]]
                            },
                            {
                                "key": "categoria_fiscal_dux",
                                "field_value": row[csv_clients_dictionary["categoria_fiscal"]]
                            },
                            {
                                "key": "tipo_documento_dux",
                                "field_value": row[csv_clients_dictionary["tipo_documento"]]
                            },
                            {
                                "key": "numero_documento_dux",
                                "field_value": row[csv_clients_dictionary["numero_documento"]]
                            },
                            {
                                "key": "cuit_cuil_dux",
                                "field_value": row[csv_clients_dictionary["cuit/cuil"]]
                            },
                            {
                                "key": "tipo_cliente_dux",
                                "field_value": row[csv_clients_dictionary["tipo_cliente"]]
                            },
                            {
                                "key": "provincia_dux",
                                "field_value": row[csv_clients_dictionary["provincia"]]
                            },
                            {
                                "key": "barrio_dux",
                                "field_value": row[csv_clients_dictionary["barrio"]]
                            },
                            {
                                "key": "direccion_facturacion_dux",
                                "field_value": row[csv_clients_dictionary["domicilio"]]
                            },
                            {
                                "key": "codigo_postal_dux",
                                "field_value": row[csv_clients_dictionary["codigo"]]
                            },
                        ]
                    }

                    if is_valid_email(row[csv_clients_dictionary["correo_electronico"]]):
                        payload["email"] = row[csv_clients_dictionary["correo_electronico"]]
                        payload["customFields"].append({
                            "key": "email_facturacion_dux",
                            "value": row[csv_clients_dictionary["correo_electronico"]]
                        })

                    try:
                        response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
                        log_api_request("POST", url, headers, payload, response=response)

                        if response.ok:
                            successful_upserts += 1
                            logger.debug(f"Successfully upserted contact {total_contacts}")
                        else:
                            logger.error(
                                f"Failed to upsert contact {total_contacts}. Status code: {response.status_code}, Response: {response.text}")
                    except Exception as e:
                        log_api_request("POST", url, headers, payload, error=e)
                        logger.error(f"Error processing contact {total_contacts}: {str(e)}")
                        continue

                except Exception as e:
                    logger.error(f"Error processing contact {total_contacts}: {str(e)}")
                    continue

            logger.info(
                f"Contact upsert process completed. Total contacts: {total_contacts}, Successful: {successful_upserts}")

        os.remove('clients.csv')

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred during contact upsert process: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
        raise


def search_invoices():
    try:
        logger.info("Starting invoice search process")
        ids_sucursales = []
        headers_ghl = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Version': '2021-07-28',
            'Authorization': f'Bearer {os.getenv("GHL_PRIVATE_INTEGRATION_KEY")}'
        }
        headers_dux = {
            "accept": "application/json",
            "authorization": os.getenv("DUX_API_KEY")
        }

        logger.debug("Fetching branch offices from DUX API")
        url_sucursales = f'https://erp.duxsoftware.com.ar/WSERP/rest/services/sucursales?idEmpresa={os.getenv("DUX_ID_EMPRESA")}'
        try:
            response_sucursales = requests.request("GET", url_sucursales, headers=headers_dux)
            log_api_request("GET", url_sucursales, headers_dux, response=response_sucursales)

            if not response_sucursales.ok:
                raise Exception(
                    f"Failed to fetch branch offices. Status code: {response_sucursales.status_code}, Response: {response_sucursales.text}")

            for i in response_sucursales.json():
                ids_sucursales.append(i['id'])

            logger.info(f"Found {len(ids_sucursales)} branch offices")
        except Exception as e:
            log_api_request("GET", url_sucursales, headers_dux, error=e)
            raise

        url_facturas = "https://erp.duxsoftware.com.ar/WSERP/rest/services/facturas"
        yesterday = datetime.now() - timedelta(1)
        yesterday_string_dux = datetime.strftime(yesterday, "%Y-%m-%d")
        logger.debug(f"Searching invoices for date: {yesterday_string_dux}")

        total_invoices_processed = 0
        successful_updates = 0

        for index, item in enumerate(ids_sucursales):
            try:
                logger.debug(f"Processing branch office {index + 1}/{len(ids_sucursales)}")
                params = {
                    "fechaDesde": yesterday_string_dux,
                    "fechaHasta": yesterday_string_dux,
                    "idEmpresa": os.getenv("DUX_ID_EMPRESA"),
                    "idSucursal": item,
                }

                time.sleep(5)
                try:
                    response_facturas = requests.request("GET", url_facturas, headers=headers_dux, params=params)
                    log_api_request("GET", url_facturas, headers_dux, params, response=response_facturas)

                    if not response_facturas.ok:
                        logger.error(
                            f"Failed to fetch invoices for branch office {item}. Status code: {response_facturas.status_code}, Response: {response_facturas.text}")
                        continue

                    facturas = response_facturas.json()['results']
                    logger.debug(f"Found {len(facturas)} invoices for branch office {item}")
                except Exception as e:
                    log_api_request("GET", url_facturas, headers_dux, params, error=e)
                    logger.error(f"Error fetching invoices for branch office {item}: {str(e)}")
                    continue

                for j in facturas:
                    total_invoices_processed += 1
                    try:
                        search_contact_result = search_contact_by_id_cliente_dux(j["id_cliente"])
                        if len(search_contact_result['contacts']) > 0:
                            url_update_contact = f"https://services.leadconnectorhq.com/contacts/{search_contact_result['contacts'][0]['id']}"
                            fecha = datetime.strptime(j["fecha_comp"], "%b %d, %Y %I:%M:%S %p")
                            fecha_formateada = fecha.strftime("%Y/%m/%d")
                            logger.debug(
                                f"Updating contact for invoice {j['id']} from branch office {response_sucursales.json()[index]['sucursal']}")

                            payload_update_contact = {
                                "customFields": [
                                    {
                                        "key": "id_factura_dux",
                                        "field_value": j["id"]
                                    },
                                    {
                                        "key": "numero_punto_venta_dux",
                                        "field_value": j["nro_pto_vta"]
                                    },
                                    {
                                        "key": "id_personal_dux",
                                        "field_value": j["id_personal"]
                                    },
                                    {
                                        "key": "id_vendedor_dux",
                                        "field_value": j["id_vendedor"]
                                    },
                                    {
                                        "key": "tipo_comprobante_dux",
                                        "field_value": j["tipo_comp"]
                                    },
                                    {
                                        "key": "numero_comprobante_dux",
                                        "field_value": j["nro_comp"]
                                    },
                                    {
                                        "key": "fecha_comprobante_dux",
                                        "field_value": fecha_formateada
                                    },
                                    {
                                        "key": "monto_sin_iva_dux",
                                        "field_value": j["monto_gravado"]
                                    },
                                    {
                                        "key": "monto_total_dux",
                                        "field_value": j["total"]
                                    },
                                    {
                                        "key": "nombre_sucursal_dux",
                                        "field_value": response_sucursales.json()[index]["sucursal"]
                                    },
                                    {
                                        "key": "tiene_cobro",
                                        "field_value": "SI" if j["detalles_cobro"] else "NO"
                                    },
                                    {
                                        "key": "presupuesto_numero_dux",
                                        "field_value": j["presupuesto"][0]["nro_presupuesto"] if j[
                                            "presupuesto"] else ""
                                    },
                                    {
                                        "key": "presupuesto_estado_dux",
                                        "field_value": j["presupuesto"][0]["estado"] if j["presupuesto"] else ""
                                    }
                                ]
                            }

                            for producto in j["detalles"]:
                                if "COMODATO" in producto["item"]:
                                    payload_update_contact["customFields"].append({
                                        "key": "contrata_comodato_dux",
                                        "value": "SI"
                                    })
                                else:
                                    payload_update_contact["customFields"].append({
                                        "key": "contrata_comodato_dux",
                                        "value": "NO"
                                    })

                            try:
                                response_update_contact = requests.request("PUT", url_update_contact,
                                                                           headers=headers_ghl,
                                                                           data=json.dumps(payload_update_contact))
                                log_api_request("PUT", url_update_contact, headers_ghl, payload_update_contact,
                                                response=response_update_contact)

                                if response_update_contact.ok:
                                    successful_updates += 1
                                    logger.debug(f"Successfully updated contact for invoice {j['id']}")
                                else:
                                    logger.error(
                                        f"Failed to update contact for invoice {j['id']}. Status code: {response_update_contact.status_code}, Response: {response_update_contact.text}")
                            except Exception as e:
                                log_api_request("PUT", url_update_contact, headers_ghl, payload_update_contact, error=e)
                                logger.error(f"Error updating contact for invoice {j['id']}: {str(e)}")
                                continue

                    except Exception as e:
                        logger.error(f"Error processing invoice {j['id']}: {str(e)}")
                        continue

            except Exception as e:
                logger.error(f"Error processing branch office {item}: {str(e)}")
                continue

        logger.info(
            f"Invoice search process completed. Total invoices processed: {total_invoices_processed}, Successful updates: {successful_updates}")

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred during invoice search process: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
        raise


def search_contact_by_id_cliente_dux(id_cliente_dux, phone="", email=""):
    try:
        logger.debug(f"Searching contact by DUX ID: {id_cliente_dux}, Phone: {phone}, Email: {email}")
        url = "https://services.leadconnectorhq.com/contacts/search"
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Version': '2021-07-28',
            'Authorization': f'Bearer {os.getenv("GHL_PRIVATE_INTEGRATION_KEY")}'
        }
        payload = {
            "locationId": os.getenv("GHL_LOCATION_ID"),
            "page": 1,
            "pageLimit": 20,
            "filters": [
                {
                    "group": "OR",
                    "filters": [
                        {
                            "field": "customFields.id_cliente_dux",
                            "operator": "eq",
                            "value": id_cliente_dux
                        },
                        {
                            "field": "email",
                            "operator": "eq",
                            "value": email
                        },
                        {
                            "field": "phone",
                            "operator": "eq",
                            "value": phone
                        }
                    ]
                }
            ],
            "sort": [
                {
                    "field": "dateAdded",
                    "direction": "desc"
                }
            ]
        }

        try:
            response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
            log_api_request("POST", url, headers, payload, response=response)

            if not response.ok:
                logger.error(
                    f"Failed to search contact. Status code: {response.status_code}, Response: {response.text}")
                return {"contacts": []}

            result = response.json()
            logger.debug(f"Found {len(result.get('contacts', []))} contacts matching the search criteria")
            return result
        except Exception as e:
            log_api_request("POST", url, headers, payload, error=e)
            logger.error(f"Error searching contact: {str(e)}")
            return {"contacts": []}

    except Exception as e:
        logger.error(f"Error in search_contact_by_id_cliente_dux: {str(e)}")
        return {"contacts": []}


def iterate_table(driver, all_clients_list):
    try:
        logger.debug("Opening Google Sheet 'Clientes DUX - GHL Cloud Server'")
        logger.debug("Extracting table data")
        rows = driver.find_elements(By.TAG_NAME, "tr")
        rows_processed = 0
        for row in rows:
            cols = [col.text for col in row.find_elements(By.TAG_NAME, "td")]
            if len(cols) == 29:
                new_cols = cols[2:]
                all_clients_list.append(new_cols)
                rows_processed += 1

        logger.info(f"Processed {rows_processed} client rows")

        if rows_processed == 0:
            logger.warning("No rows found to process, stopping execution")
            raise NoRowsFoundException("No rows were found to process in the current page")

        filename = 'clients.csv'
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(all_clients_list)

        upsert_contacts()


    except NoRowsFoundException:
        # Just log the warning and re-raise, without sending email
        logger.warning("No rows found in the current page, stopping execution")
        raise
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred while iterating table: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
        raise


# Add this new custom exception class at the top level of the file, after the imports
class NoRowsFoundException(Exception):
    """Exception raised when no rows are found to process"""
    pass


def search_contacts(location_id, integration_key, id_cliente_dux='', email='', phone=''):
    url = "https://services.leadconnectorhq.com/contacts/search"

    payload = json.dumps({
        "locationId": location_id,
        "page": 1,
        "pageLimit": 20,
        "filters": [
            {
                "group": "OR",
                "filters": [
                    {
                        "field": "customFields.id_cliente_dux",
                        "operator": "eq",
                        "value": id_cliente_dux
                    },
                    {
                        "field": "email",
                        "operator": "eq",
                        "value": email
                    },
                    {
                        "field": "phone",
                        "operator": "eq",
                        "value": phone
                    }
                ]
            }
        ],
        "sort": [
            {
                "field": "dateAdded",
                "direction": "desc"
            }
        ]
    })
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {integration_key}',
        'Content-Type': 'application/json',
        'Version': '2021-07-28'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(json.dumps(response.json(), indent=2))


def log_api_request(method, url, headers, payload=None, response=None, error=None):
    """
    Log API request and response details
    """
    try:
        # Mask sensitive information in headers
        masked_headers = headers.copy()
        if 'Authorization' in masked_headers:
            masked_headers['Authorization'] = 'Bearer [MASKED]'

        # Log request details
        logger.debug(f"API Request - Method: {method}, URL: {url}")
        logger.debug(f"API Request - Headers: {json.dumps(masked_headers, indent=2)}")
        if payload:
            logger.debug(f"API Request - Payload: {json.dumps(payload, indent=2)}")

        # Log response or error
        if response:
            logger.debug(f"API Response - Status Code: {response.status_code}")
            logger.debug(f"API Response - Body: {response.text}")
        elif error:
            logger.error(f"API Error: {str(error)}")

    except Exception as e:
        logger.error(f"Error logging API request: {str(e)}")


if __name__ == "__main__":
    main()

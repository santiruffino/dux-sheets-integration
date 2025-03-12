#!/usr/bin/env python3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import pygsheets
import os
from dotenv import load_dotenv
from datetime import timedelta, datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import traceback
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
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
    
    # File handler (rotating log files, max 5MB each, keep 5 backup files)
    file_handler = RotatingFileHandler('logs/dux_script.log', maxBytes=5*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

load_dotenv()

def send_error_email(error_message):
    """
    Enviar un email cuando ocurre un error
    """
    logger.info("Attempting to send error notification email")
    sender_email = os.getenv("SMTP_EMAIL")
    sender_password = os.getenv("SMTP_PASSWORD")
    receiver_email = os.getenv("NOTIFICATION_EMAIL")
    
    # Crear email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Error en la ejecución del script DUX"
    
    # Agregar error al body del email
    body = f"""
    Se ha producido un error durante la ejecución del script DUX:
    
    Timestamp: {datetime.now()}
    Error: {error_message}
    """
    
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Crear sesion SMTP
        logger.debug("Establishing SMTP connection")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Enviar email
        server.send_message(message)
        server.quit()
        logger.info("Error notification email sent successfully")
    except Exception as e:
        logger.error(f"Failed to send error email: {str(e)}")

def main():
    driver = None
    try:
        logger.info("Starting DUX script execution")
        all_clients_list = []
        logger.debug("Authorizing with pygsheets")
        gc = pygsheets.authorize(service_file="dux-integration-api-5f2a21be17a1.json")
        
        # Configurar Selenium con Chrome
        logger.debug("Initializing Chrome WebDriver")
        driver = webdriver.Chrome()

        # Paso 1: Ir a la página de login
        logger.info("Navigating to DUX login page")
        driver.get("https://erp.duxsoftware.com.ar/")

        # Paso 2: Ingresar credenciales
        logger.debug("Entering login credentials")
        driver.find_element(By.ID, "formLogin:inputUsuario").send_keys(os.getenv("DUX_USERNAME"))
        driver.find_element(By.ID, "formLogin:j_idt16").send_keys(os.getenv("DUX_PASSWORD"), Keys.RETURN)

        logger.debug("Waiting for page load after login")
        time.sleep(5)

        # Paso 3: Aceptar select de sucursal
        logger.debug("Selecting branch office")
        driver.find_element(By.ID, "formInicio:j_idt882").click()
        time.sleep(5)

        # Paso 4: Navegar a pagina de clientes
        logger.info("Navigating to clients page")
        driver.get("https://erp.duxsoftware.com.ar/pages/configuracion/cliente/listaClienteBeta.faces")

        # Paso 5 y 6: Configurar fecha
        logger.debug("Configuring date filters")
        driver.find_element(By.ID, "formCabecera:j_idt1003_label").click()
        driver.find_element(By.ID, "formCabecera:j_idt1003_3").click()

        time.sleep(10)

        # Paso 7: Escribir fecha y dar enter
        yesterday = datetime.now() - timedelta(1)
        yesterdayStringDux = datetime.strftime(yesterday, "%d%m%y")
        logger.debug(f"Setting date filter to: {yesterdayStringDux}")
        driver.find_element(By.ID, "formCabecera:j_idt1013_input").send_keys(yesterdayStringDux, Keys.RETURN)

        time.sleep(7)

        # Paso 8: Extraer datos de la tabla
        button_next_page_disabled = False
        page_number = 1
        
        logger.info("Starting data extraction from table")
        while not button_next_page_disabled:
            logger.debug(f"Processing page {page_number}")
            iterate_table(driver, gc, all_clients_list)
            button_next_page = driver.find_element(By.XPATH, "/html/body/div[2]/div[4]/div/div[2]/div/form/div/div[5]/a[3]")
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

    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
    finally:
        if driver:
            logger.debug("Closing Chrome WebDriver")
            driver.quit()

def iterate_table(driver, gc, all_clients_list):
    try:
        logger.debug("Opening Google Sheet 'Clientes DUX'")
        sh = gc.open('Clientes DUX')
        wks = sh[0]
        
        logger.debug("Extracting table data")
        rows = driver.find_elements(By.TAG_NAME, "tr")
        rows_processed = 0
        for row in rows:
            cols = [col.text for col in row.find_elements(By.TAG_NAME, "td")]
            if len(cols) == 29:
                all_clients_list.append(cols)
                rows_processed += 1
        
        logger.info(f"Processed {rows_processed} client rows")
        logger.debug("Updating Google Sheet with new data")
        wks.update_values('A2', all_clients_list)
        logger.debug("Google Sheet update completed")
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"An error occurred while iterating table: {str(e)}")
        logger.error(f"Stack trace: {error_details}")
        send_error_email(error_details)
        raise

if __name__ == "__main__":
    main()

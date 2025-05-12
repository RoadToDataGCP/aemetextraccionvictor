from dotenv import load_dotenv
from urllib.parse import urlencode
import os
import requests
import pandas as pd

# Cargar variables del archivo .env
load_dotenv()

# Obtener la API key desde las variables de entorno
api_key = os.getenv("API_KEY")

# Validación por si no se encuentra la clave
if not api_key:
    raise ValueError("No se encontró la variable de entorno 'API_KEY'")

# Encabezado con la clave
header = {
    'api_key': api_key
}

def construir_url(url_base, **params):
    if params:
        return f"{url_base}?{urlencode(params)}"
    return url_base

def realizar_peticion(url_completa, headers=header):

    def obtener_datos(url_datos, headers=header):
        try:
            # Realizar la segunda petición GET a la URL de los datos
            response = requests.get(url_datos, headers=headers)
            response.raise_for_status()  # Lanza error si la respuesta fue 4xx o 5xx
            
            # Intentar obtener los datos reales
            try:
                return response.json()  # Devuelve los datos en formato JSON
            except ValueError:
                return response.text  # Si no es JSON, devolver como texto

        except requests.exceptions.RequestException as e:
            print(f"Error al obtener los datos: {e}")
            return None

    try:
        # Realizamos la petición GET
        response = requests.get(url_completa, headers=headers)
        response.raise_for_status()  # Lanza error si la respuesta fue 4xx o 5xx
        
        # Intentamos obtener la respuesta en formato JSON
        try:
            respuesta_json = response.json()
        except ValueError:
            # Si no es JSON, devolver como texto
            return response.text

        # Verificar el estado de la respuesta
        estado = respuesta_json.get('estado')
        descripcion = respuesta_json.get('descripcion', 'Descripción no disponible')

        if estado == 200:
            # Si el estado es 200, devolver los datos
            return obtener_datos(respuesta_json['datos'])
        else:
            # Si el estado no es 200, mostrar el error con el estado y la descripción
            print(f"Error: Estado {estado}, Descripción: {descripcion}")
            return None

    except requests.exceptions.RequestException as e:
        # Capturar cualquier excepción que ocurra durante la solicitud
        print(f"Error en la petición: {e}")
        return None


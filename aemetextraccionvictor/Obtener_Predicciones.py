import json
import pandas as pd
from datetime import datetime
from Conectar_API import construir_url, realizar_peticion

def iniciar():
    # Lista de códigos INE de 10 municipios
    municipios = ["28079", "08019", "41091", "03065", "29067", "15078", "48020", "46017", "07040", "11027"]

    # URL base del endpoint
    url_base = "https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria"

    # Día actual
    hoy = datetime.today().date()
    ts_now = datetime.now().isoformat()

    # Acumulador general
    filas = []

    # Función auxiliar para extraer por periodo
    def extraer_valor(lista, campo, periodo):
        for item in lista:
            if item.get("periodo") == periodo:
                return item.get(campo)
        return None

    # Iterar sobre municipios
    for codigo_municipio in municipios:
        print(f"📡 Procesando municipio: {codigo_municipio}")

        url = construir_url(f"{url_base}/{codigo_municipio}")
        datos = realizar_peticion(url)

        if not datos:
            print(f"⚠️ No se pudieron obtener datos para municipio {codigo_municipio}")
            continue

        if isinstance(datos, list):
            datos = datos[0]

        municipio = datos.get("nombre")
        provincia = datos.get("provincia")

        for dia in datos["prediccion"]["dia"]:
            fecha_str = dia["fecha"]
            fecha_dt = datetime.fromisoformat(fecha_str).date()

            if fecha_dt != hoy:
                continue

            # Obtener todos los periodos existentes
            periodos = set()
            for campo in ["probPrecipitacion", "estadoCielo", "viento", "rachaMax", "cotaNieveProv"]:
                periodos.update(x.get("periodo", "00-24") for x in dia.get(campo, []))

            if not periodos:
                periodos = {"00-24"}

            for periodo in periodos:
                fila = {
                    "fecha": fecha_str,
                    "periodo": periodo,
                    "codigo_municipio": codigo_municipio,
                    "provincia": provincia,
                    "municipio": municipio,
                    "temp_max": dia.get("temperatura", {}).get("maxima"),
                    "temp_min": dia.get("temperatura", {}).get("minima"),
                    "humedad_max": dia.get("humedadRelativa", {}).get("maxima"),
                    "humedad_min": dia.get("humedadRelativa", {}).get("minima"),
                    "sens_termica_max": dia.get("sensTermica", {}).get("maxima"),
                    "sens_termica_min": dia.get("sensTermica", {}).get("minima"),
                    "uv_max": dia.get("uvMax"),
                    "ts_insert": ts_now,
                    "ts_update": ts_now,
                    "precipitacion": extraer_valor(dia.get("probPrecipitacion", []), "value", periodo),
                    "estado_cielo": extraer_valor(dia.get("estadoCielo", []), "descripcion", periodo),
                    "viento_dir": extraer_valor(dia.get("viento", []), "direccion", periodo),
                    "viento_vel": extraer_valor(dia.get("viento", []), "velocidad", periodo),
                    "racha_max": extraer_valor(dia.get("rachaMax", []), "value", periodo),
                    "cota_nieve": extraer_valor(dia.get("cotaNieveProv", []), "value", periodo)
                }
                filas.append(fila)

    # Guardar CSV
    if filas:
        df = pd.DataFrame(filas)
        df.to_csv("aemetextraccionvictor/prediccion_hoy.csv", sep=";", index=False, encoding="utf-8-sig")
        print("✅ Archivo 'prediccion_hoy.csv' generado correctamente.")

        # Guardar JSON
        with open("aemetextraccionvictor/prediccion_hoy.json", "w", encoding="utf-8") as f:
            json.dump(filas, f, ensure_ascii=False, indent=2)
        print("✅ Archivo 'prediccion_hoy.json' generado correctamente.")
    else:
        print("⚠️ No se obtuvieron datos para el día actual en ningún municipio.")

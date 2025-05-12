from Obtener_Predicciones import iniciar
from google.cloud import storage
import datetime as dt


def subirabucket(archivo, nombrecarpeta):
        try:
            fechahoy = dt.datetime.now().strftime("%Y-%m-%d")
            destination_blob_name = f"{nombrecarpeta}/{fechahoy}/{archivo.split('/')[-1]}"
    
            client = storage.Client()
            bucket = client.bucket('aemetextraccionvictor')
            blob = bucket.blob(destination_blob_name)
            blob.upload_from_filename(archivo)
    
            print(f"Archivo subido a gs://{'aemetextraccionvictor'}/{destination_blob_name}")
            
 
        except Exception as e:
            print(f"Error al subir el csv al bucket{e}")
            

def main():
    iniciar()
    subirabucket('prediccion_hoy.csv', 'output')
 

if __name__ == "__main__":
    print('Holaa')
    main()
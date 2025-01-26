# app/utils.py

import requests  # Asegúrate de tener importado requests
from datetime import datetime
from .models import Gasolinera, Historico
from .schemas import GasolineraCreate, HistoricoCreate
from sqlalchemy.orm import Session
from .crud import create_gasolinera, create_historico
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data_from_ministerio():
    ministerio_url = "https://sedeaplicaciones.minetur.gob.es/ServiciosRESTCarburantes/PreciosCarburantes/EstacionesTerrestres/"
    logger.info(f"Haciendo solicitud a la API del Ministerio: {ministerio_url}")
    response = requests.get(ministerio_url)
    logger.info(f"Respuesta recibida con status code: {response.status_code}")
    if response.status_code == 200:
        try:
            data_json = response.json()
            logger.info("Datos parseados de JSON a diccionario.")
            # Imprimir las claves principales del JSON
            logger.info(f"Estructura de las claves principales del JSON: {list(data_json.keys())}")
            # Imprimir una gasolinera de ejemplo
            if 'ListaEESSPrecio' in data_json and len(data_json['ListaEESSPrecio']) > 0:
                logger.info(f"Ejemplo de una gasolinera: {data_json['ListaEESSPrecio'][0]}")
            return data_json
        except ValueError as e:
            logger.error(f"Error al parsear JSON: {e}")
            raise Exception("Error al parsear JSON de la respuesta del Ministerio")
    else:
        logger.error(f"Error al obtener datos del Ministerio: {response.status_code}")
        raise Exception("Error al obtener datos del Ministerio")

def convert_to_float(value):
    try:
        return float(value.replace(',', '.')) if value else None
    except (AttributeError, ValueError) as e:
        logger.warning(f"Error al convertir valor a float: {value} - {e}")
        return None

def parse_and_store_data(db: Session, batch_size: int = 1000):
    logger.info("Iniciando proceso de recolección y almacenamiento de gasolineras.")
    data = fetch_data_from_ministerio()
    try:
        lista_gasolineras = data['ListaEESSPrecio']  # Ajusta esta clave según la estructura JSON real
        logger.info(f"Total de gasolineras a procesar: {len(lista_gasolineras)}")
    except KeyError as e:
        logger.error(f"Clave faltante en la respuesta: {e}")
        raise Exception("Formato inesperado de la respuesta del Ministerio")

    total = len(lista_gasolineras)
    logger.info(f"Total de gasolineras a procesar: {total}")

    for i in range(0, total, batch_size):
        batch = lista_gasolineras[i:i+batch_size]
        logger.info(f"Procesando lote {i//batch_size + 1} con {len(batch)} gasolineras.")
        for gasolinera_data in batch:
            ideess = gasolinera_data.get('IDEESS', 'N/A')
            logger.info(f"Procesando gasolinera: IDEESS={ideess}")
            try:
                # Usar convert_to_float para longitud y latitud
                longitud = convert_to_float(gasolinera_data.get("Longitud (WGS84)"))
                latitud = convert_to_float(gasolinera_data.get("Latitud"))
                
                # Verificar que longitud y latitud no sean None
                if longitud is None or latitud is None:
                    logger.warning(f"Longitud o latitud inválida para gasolinera {ideess}. Saltando.")
                    continue

                gasolinera = GasolineraCreate(
                    IDEESS=gasolinera_data["IDEESS"],
                    rotulo=gasolinera_data["Rótulo"],
                    direccion=gasolinera_data["Dirección"],
                    localidad=gasolinera_data["Localidad"],
                    provincia=gasolinera_data["Provincia"],
                    longitud=longitud,
                    latitud=latitud
                )
                logger.info(f"Gasolinera creada: {gasolinera.IDEESS}")
            except (KeyError, ValueError) as e:
                logger.warning(f"Error al procesar gasolinera {ideess}: {e}")
                continue

            existing_gasolinera = db.query(Gasolinera).filter(Gasolinera.IDEESS == gasolinera.IDEESS).first()
            if not existing_gasolinera:
                create_gasolinera(db, gasolinera)
                logger.info(f"Gasolinera {gasolinera.IDEESS} añadida a la base de datos.")
            else:
                logger.info(f"Gasolinera {gasolinera.IDEESS} ya existe en la base de datos.")

            # Procesar histórico de precios
            historico = HistoricoCreate(
                id=f"{gasolinera.IDEESS}-{datetime.today().strftime('%Y%m%d')}",
                gasolinera_id=gasolinera.IDEESS,
                fecha=datetime.today().date(),
                precioGasolina95=convert_to_float(gasolinera_data.get("Precio Gasolina 95 E5")),
                precioGasolina98=convert_to_float(gasolinera_data.get("Precio Gasolina 98 E5")),
                precioGasoleoA=convert_to_float(gasolinera_data.get("Precio Gasoleo A")),
                precioGasoleoPremium=convert_to_float(gasolinera_data.get("Precio Gasoleo Premium")),
                precioGLP=convert_to_float(gasolinera_data.get("Precio GLP")),
                precioGNC=convert_to_float(gasolinera_data.get("Precio Gas Natural Comprimido")),
                precioGNL=convert_to_float(gasolinera_data.get("Precio Gas Natural Licuado")),
                precioHidrogeno=convert_to_float(gasolinera_data.get("Precio Hidrogeno")),
                precioBioetanol=convert_to_float(gasolinera_data.get("Precio Bioetanol")),
                precioBiodiesel=convert_to_float(gasolinera_data.get("Precio Biodiesel")),
                precioEsterMetilico=convert_to_float(gasolinera_data.get("Precio Éster metílico"))
            )
            logger.info(f"Historico creado para gasolinera {historico.gasolinera_id} en fecha {historico.fecha}")

            existing_historico = db.query(Historico).filter(Historico.id == historico.id).first()
            if not existing_historico:
                create_historico(db, historico)
                logger.info(f"Histórico {historico.id} añadido a la base de datos.")
            else:
                logger.info(f"Histórico {historico.id} ya existe en la base de datos.")

        db.commit()
        logger.info(f"Lote {i//batch_size + 1} procesado y commit realizado.")

    logger.info("Proceso de recolección y almacenamiento completado.")
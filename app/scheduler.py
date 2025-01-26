from apscheduler.schedulers.background import BackgroundScheduler
from .database import SessionLocal
from .utils import parse_and_store_data

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(store_data_job, 'cron', hour=0, minute=10)  # Ejecuta todos los días a las 00:10
    scheduler.start()

def store_data_job():
    db = SessionLocal()
    try:
        parse_and_store_data(db)
    except Exception as e:
        print(f"Error en la tarea programada: {e}")
    finally:
        db.close()
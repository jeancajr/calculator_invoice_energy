from fastapi import FastAPI, HTTPException
import psycopg2
from pydantic import BaseModel
from datetime import date

# Se Crea la aplicación de FastAPI
app = FastAPI()

# Se Conecta a PostgreSQL
# Nombre de la base de datos :  energybd
# usuario : postgress
# contraseña 123456

## en http://127.0.0.1:8000/docs se prueba FastAPI

conn = psycopg2.connect(
    host="localhost",
    database="energybd",
    user="postgres",
    password="123456"
)

# Modelos de datos
class InvoiceRequest(BaseModel):
    client_id: int
    year: int
    month: int

# Se importa desde calculos_factura
from calculos_factura import calcular_factura, calcular_ea, calcular_ec, calcular_ee1_ee2


# Implementación de los Endpoints
# Ruta raíz
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Facturación Energética ll"}

# POST /calculate-invoice
@app.post("/calculate-invoice")
async def calculate_invoice(invoice_request: InvoiceRequest):
    try:
        # Se desglosa el request
        client_id = invoice_request.client_id
        year = invoice_request.year
        month = invoice_request.month
        
        # Llama a las funciones de cálculo
        ea, ec, ee1, ee2 = calcular_factura(client_id, conn)
        
        return {
            "client_id": client_id,
            "year": year,
            "month": month,
            "ea": ea,
            "ec": ec,
            "ee1": ee1,
            "ee2": ee2
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al calcular la factura: {str(e)}")


# GET /client-statistics/{client_id}
@app.get("/client-statistics/{client_id}")
async def client_statistics(client_id: int):
    try:
        with conn.cursor() as cur:
            # Obtener estadísticas de consumo e inyección
            query = """
            SELECT SUM(c.value) AS total_consumo, SUM(i.value) AS total_inyeccion
            FROM consumption c
            JOIN injection i ON c.id_record = i.id_record
            JOIN records r ON c.id_record = r.id_record
            WHERE r.id_service = %s
            """
            cur.execute(query, (client_id,))
            result = cur.fetchone()
            
            if result:
                total_consumo, total_inyeccion = result
                return {
                    "client_id": client_id,
                    "total_consumo": total_consumo,
                    "total_inyeccion": total_inyeccion
                }
            else:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en estadísticas: {str(e)}")


# GET /system-load
@app.get("/system-load")
async def system_load():
    try:
        with conn.cursor() as cur:
            # Se obtiene la carga del sistema por hora usando record_timestamp de la tabla records
            query = """
            SELECT EXTRACT(HOUR FROM r.record_timestamp) AS hour, SUM(c.value) AS total_consumo
            FROM consumption c
            JOIN records r ON c.id_record = r.id_record
            GROUP BY hour
            ORDER BY hour;
            """
            cur.execute(query)
            result = cur.fetchall()
            
            # Se formatean los resultados
            system_load = [{"hour": int(row[0]), "total_consumo": row[1]} for row in result]
            return system_load
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en la carga del sistema: {str(e)}")


# Endpoints para cálculos independientes

@app.get("/calculate-ea/{client_id}")
async def calculate_ea_endpoint(client_id: int):
    try:
        ea = calcular_ea(client_id, conn)
        return {"client_id": client_id, "ea": ea}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al calcular EA: {str(e)}")


@app.get("/calculate-ec/{client_id}")
async def calculate_ec_endpoint(client_id: int):
    try:
        ec = calcular_ec(client_id, conn)
        return {"client_id": client_id, "ec": ec}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al calcular EC: {str(e)}")


@app.get("/calculate-ee1-ee2/{client_id}")
async def calculate_ee1_ee2_endpoint(client_id: int):
    try:
        ee1, ee2 = calcular_ee1_ee2(client_id, conn)
        return {"client_id": client_id, "ee1": ee1, "ee2": ee2}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al calcular EE1 y EE2: {str(e)}")
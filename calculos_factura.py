import psycopg2

# Configuración de conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="energybd",
    user="postgres",
    password="123456"
)

# Función para calcular Energía Activa (EA)
def calcular_ea(id_service, conn):
    try:
        with conn.cursor() as cur:
            query = """
            SELECT SUM(c.value), t.cu 
            FROM consumption c
            JOIN records r ON c.id_record = r.id_record
            JOIN services s ON r.id_service = s.id_service
            JOIN tariffs t ON s.id_market = t.id_market
            WHERE r.id_service = %s AND (s.voltage_level IN (2, 3) OR s.cdi = t.cdi)
            GROUP BY t.cu;
            """
            cur.execute(query, (id_service,))
            result = cur.fetchone()
            conn.commit()  # Confirmar la transacción exitosa
            print(f"result: {query }")
            if result: 
                consumo_total, tarifa_cu = result
                energia_activa = consumo_total * tarifa_cu
                print(f"Aqui entro")
                print(f"consumo_total: {consumo_total}")
                print(f"Tarida_cu: {tarifa_cu}")
                return energia_activa
            return 0
        
    except Exception as e:
        conn.rollback()  # Deshacer cambios si hay error
        raise e
    
# calcular_ea(2256, conn)

# Función para calcular Comercialización de Excedentes de Energía (EC)
def calcular_ec(id_service, conn):
    with conn.cursor() as cur:
        query = """
        SELECT SUM(i.value), t.c 
        FROM injection i
        JOIN records r ON i.id_record = r.id_record
        JOIN services s ON r.id_service = s.id_service
        JOIN tariffs t ON s.id_market = t.id_market
        WHERE r.id_service = %s AND (s.voltage_level IN (2, 3) OR s.cdi = t.cdi)
        GROUP BY t.c;
        """
        cur.execute(query, (id_service,))
        result = cur.fetchone()
        if result:
            inyeccion_total, tarifa_c = result
            comercializacion_excedentes = inyeccion_total * tarifa_c
            return comercializacion_excedentes
        return 0

# Función para calcular Excedentes de Energía Tipo 1 (EE1) y Tipo 2 (EE2)
def calcular_ee1_ee2(id_service, conn):
    with conn.cursor() as cur:
        query = """
        SELECT SUM(c.value), SUM(i.value), t.cu 
        FROM consumption c
        JOIN records r_c ON c.id_record = r_c.id_record
        JOIN injection i ON i.id_record = r_c.id_record
        JOIN records r_i ON i.id_record = r_i.id_record
        JOIN services s ON r_i.id_service = s.id_service
        JOIN tariffs t ON s.id_market = t.id_market
        WHERE r_c.id_service = %s AND (s.voltage_level IN (2, 3) OR s.cdi = t.cdi)
        GROUP BY t.cu;
        """
        cur.execute(query, (id_service,))
        result = cur.fetchone()
        
        if result:
            consumo_total, inyeccion_total, tarifa_cu_neg = result
            
            # Calcular EE1
            if inyeccion_total <= consumo_total:
                ee1 = inyeccion_total * tarifa_cu_neg
            else:
                ee1 = consumo_total * tarifa_cu_neg
            
            # Calcular EE2
            ee2 = 0
            if inyeccion_total > consumo_total:
                exceso = inyeccion_total - consumo_total
                query_horas = """
                SELECT value FROM xm_data_hourly_per_agent
                WHERE record_timestamp >= (SELECT MIN(record_timestamp) FROM records WHERE id_service = %s)
                ORDER BY record_timestamp
                """
                cur.execute(query_horas, (id_service,))
                tarifas_horarias = cur.fetchall()

                # Convertir exceso a entero
                for i in range(min(int(exceso), len(tarifas_horarias))):  # Convertimos exceso a entero
                    ee2 += tarifas_horarias[i][0]  # Sumar las tarifas por hora en función del exceso
            
            return ee1, ee2
        
        return 0, 0

def calcular_factura(id_service, conn):
    ea = calcular_ea(id_service, conn)
    ec = calcular_ec(id_service, conn)
    ee1, ee2 = calcular_ee1_ee2(id_service, conn)
    
    print(f"Energía Activa (EA): {ea}")
    print(f"Comercialización de Excedentes (EC): {ec}")
    print(f"Excedentes de Energía tipo 1 (EE1): {ee1}")
    print(f"Excedentes de Energía tipo 2 (EE2): {ee2}")
    
    return ea, ec, ee1, ee2

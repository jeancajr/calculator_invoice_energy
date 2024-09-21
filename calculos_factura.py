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
    with conn.cursor() as cur:
        query = """
        SELECT SUM(c.value), t.cu 
        FROM consumption c
        JOIN records r ON c.id_record = r.id_record
        JOIN services s ON r.id_service = s.id_service
        JOIN tariffs t ON s.id_market = t.id_market AND s.cdi = t.cdi AND s.voltage_level = t.voltage_level
        WHERE r.id_service = %s
        GROUP BY t.cu;
        """
        cur.execute(query, (id_service,))
        result = cur.fetchone()
        if result:
            consumo_total, tarifa_cu = result
            energia_activa = consumo_total * tarifa_cu
            return energia_activa
        return 0

# Función para calcular Comercialización de Excedentes de Energía (EC)
def calcular_ec(id_service, conn):
    with conn.cursor() as cur:
        query = """
        SELECT SUM(i.value), t.c 
        FROM injection i
        JOIN records r ON i.id_record = r.id_record
        JOIN services s ON r.id_service = s.id_service
        JOIN tariffs t ON s.id_market = t.id_market AND s.cdi = t.cdi AND s.voltage_level = t.voltage_level
        WHERE r.id_service = %s
        GROUP BY t.c;
        """
        cur.execute(query, (id_service,))
        result = cur.fetchone()
        if result:
            inyeccion_total, tarifa_c = result
            comercializacion_excedentes = inyeccion_total * tarifa_c
            return comercializacion_excedentes
        return 0

# # Función para calcular Excedentes de Energía Tipo 1 (EE1) y Tipo 2 (EE2)
def calcular_ee1_ee2(id_service, conn):
    with conn.cursor() as cur:
        # Consulta para obtener los valores de consumo, inyección y tarifa CU
        query = """
        SELECT SUM(c.value), SUM(i.value), t.cu 
        FROM consumption c
        JOIN records r_c ON c.id_record = r_c.id_record
        JOIN injection i ON i.id_record = r_c.id_record
        JOIN records r_i ON i.id_record = r_i.id_record
        JOIN services s ON r_i.id_service = s.id_service
        JOIN tariffs t ON s.id_market = t.id_market AND s.cdi = t.cdi AND s.voltage_level = t.voltage_level
        WHERE r_c.id_service = %s
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
                WHERE id_service = %s
                ORDER BY hora
                """
                cur.execute(query_horas, (id_service,))
                tarifas_horarias = cur.fetchall()

                for i in range(min(exceso, len(tarifas_horarias))):
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
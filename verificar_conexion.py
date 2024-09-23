
import psycopg2
# Archivo utilizado para verificar la conexion a la base de datos
# Nombre de la base de datos :  energybd
# usuario : postgress
# contraseña 123456
try:
    conn = psycopg2.connect(
        host="localhost",  
        database="energybd",  
        user="postgres", 
        password="123456" 
    )
    print("Conexión exitosa a la base de datos.")
    
    # Se Verifica el estado de la conexión
    cur = conn.cursor()
    cur.execute("SELECT version();")  # Se Consulta la versión de PostgreSQL
    db_version = cur.fetchone()
    print(f"Versión de la base de datos: {db_version}")
    
    # Se cierra la conexión
    cur.close()
    conn.close()

except Exception as error:
    print(f"Error al conectar a la base de datos: {error}")
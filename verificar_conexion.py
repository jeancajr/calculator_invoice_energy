
import psycopg2
try:
    conn = psycopg2.connect(
        host="localhost",  # Cambia por la IP o dominio del servidor de Pagemind 4
        database="energybd",  # Cambia por el nombre de tu base de datos
        user="postgres",  # Cambia por tu usuario de PostgreSQL
        password="123456"  # Cambia por la contraseña correspondiente
    )
    print("Conexión exitosa a la base de datos.")
    
    # Verificar el estado de la conexión
    cur = conn.cursor()
    cur.execute("SELECT version();")  # Consulta la versión de PostgreSQL
    db_version = cur.fetchone()
    print(f"Versión de la base de datos: {db_version}")
    
    # Cierra la conexión
    cur.close()
    conn.close()

except Exception as error:
    print(f"Error al conectar a la base de datos: {error}")
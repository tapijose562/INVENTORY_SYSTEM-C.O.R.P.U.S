import sqlite3

conn = sqlite3.connect('inventory.db')
cursor = conn.cursor()

# Listar tablas
cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
tables = cursor.fetchall()
print('Tablas en la base de datos:')
for table in tables:
    print(f'- {table[0]}')

# Mostrar estructura de products
print('\nEstructura de la tabla products:')
cursor.execute('PRAGMA table_info(products)')
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# Mostrar estructura de product_images
print('\nEstructura de la tabla product_images:')
cursor.execute('PRAGMA table_info(product_images)')
columns = cursor.fetchall()
for col in columns:
    print(f'  {col[1]} ({col[2]})')

# Mostrar algunos datos de ejemplo
print('\nPrimeros 3 productos:')
cursor.execute('SELECT id, name, brand, colors FROM products LIMIT 3')
products = cursor.fetchall()
for prod in products:
    print(f'  ID: {prod[0]}, Nombre: {prod[1]}, Marca: {prod[2]}, Colores: {prod[3]}')

print('\nPrimeras 3 imágenes de productos:')
cursor.execute('SELECT id, product_id, detected_brand, detected_color FROM product_images LIMIT 3')
images = cursor.fetchall()
for img in images:
    print(f'  ID: {img[0]}, Producto: {img[1]}, Marca detectada: {img[2]}, Color detectado: {img[3]}')

conn.close()
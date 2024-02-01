from pydantic import BaseModel, FilePath, Field, EmailStr, field_validator, ValidationError
from pymongo import MongoClient
from datetime import datetime
import requests
# Realizar una copia de seguridad de la base de datos con mongodump
'''
import subprocess

backup_command = [
    'mongodump',
    '--host', 'mongo',
    '--port', '27017',
    '--db', 'tienda',
    '--out', './copia_seguridad'
]

subprocess.run(backup_command)
'''
# Definir modelos Pydantic para la base de datos
class Nota(BaseModel):
    puntuación: float = Field(ge=0.0, lt=5.0)
    cuenta: int = Field(ge=1)

class Producto(BaseModel):
    nombre: str
    precio: float
    descripción: str
    categoría: str
    imágen: str | None
    rating: Nota

    #COMPROBACIÓN DE MAYÚSCULA 
    @field_validator('nombre')
    @classmethod
    def nombre_debe_empezar_con_mayuscula(cls, v: str) -> str:
        if not v[0].isupper():
            raise ValueError('debe empezar con una letra mayúscula')
        return v

class Compra(BaseModel):
    usuario: EmailStr
    fecha: datetime
    productos: list



# Obtener datos iniciales de la API para los productos v
api_url = 'https://fakestoreapi.com/products'
productos_api = requests.get(api_url).json()

# Obtener datos iniciales de la API para los productos v
api_url = 'https://fakestoreapi.com/products'
productos_api = requests.get(api_url).json()

#Obtener datos iniciales de las compras
api_url_compras = 'https://fakestoreapi.com/carts'  
compras_api = requests.get(api_url_compras).json()



#Descargamos la imagen 
for producto_data in productos_api:
    img_url = producto_data.get('image')
    img_nombre = str(producto_data.get('id'))+'.jpg'

    response = requests.get(img_url)
    with open('./imágenes/'+ img_nombre,'wb') as f:
        f.write(response.content)

#Obtener datos iniciales de las compras
api_url_compras = 'https://fakestoreapi.com/carts'  
compras_api = requests.get(api_url_compras).json()



#Descargamos la imagen 
for producto_data in productos_api:
    img_url = producto_data.get('image')
    img_nombre = str(producto_data.get('id'))+'.jpg'

    response = requests.get(img_url)
    with open('./imágenes/'+ img_nombre,'wb') as f:
        f.write(response.content)
              
# Conexión con la base de datos MongoDB
client = MongoClient('mongo', 27017)  #mi host y puerto 
tienda_db = client.tienda   #nombre base de datos 

productos_collection = tienda_db.productos



#Borramos si hay algo en la base de datos 
# Borrar todos los documentos de la colección "productos"
productos_collection.delete_many({})



# Insertar productos en la base de datos
for producto_data in productos_api:
 # Mapear los datos de la API a la estructura esperada por Producto
   
   
    producto_dict = {
    "nombre": producto_data["title"],
    "precio": producto_data["price"],
    "descripción": producto_data["description"],
    "categoría": producto_data["category"],
    "imágen": './imágenes/' + str(producto_data['id']) + '.jpg',
                   
    "rating": {
        "puntuación": producto_data["rating"]["rate"],
        "cuenta": producto_data["rating"]["count"]
    }
}
    
    # Crear una instancia de Producto a partir de los datos mapeados
    producto = Producto(**producto_dict)
    
    # Insertar el producto en la base de datos
    productos_collection.insert_one(producto.model_dump())


# Consultar productos para obtener sus índices en MongoDB
productos_en_bd = list(productos_collection.find())
productos_indices = [str(prod['_id']) for prod in productos_en_bd]


#Conexion base de datos,borramos los documentos de la coleccion compras
compras_collection = tienda_db.compras
compras_collection.delete_many({})


for compra_data in compras_api:
    #hacer una lista de productos para guardar los ids y el quantity
    compra_product_list= []
    for compra_produc in compra_data["products"]:
        producto_id=compra_produc["productId"]-1
        quantity = compra_produc["quantity"]

    #hacer una consulta para encontrar  ( ids y quantity) los productos insertados anteriormente 
    prod_api=productos_collection.find().limit(1).skip(producto_id).next()
    # Mapear los datos de la API a la estructura esperada por CompraAPI

    if prod_api:
        producto_dict = {
            "productId":prod_api['_id'],
            "quantity":quantity
        }
        #hago una lista con los datos encontrados en la busqueda 
        compra_product_list.append(producto_dict)
    
    # Mapear los datos de la API a la estructura esperada por  Compra

    nueva_compra = Compra(
        usuario = "correo.ejemplo@gmail.com",
        fecha=datetime.now(),
        productos=compra_product_list
    )



#validamos la compra 
    #compra = Compra(**nueva_compra)
    compras_collection.insert_one(nueva_compra.model_dump())


'''
# Realizar una compra de ejemplo
nueva_compra = {
    'usuario': 'fulanito@correo.com',
    'fecha': datetime.now(),
    'productos': productos_indices  # Referencia a los índices de MongoDB
}'''




# Conexión con la colección de compras
#compras_collection = tienda_db.compras

# Borrar todos los documentos de la colección "compras"
#compras_collection.delete_many({})

#compras_collection.insert_one(compra.dict())

# Imprimir el resultado
#print(f"Compra realizada: {compra.dict()}")

print(f"Compra realizada: {nueva_compra.model_dump()}")


# Consulta de productos de electrónica entre 100 y 200€, ordenados por precio
productos_electronica = productos_collection.find({
    "categoría": "electronics",
    "precio": {"$gte": 100, "$lte": 200}
}).sort("precio", 1)

'''
resultados_electronica = list(productos_electronica)

print("Productos de electrónica entre 100 y 200€:")
print("Número de resultados:", len(resultados_electronica))

'''

print("PRODUCTOS DE ELECTRÓNICA ENTRE 100 Y 200€, ORDENADOS POR PRECIO ")

for producto in productos_electronica:
    print(producto)

# Consulta de productos con la palabra 'pocket' en la descripción
productos_con_pocket = productos_collection.find({
    "descripción": {"$regex": "pocket", "$options": "i"}
})

print("PRODUCTOS CON LA PALABRA POCKET EN LA DESCRIPCIÓN")

for producto in productos_con_pocket:
    print(producto)

# Consulta de productos con una puntuación mayor de 4
productos_con_alta_puntuacion = productos_collection.find({
    "rating.puntuación": {"$gt": 4.0}
})
print("PRODUCTOS CON PUNTUACIÓN MAYOR DE 4")

for producto in productos_con_alta_puntuacion:
    print(producto)

# Ropa de hombre, ordenada por puntuación 
consulta_hombre = productos_collection.find({
     "categoría" : "men's clothing"
}).sort("rating.puntuacion", 1)

print("Ropa de hombre, ordenada por puntuación")
for producto in consulta_hombre:
    print(producto)

# Facturación total
total_compras = compras_collection.find()

facturacion_total = 0.0

for compra in total_compras:
    for producto_comprado in compra["productos"]:
        producto_id = producto_comprado["productId"]
        producto = productos_collection.find_one({"_id": producto_id})
        if producto:
            precio_producto = producto["precio"]
            cantidad_comprada = producto_comprado["quantity"]
            facturacion_total += precio_producto * cantidad_comprada

print(f"La facturación total es {round(facturacion_total, 2)} euros")

# Facturación por categoría de producto
facturacion_por_categoria = {}

total_compras = compras_collection.find()

for compra in total_compras:
    for producto_comprado in compra["productos"]:
        producto_id = producto_comprado["productId"]        
        producto = productos_collection.find_one({"_id": producto_id})
        
        if producto:
            categoria_producto = producto["categoría"]
            
            precio_producto = producto["precio"]
            cantidad_comprada = producto_comprado["quantity"]
            
            costo_total_producto = precio_producto * cantidad_comprada
            
            if categoria_producto in facturacion_por_categoria:
                facturacion_por_categoria[categoria_producto] += costo_total_producto
            else:
                facturacion_por_categoria[categoria_producto] = costo_total_producto

for categoria, facturacion in facturacion_por_categoria.items():
    print(f"Facturación en la categoría '{categoria}': {facturacion} euros")
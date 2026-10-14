#Añade el campo 'categoria' al cliente, el cual solo puede recibir los valores 'VIP', 'Regular' o 'Nuevo'. Por defecto debe ser 'Regular'."
#En models.py (Clase Cliente):
class Cliente(Persona):
    """Cliente ES UNA Persona, con teléfono, dirección y categoría."""

    def __init__(self, id_registro=0, nombre="", apellido="", email="", telefono="", direccion="", categoria="Regular"):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = str(telefono)
        self.direccion = str(direccion)
        self.categoria = str(categoria).title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["telefono"] = self.telefono
        datos["direccion"] = self.direccion
        datos["categoria"] = self.categoria
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.telefono} · Categoría: {self.categoria}"


#En views.py (Método validar en ClienteController):
if "categoria" in datos:
            cat = str(datos["categoria"]).strip().title()
            if cat not in ("Vip", "Regular", "Nuevo"):
                return "La categoría debe ser: VIP, Regular o Nuevo"


#main

datos = {
                "nombre": input("Nombre: "),
                "apellido": input("Apellido: "),
                "email": input("Email: "),
                "telefono": input("Teléfono: "),
                "direccion": input("Dirección: "),
                "categoria": input("Categoría [VIP/Regular/Nuevo] (por defecto Regular): ") or "Regular"
            }





#"Añade un método de búsqueda que permita encontrar a todos los clientes que pertenezcan a una categoría específica (por ejemplo, todos los 'VIP')
def buscar_por_categoria(self, categoria_buscada):
        """Devuelve una lista de clientes filtrados por su categoría."""
        categoria_buscada = categoria_buscada.strip().title()
        return [c for c in self.lista if c.categoria == categoria_buscada]






#En models.py (Actualización en la clase Producto)
#Le agregamos dos métodos a la clase Producto para verificar y restar el stock.


class Producto(ModeloBase):
    """Representa un producto dentro del sistema de inventario."""

    def __init__(self, id_registro=0, nombre="", precio=0.0, stock=0):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.precio = float(precio)
        self.stock = int(stock)

    def hay_stock(self, cantidad):
        """Verifica si hay suficiente cantidad disponible."""
        return self.stock >= int(cantidad)

    def descontar_stock(self, cantidad):
        """Resta la cantidad vendida del inventario si hay suficiente stock."""
        cantidad = int(cantidad)
        if self.hay_stock(cantidad):
            self.stock -= cantidad
            return True
        return False

    def devolver_stock(self, cantidad):
        """Devuelve la cantidad al inventario si se anula la venta."""
        self.stock += int(cantidad)
        return True

    def a_diccionario(self):
        return self.__dict__

    def etiqueta(self):
        return f"{self.nombre} · Precio: ${self.precio:.2f} · Stock: {self.stock} unidades"


#En views.py (Actualización en la clase VentaController)
#En la validación revisamos el stock con producto.hay_stock(), y al momento de crear la venta descontamos la cantidad y guardamos el producto actualizado.
class VentaController(CrudBase):

    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = [v.a_diccionario() for v in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser enteros válidos"

        if cantidad <= 0:
            return "La cantidad a vender debe ser mayor a 0"

        if not self.clientes.obtener(cliente_id):
            return f"No existe un cliente registrado con ID {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if not producto:
            return f"No existe un producto registrado con ID {producto_id}"

        # VALIDACIÓN DE STOCK DISPONIBLE
        if not producto.hay_stock(cantidad):
            return (f"Stock insuficiente para '{producto.nombre}'. "
                    f"Disponible: {producto.stock} unidades | Solicitado: {cantidad} unidades")

        return None

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        producto = self.productos.obtener(int(datos["producto_id"]))
        cantidad = int(datos["cantidad"])
        total = producto.precio * cantidad

        # APLICAR DESCUENTO DE STOCK Y GUARDAR CAMBIOS EN PRODUCTOS
        producto.descontar_stock(cantidad)
        self.productos.guardar()

        venta = Venta(
            self.siguiente(),
            int(datos["cliente_id"]),
            producto.id,
            cantidad,
            total,
            str(datos.get("fecha", "")).strip()
        )
        self.lista.append(venta)
        self.guardar()
        return True, f"Venta #{venta.id} registrada con éxito. Total: ${total:.2f}"






    



#Paso 1: Actualizar la clase Cliente en models.py
#Le agregamos el atributo categoria para poder identificar si el cliente goza de este beneficio:
class Cliente(Persona):
    """Cliente ES UNA Persona, con teléfono, dirección y categoría."""

    def __init__(id_registro=0, nombre="", apellido="", email="", telefono="", direccion="", categoria="Regular"):
        # Nota: Asegúrate de mantener la llamada a super().__init__ según tu estructura base
        pass

# Aquí te dejo la clase Cliente completa con el cambio integrado:
class Cliente(Persona):
    """Cliente ES UNA Persona, con teléfono, dirección y categoría."""

    def __init__(self, id_registro=0, nombre="", apellido="", email="", telefono="", direccion="", categoria="Regular"):
        super().__init__(id_registro, nombre, apellido, email)
        self.telefono = str(telefono)
        self.direccion = str(direccion)
        self.categoria = str(categoria).strip().title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["telefono"] = self.telefono
        datos["direccion"] = self.direccion
        datos["categoria"] = self.categoria
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · Tel: {self.telefono} · Cat: {self.categoria}"

#Paso 2: Actualizar el método crear en VentaController (views.py)
#Aquí es donde ocurre la magia de la regla de negocio. Consultamos al cliente a través de su ID, evaluamos su categoría y aplicamos el cálculo del descuento:

class VentaController(CrudBase):

    def __init__(self, clientes, productos, archivo="data/ventas.json"):
        self.clientes = clientes
        self.productos = productos
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Venta.desde_diccionario(datos))

    def guardar(self):
        datos = [v.a_diccionario() for v in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            cliente_id = int(datos.get("cliente_id", 0))
            producto_id = int(datos.get("producto_id", 0))
            cantidad = int(datos.get("cantidad", 0))
        except (TypeError, ValueError):
            return "cliente_id, producto_id y cantidad deben ser enteros válidos"

        if cantidad <= 0:
            return "La cantidad a vender debe ser mayor a 0"

        if not self.clientes.obtener(cliente_id):
            return f"No existe un cliente registrado con ID {cliente_id}"

        producto = self.productos.obtener(producto_id)
        if not producto:
            return f"No existe un producto registrado con ID {producto_id}"

        if not producto.hay_stock(cantidad):
            return f"Stock insuficiente para '{producto.nombre}'. Disponible: {producto.stock}"

        return None

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cliente_id = int(datos["cliente_id"])
        producto_id = int(datos["producto_id"])
        cantidad = int(datos["cantidad"])

        cliente = self.clientes.obtener(cliente_id)
        producto = self.productos.obtener(producto_id)

        # 1. Calcular subtotal base
        subtotal = producto.precio * cantidad

        # 2. APLICAR REGLA DE DESCUENTO VIP (10%)
        descuento = 0.0
        if cliente and cliente.categoria == "Vip":
            descuento = subtotal * 0.10

        total = subtotal - descuento

        # 3. Descontar stock del producto y guardar
        producto.descontar_stock(cantidad)
        self.productos.guardar()

        # 4. Crear la venta guardando el total ya con descuento aplicado
        venta = Venta(
            self.siguiente(),
            cliente_id,
            producto.id,
            cantidad,
            round(total, 2),
            str(datos.get("fecha", "")).strip()
        )
        self.lista.append(venta)
        self.guardar()

        mensaje = f"Venta #{venta.id} registrada. Subtotal: ${subtotal:.2f}"
        if descuento > 0:
            mensaje += f" (Desc. VIP 10%: -${descuento:.2f}) -> Total: ${total:.2f}"
        else:
            mensaje += f" -> Total: ${total:.2f}"

        return True, mensaje
    































#Modifica el cálculo del total de la venta: si el cliente es categoría 'VIP', aplica un 10% de descuento automático sobre el subtotal
#¿Dónde se modifica?
#models.py (Clase Cliente o Venta):
#Si el cliente tiene un atributo categoria, la venta puede consultarlo.


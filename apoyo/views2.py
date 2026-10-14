#Agrega al resumen general el promedio de notas global de toda la institución o el estudiante con el promedio más alto
#En views.py (se agrega un método auxiliar en MatriculaController) y en main.py (se invoca dentro de mostrar_resumen).



from abc import ABC, abstractmethod
from models import Estudiante, Materia, Matricula
from shared.json_manager import GestorJSON
from shared.herramientas import es_email_valido


class CrudBase(ABC):
    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def obtener(self, id_registro):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


class EstudianteController(CrudBase):

    def __init__(self, archivo="data/estudiantes.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Estudiante.desde_diccionario(datos))

    def guardar(self):
        datos = [e.a_diccionario() for e in self.lista]
        self.gestor.guardar(datos)

    def carnets_registrados(self, excepto_id=None):
        """CONJUNTO de carnets ya usados: preguntar 'x in conjunto' es instantáneo."""
        return {e.carnet.upper() for e in self.lista if e.id != excepto_id}

    def emails_registrados(self, excepto_id=None):
        """CONJUNTO de emails ya usados para validación rápida."""
        return {e.email.lower() for e in self.lista if e.id != excepto_id}

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "apellido", "email", "carnet"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            if not es_email_valido(email):
                return f"Email inválido: '{email}'"
            if email in self.emails_registrados(id_actual):
                return "Ese email ya está registrado"

        if "carnet" in datos:
            carnet = str(datos["carnet"]).strip().upper()
            if carnet in self.carnets_registrados(id_actual):
                return f"El carnet '{carnet}' ya está registrado"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_estudiante):
        for e in self.lista:
            if e.id == id_estudiante:
                return e
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []
        encontrados = []
        for e in self.lista:
            if (texto in e.nombre.lower() or
                texto in e.apellido.lower() or
                texto in e.email.lower() or
                texto in e.carnet.lower() or
                texto in e.carrera.lower()):
                encontrados.append(e)
        return encontrados

    def siguiente(self):
        mayor = max([e.id for e in self.lista], default=0)
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        estudiante = Estudiante(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["apellido"]).strip().title(),
            str(datos["email"]).strip().lower(),
            str(datos["carnet"]).strip().upper(),
            str(datos.get("carrera", "")).strip().title()
        )
        self.lista.append(estudiante)
        self.guardar()
        return True, f"Estudiante creado: {estudiante.etiqueta()}"

    def actualizar(self, id_estudiante, datos):
        estudiante = self.obtener(id_estudiante)
        if not estudiante:
            return False, f"No existe un estudiante con id {id_estudiante}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "apellido", "email", "carnet", "carrera"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_estudiante)
        if error:
            return False, error

        for campo, valor in datos.items():
            valor = str(valor).strip()
            if campo in ("nombre", "apellido", "carrera"):
                valor = valor.title()
            elif campo == "email":
                valor = valor.lower()
            elif campo == "carnet":
                valor = valor.upper()
            setattr(estudiante, campo, valor)

        self.guardar()
        return True, f"Estudiante {id_estudiante} actualizado"

    def eliminar(self, id_estudiante):
        estudiante = self.obtener(id_estudiante)
        if not estudiante:
            return False, f"No existe un estudiante con id {id_estudiante}"
        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"


class MateriaController(CrudBase):

    def __init__(self, archivo="data/materias.json"):
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Materia.desde_diccionario(datos))

    def guardar(self):
        datos = [m.a_diccionario() for m in self.lista]
        self.gestor.guardar(datos)

    def codigos_registrados(self, excepto_id=None):
        """CONJUNTO de códigos de materias únicos."""
        return {m.codigo.upper() for m in self.lista if m.id != excepto_id}

    def validar(self, datos, id_actual=None):
        if id_actual is None:
            for campo in ("nombre", "codigo", "creditos"):
                if str(datos.get(campo, "")).strip() == "":
                    return f"El campo {campo} es obligatorio"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            if codigo in self.codigos_registrados(id_actual):
                return f"El código '{codigo}' ya está registrado"

        if "creditos" in datos:
            try:
                creditos = int(datos["creditos"])
                if not (1 <= creditos <= 10):
                    return "Los créditos deben estar entre 1 y 10"
            except ValueError:
                return "Los créditos deben ser un número entero"

        if "cupos" in datos:
            try:
                cupos = int(datos["cupos"])
                if not (0 <= cupos <= Materia.CUPOS_MAXIMOS):
                    return f"Los cupos deben estar entre 0 y {Materia.CUPOS_MAXIMOS}"
            except ValueError:
                return "Los cupos deben ser un número entero"

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_materia):
        for m in self.lista:
            if m.id == id_materia:
                return m
        return None

    def buscar(self, texto):
        texto = texto.strip().lower()
        if not texto:
            return []
        encontrados = []
        for m in self.lista:
            if texto in m.nombre.lower() or texto in m.codigo.lower():
                encontrados.append(m)
        return encontrados

    def siguiente(self):
        mayor = max([m.id for m in self.lista], default=0)
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        cupos = int(datos.get("cupos", Materia.CUPOS_MAXIMOS))
        materia = Materia(
            self.siguiente(),
            str(datos["nombre"]).strip().title(),
            str(datos["codigo"]).strip().upper(),
            int(datos["creditos"]),
            cupos
        )
        self.lista.append(materia)
        self.guardar()
        return True, f"Materia creada: {materia.etiqueta()}"

    def actualizar(self, id_materia, datos):
        materia = self.obtener(id_materia)
        if not materia:
            return False, f"No existe una materia con id {id_materia}"
        if not datos:
            return False, "No se indicó ningún cambio"

        permitidos = {"nombre", "codigo", "creditos", "cupos"}
        desconocidos = set(datos) - permitidos
        if desconocidos:
            return False, f"Campos no válidos: {', '.join(sorted(desconocidos))}"

        error = self.validar(datos, id_materia)
        if error:
            return False, error

        if "nombre" in datos:
            materia.nombre = str(datos["nombre"]).strip().title()
        if "codigo" in datos:
            materia.codigo = str(datos["codigo"]).strip().upper()
        if "creditos" in datos:
            materia.creditos = int(datos["creditos"])
        if "cupos" in datos:
            materia.cupos = int(datos["cupos"])

        self.guardar()
        return True, f"Materia {id_materia} actualizada"

    def eliminar(self, id_materia):
        materia = self.obtener(id_materia)
        if not materia:
            return False, f"No existe una materia con id {id_materia}"
        self.lista.remove(materia)
        self.guardar()
        return True, f"Materia {id_materia} eliminada"

    def materias_sin_cupo(self):
        """Lista de materias con cupos agotados."""
        return [m for m in self.lista if not m.hay_cupo()]


class MatriculaController(CrudBase):

    def __init__(self, estudiantes, materias, archivo="data/matriculas.json"):
        self.estudiantes = estudiantes
        self.materias = materias
        self.gestor = GestorJSON(archivo)
        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Matricula.desde_diccionario(datos))

    def guardar(self):
        datos = [mat.a_diccionario() for mat in self.lista]
        self.gestor.guardar(datos)

    def validar(self, datos):
        try:
            estudiante_id = int(datos.get("estudiante_id", 0))
            materia_id = int(datos.get("materia_id", 0))
        except (TypeError, ValueError):
            return "estudiante_id y materia_id deben ser números enteros"

        if not self.estudiantes.obtener(estudiante_id):
            return f"No existe un estudiante con id {estudiante_id}"

        materia = self.materias.obtener(materia_id)
        if not materia:
            return f"No existe una materia con id {materia_id}"

        if not materia.hay_cupo():
            return f"La materia {materia.nombre} no tiene cupos disponibles"

        periodo = str(datos.get("periodo", "")).strip()
        if not periodo:
            return "El periodo académico es obligatorio"

        # 1) Validar duplicidad en la misma materia y periodo
        for mat in self.lista:
            if mat.estudiante_id == estudiante_id and mat.materia_id == materia_id and mat.periodo == periodo:
                return "El estudiante ya está matriculado en esta materia para este periodo"

        # 2) Validar límite máximo de créditos por periodo (ej. Máximo 20 créditos)
        MAX_CREDITOS_PERIODO = 20
        creditos_actuales = sum(
            self.materias.obtener(mat.materia_id).creditos 
            for mat in self.lista 
            if mat.estudiante_id == estudiante_id and mat.periodo == periodo and self.materias.obtener(mat.materia_id)
        )

        if creditos_actuales + materia.creditos > MAX_CREDITOS_PERIODO:
            return (f"Límite de créditos excedido para el periodo {periodo}. "
                    f"Ya cursa {creditos_actuales} créditos y esta materia tiene {materia.creditos} "
                    f"(Máximo permitido: {MAX_CREDITOS_PERIODO})")

        return None

    def leer(self):
        return self.lista

    def obtener(self, id_matricula):
        for mat in self.lista:
            if mat.id == id_matricula:
                return mat
        return None

    def buscar(self, texto):
        texto = texto.strip()
        if not texto:
            return []
        encontrados = []
        for mat in self.lista:
            if texto in mat.periodo or texto in mat.fecha:
                encontrados.append(mat)
        return encontrados

    def siguiente(self):
        mayor = max([mat.id for mat in self.lista], default=0)
        return mayor + 1

    def crear(self, datos):
        error = self.validar(datos)
        if error:
            return False, error

        materia = self.materias.obtener(int(datos["materia_id"]))
        
        materia.ocupar_cupo()
        self.materias.guardar()

        matricula = Matricula(
            self.siguiente(),
            int(datos["estudiante_id"]),
            materia.id,
            str(datos["periodo"]).strip(),
            float(datos.get("nota", 0.0)),
            str(datos.get("fecha", "")).strip()
        )
        self.lista.append(matricula)
        self.guardar()
        return True, f"Matrícula #{matricula.id} registrada con éxito"

    def actualizar(self, id_matricula, datos):
        return False, "Las matrículas no se modifican directamente: use registrar nota o retire la matrícula"

    def eliminar(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if not matricula:
            return False, f"No existe la matrícula {id_matricula}"

        materia = self.materias.obtener(matricula.materia_id)
        if materia:
            materia.liberar_cupo()
            self.materias.guardar()

        self.lista.remove(matricula)
        self.guardar()
        return True, f"Matrícula #{id_matricula} retirada y cupo devuelto"

    def registrar_nota(self, id_matricula, nota):
        if not Materia.es_nota_valida(nota):
            return False, "Nota inválida (debe ser un número entre 0 y 20)"
        
        matricula = self.obtener(id_matricula)
        if not matricula:
            return False, f"No existe la matrícula {id_matricula}"

        matricula.nota = float(nota)
        self.guardar()
        return True, f"Nota registrada para la matrícula #{id_matricula}: {matricula.nota} ({matricula.estado()})"

    def retirar_matricula(self, id_matricula):
        return self.eliminar(id_matricula)

    def certificado(self, id_matricula):
        matricula = self.obtener(id_matricula)
        if not matricula:
            return None

        estudiante = self.estudiantes.obtener(matricula.estudiante_id)
        materia = self.materias.obtener(matricula.materia_id)

        texto = f"CERTIFICADO #{matricula.id}   periodo: {matricula.periodo}\n"
        texto += f"Estudiante: {estudiante.nombre} {estudiante.apellido}   ({estudiante.carnet})\n"
        texto += f"Materia   : {materia.nombre}   ({materia.codigo}) · {materia.creditos} créditos\n"
        texto += "-" * 42 + "\n"
        texto += f"Nota      : {matricula.nota}\n"
        texto += f"Estado    : {matricula.estado()}"
        return texto

    def matriculas_por_estudiante(self):
        agrupadas = {}
        for mat in self.lista:
            agrupadas.setdefault(mat.estudiante_id, []).append(mat)
        return agrupadas

    def promedio_de_estudiante(self, estudiante_id):
        mats = self.matriculas_por_estudiante().get(estudiante_id, [])
        if not mats:
            return 0.0
        suma = sum(mat.nota for mat in mats)
        return round(suma / len(mats), 2)

    def promedio_general_institucional(self):
        """Calcula el promedio general de todas las notas registradas."""
        if not self.lista:
            return 0.0
        suma_notas = sum(m.nota for m in self.lista)
        return round(suma_notas / len(self.lista), 2)


#main

#Código en main.py (mostrar_resumen):
#Remplazas la función mostrar_resumen completa:

from views import EstudianteController, MateriaController, MatriculaController
from models import Materia
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, 
    imprimir_info, confirmar, limpiar_pantalla
)
import datetime


def mostrar_lista(elementos):
    if not elementos:
        imprimir_info("No hay registros para mostrar.")
        return
    for item in elementos:
        print(f" - {item.etiqueta()}")
    print()


def mostrar_detalle(item):
    if not item:
        imprimir_error("Elemento no encontrado.")
        return
    print("-" * 40)
    print(f" Detalle: {item.etiqueta()}")
    print("-" * 40)


def menu_estudiantes(ctrl):
    while True:
        imprimir_titulo("GESTIÓN DE ESTUDIANTES")
        print("1. Crear estudiante")
        print("2. Ver todos los estudiantes")
        print("3. Buscar estudiante")
        print("4. Ver estudiante por ID")
        print("5. Actualizar estudiante")
        print("6. Eliminar estudiante")
        print("0. Volver al menú principal")
        
        opcion = input("\nElige una opción: ").strip()
        
        if opcion == "1":
            imprimir_titulo("CREAR ESTUDIANTE")
            datos = {
                "nombre": input("Nombre: "),
                "apellido": input("Apellido: "),
                "email": input("Email: "),
                "carnet": input("Carnet (ej. EST2026001): "),
                "carrera": input("Carrera: ")
            }
            exito, mensaje = ctrl.crear(datos)
            imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "2":
            imprimir_titulo("LISTA DE ESTUDIANTES")
            mostrar_lista(ctrl.leer())
            input("Presiona Enter para continuar...")
            
        elif opcion == "3":
            imprimir_titulo("BUSCAR ESTUDIANTE")
            texto = input("Texto a buscar (nombre, carnet, etc.): ")
            resultados = ctrl.buscar(texto)
            imprimir_info(f"Se encontraron {len(resultados)} resultados:")
            mostrar_lista(resultados)
            input("Presiona Enter para continuar...")
            
        elif opcion == "4":
            imprimir_titulo("VER ESTUDIANTE POR ID")
            try:
                id_reg = int(input("ID del estudiante: "))
                mostrar_detalle(ctrl.obtener(id_reg))
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "5":
            imprimir_titulo("ACTUALIZAR ESTUDIANTE")
            try:
                id_reg = int(input("ID del estudiante a actualizar: "))
                est = ctrl.obtener(id_reg)
                if not est:
                    imprimir_error("Estudiante no encontrado.")
                else:
                    print(f"Actualizando a: {est.etiqueta()}")
                    print("Deje en blanco el campo si no desea cambiarlo.")
                    datos = {}
                    for campo in ("nombre", "apellido", "email", "carnet", "carrera"):
                        val = input(f"Nuevo {campo} [{getattr(est, campo)}]: ").strip()
                        if val:
                            datos[campo] = val
                    exito, mensaje = ctrl.actualizar(id_reg, datos)
                    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "6":
            imprimir_titulo("ELIMINAR ESTUDIANTE")
            try:
                id_reg = int(input("ID del estudiante a eliminar: "))
                if confirmar("¿Está seguro de eliminar este estudiante?"):
                    exito, mensaje = ctrl.eliminar(id_reg)
                    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "0":
            break
        else:
            imprimir_error("Opción inválida.")
            input("Presiona Enter para continuar...")


def menu_materias(ctrl):
    while True:
        imprimir_titulo("GESTIÓN DE MATERIAS")
        print("1. Crear materia")
        print("2. Ver todas las materias")
        print("3. Buscar materia")
        print("4. Ver materia por ID")
        print("5. Actualizar materia")
        print("6. Eliminar materia")
        print("0. Volver al menú principal")
        
        opcion = input("\nElige una opción: ").strip()
        
        if opcion == "1":
            imprimir_titulo("CREAR MATERIA")
            datos = {
                "nombre": input("Nombre de la materia: "),
                "codigo": input("Código (ej. MAT101): "),
                "creditos": input("Créditos (1-10): "),
                "cupos": input(f"Cupos (máximo {Materia.CUPOS_MAXIMOS}): ")
            }
            exito, mensaje = ctrl.crear(datos)
            imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "2":
            imprimir_titulo("LISTA DE MATERIAS")
            mostrar_lista(ctrl.leer())
            input("Presiona Enter para continuar...")
            
        elif opcion == "3":
            imprimir_titulo("BUSCAR MATERIA")
            texto = input("Texto a buscar: ")
            resultados = ctrl.buscar(texto)
            imprimir_info(f"Se encontraron {len(resultados)} resultados:")
            mostrar_lista(resultados)
            input("Presiona Enter para continuar...")
            
        elif opcion == "4":
            imprimir_titulo("VER MATERIA POR ID")
            try:
                id_reg = int(input("ID de la materia: "))
                mostrar_detalle(ctrl.obtener(id_reg))
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "5":
            imprimir_titulo("ACTUALIZAR MATERIA")
            try:
                id_reg = int(input("ID de la materia a actualizar: "))
                mat = ctrl.obtener(id_reg)
                if not mat:
                    imprimir_error("Materia no encontrada.")
                else:
                    print(f"Actualizando a: {mat.etiqueta()}")
                    datos = {}
                    for campo in ("nombre", "codigo", "creditos", "cupos"):
                        val = input(f"Nuevo {campo} [{getattr(mat, campo)}]: ").strip()
                        if val:
                            datos[campo] = val
                    exito, mensaje = ctrl.actualizar(id_reg, datos)
                    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "6":
            imprimir_titulo("ELIMINAR MATERIA")
            try:
                id_reg = int(input("ID de la materia a eliminar: "))
                if confirmar("¿Está seguro de eliminar esta materia?"):
                    exito, mensaje = ctrl.eliminar(id_reg)
                    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "0":
            break
        else:
            imprimir_error("Opción inválida.")
            input("Presiona Enter para continuar...")


def menu_matriculas(ctrl):
    while True:
        imprimir_titulo("GESTIÓN DE MATRÍCULAS")
        print("1. Matricular estudiante")
        print("2. Ver todas las matrículas")
        print("3. Registrar nota")
        print("4. Ver certificado")
        print("5. Retirar matrícula")
        print("0. Volver al menú principal")
        
        opcion = input("\nElige una opción: ").strip()
        
        if opcion == "1":
            imprimir_titulo("NUEVA MATRÍCULA")
            datos = {
                "estudiante_id": input("ID del Estudiante: "),
                "materia_id": input("ID de la Materia: "),
                "periodo": input("Periodo académico (ej. 2026-1): "),
                "nota": input("Nota inicial (opcional, por defecto 0): ") or "0.0",
                "fecha": datetime.date.today().strftime("%Y-%m-%d")
            }
            exito, mensaje = ctrl.crear(datos)
            imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "2":
            imprimir_titulo("LISTA DE MATRÍCULAS")
            mostrar_lista(ctrl.leer())
            input("Presiona Enter para continuar...")
            
        elif opcion == "3":
            imprimir_titulo("REGISTRAR NOTA")
            try:
                id_reg = int(input("ID de la matrícula: "))
                nota_val = float(input("Ingrese la nota (0 a 20): "))
                exito, mensaje = ctrl.registrar_nota(id_reg, nota_val)
                imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("Datos numéricos inválidos.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "4":
            imprimir_titulo("CERTIFICADO DE MATRÍCULA")
            try:
                id_reg = int(input("ID de la matrícula: "))
                cert = ctrl.certificado(id_reg)
                if cert:
                    print(cert)
                else:
                    imprimir_error("Matrícula no encontrada.")
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "5":
            imprimir_titulo("RETIRAR MATRÍCULA")
            try:
                id_reg = int(input("ID de la matrícula a retirar: "))
                if confirmar("¿Está seguro de retirar esta matrícula?"):
                    exito, mensaje = ctrl.retirar_matricula(id_reg)
                    imprimir_exito(mensaje) if exito else imprimir_error(mensaje)
            except ValueError:
                imprimir_error("ID inválido.")
            input("\nPresiona Enter para continuar...")
            
        elif opcion == "0":
            break
        else:
            imprimir_error("Opción inválida.")
            input("Presiona Enter para continuar...")


def mostrar_resumen(estudiantes_ctrl, materias_ctrl, matriculas_ctrl):
    imprimir_titulo("RESUMEN DEL SISTEMA ACADÉMICO")
    
    total_estudiantes = len(estudiantes_ctrl.leer())
    carreras = sorted({e.carrera for e in estudiantes_ctrl.leer() if e.carrera})
    materias_agotadas = len(materias_ctrl.materias_sin_cupo())
    aprobadas = sum(1 for m in matriculas_ctrl.leer() if m.esta_aprobada())
    
    # NUEVO DATO CALCULADO
    promedio_global = matriculas_ctrl.promedio_general_institucional()
    
    print(f"• Total de estudiantes registrados : {total_estudiantes}")
    print(f"• Carreras distintas               : {', '.join(carreras) if carreras else 'Ninguna'}")
    print(f"• Materias sin cupo disponible     : {materias_agotadas}")
    print(f"• Matrículas aprobadas             : {aprobadas}")
    print(f"• Promedio general institucional   : {promedio_global}")
    print()


def main():
    estudiantes_ctrl = EstudianteController()
    materias_ctrl = MateriaController()
    matriculas_ctrl = MatriculaController(estudiantes_ctrl, materias_ctrl)
    
    while True:
        imprimir_titulo("SISTEMA ACADÉMICO UNIDAD EDUCATIVA")
        print("1. Estudiantes")
        print("2. Materias")
        print("3. Matrículas")
        print("4. Resumen del sistema")
        print("0. Salir")
        
        opcion = input("\nElige una opción: ").strip()
        
        if opcion == "1":
            menu_estudiantes(estudiantes_ctrl)
        elif opcion == "2":
            menu_materias(materias_ctrl)
        elif opcion == "3":
            menu_matriculas(matriculas_ctrl)
        elif opcion == "4":
            mostrar_resumen(estudiantes_ctrl, materias_ctrl, matriculas_ctrl)
            input("Presiona Enter para continuar...")
        elif opcion == "0":
            imprimir_info("¡Hasta luego!")
            break
        else:
            imprimir_error("Opción inválida. Intente de nuevo.")
            input("Presiona Enter para continuar...")


if __name__ == "__main__":
    main()





#Evitar la eliminación de una entidad con dependencias
#Lo que pediría el profesor:

#"Si un estudiante tiene matrículas activas, no permitas que sea eliminado hasta que retire o borre sus matrículas."

#¿Dónde se modifica?
#En views.py (método eliminar dentro de EstudianteController).

def eliminar(self, id_estudiante, matriculas_ctrl=None):
        estudiante = self.obtener(id_estudiante)
        if not estudiante:
            return False, f"No existe un estudiante con id {id_estudiante}"
        
        # VALIDACIÓN DE INTEGRIDAD REFERENCIAL
        if matriculas_ctrl:
            tiene_matriculas = any(m.estudiante_id == id_estudiante for m in matriculas_ctrl.leer())
            if tiene_matriculas:
                return False, f"No se puede eliminar al estudiante #{id_estudiante} porque tiene matrículas registradas"

        self.lista.remove(estudiante)
        self.guardar()
        return True, f"Estudiante {id_estudiante} eliminado"
#Modifica la lógica para que las notas no solo sean Aprobado o Reprobado. 
#Si la nota está entre 10.0 y 13.9, el estado debe ser 'Recuperación'. Si es 14.0 o más, 'Aprobado', y si es menor a 10.0, 'Reprobado'."

class ModeloBase:
    """Clase base para todos los modelos del sistema."""
    
    def __init__(self, id_registro=0):
        self.id = int(id_registro)

    def a_diccionario(self):
        return self.__dict__

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(**datos)

    def etiqueta(self):
        return f"ID: {self.id}"


class Persona(ModeloBase):
    """Representa a una persona dentro de la unidad educativa."""
    
    def __init__(self, id_registro=0, nombre="", apellido="", email=""):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.apellido = str(apellido)
        self.email = str(email)

    def etiqueta(self):
        return f"{self.nombre} {self.apellido}"


class Estudiante(Persona):
    """Estudiante ES UNA Persona, con carnet y carrera."""

    def __init__(self, id_registro=0, nombre="", apellido="", email="", carnet="", carrera=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.carnet = str(carnet)
        self.carrera = str(carrera)

    def a_diccionario(self):
        datos = super().a_diccionario()  # id, nombre, apellido, email
        datos["carnet"] = self.carnet
        datos["carrera"] = self.carrera
        return datos

    def etiqueta(self):
        return f"{super().etiqueta()} · {self.carnet} · {self.carrera}"


class Materia(ModeloBase):
    """Aquí va TODO lo estático de tu proyecto."""

    CUPOS_MAXIMOS = 30
    NOTA_APROBACION = 14

    def __init__(self, id_registro=0, nombre="", codigo="", creditos=0, cupos=30):
        super().__init__(id_registro)
        self.nombre = str(nombre)
        self.codigo = str(codigo)
        self.creditos = int(creditos)
        self.cupos = int(cupos)

    @staticmethod
    def es_nota_valida(valor):
        try:
            nota = float(valor)
            return 0.0 <= nota <= 20.0
        except (TypeError, ValueError):
            return False

    def hay_cupo(self):
        return self.cupos > 0

    def ocupar_cupo(self):
        if self.hay_cupo():
            self.cupos -= 1
            return True
        return False

    def liberar_cupo(self):
        if self.cupos < self.CUPOS_MAXIMOS:
            self.cupos += 1
            return True
        return False

    def a_diccionario(self):
        return self.__dict__

    def etiqueta(self):
        return f"({self.codigo}) {self.nombre} · Créditos: {self.creditos} · Cupos: {self.cupos}/{self.CUPOS_MAXIMOS}"


class Matricula(ModeloBase):
    """Representa la inscripción de un estudiante en una materia."""

    def __init__(self, id_registro=0, estudiante_id=0, materia_id=0, periodo="", nota=0.0, fecha=""):
        super().__init__(id_registro)
        self.estudiante_id = int(estudiante_id)
        self.materia_id = int(materia_id)
        self.periodo = str(periodo)
        self.nota = float(nota)
        self.fecha = str(fecha)

    def esta_aprobada(self):
        return self.nota >= Materia.NOTA_APROBACION

    def estado(self):
        # Lógica de tres estados basada en la nota
        if self.nota >= Materia.NOTA_APROBACION:  # 14 en adelante
            return "Aprobado"
        elif self.nota >= 10.0:                   # De 10.0 a 13.9
            return "En Recuperación"
        else:                                     # Menor a 10.0
            return "Reprobado"

    def a_diccionario(self):
        return self.__dict__

    def etiqueta(self):
        return f"Matrícula #{self.id} | Periodo: {self.periodo} | Nota: {self.nota} ({self.estado()})"
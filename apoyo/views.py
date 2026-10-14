#CAMBIO EN EL VIEWS  Modifica el sistema para que un estudiante no pueda matricularse en mAs de un nUmero maximo de creditos (por ejemplo, 20 creditos) en un mismo periodo academico.
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
        
        # Sumamos los créditos de las materias en las que ya está matriculado en ese mismo periodo
        creditos_actuales = sum(
            self.materias.obtener(mat.materia_id).creditos 
            for mat in self.lista 
            if mat.estudiante_id == estudiante_id and mat.periodo == periodo and self.materias.obtener(mat.materia_id)
        )

        # Verificamos si al sumar la nueva materia se pasa del límite
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
        
        # Ocupar el cupo en la materia y guardar cambios
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
        """Retirar matrícula: se borra y el cupo vuelve a la materia."""
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
        """DICCIONARIO índice para cruzar entidades y armar el certificado."""
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
        """DICCIONARIO de LISTAS: {estudiante_id: [matrículas de ese estudiante]} usando setdefault."""
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
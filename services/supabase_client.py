"""
Cliente de Supabase para interactuar con la base de datos
"""
from supabase import create_client, Client
from config import get_config
import logging

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Cliente singleton para Supabase"""

    _instance = None
    _client: Client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa el cliente de Supabase"""
        config = get_config()
        url = config.SUPABASE_URL
        # Usar SERVICE_KEY para evitar restricciones RLS
        key = config.SUPABASE_SERVICE_KEY or config.SUPABASE_KEY

        if not url or not key:
            logger.error("Supabase credentials not configured")
            raise ValueError(
                "SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar configurados en .env"
            )

        self._client = create_client(url, key)
        logger.info(f"Supabase client initialized successfully (using {'SERVICE_KEY' if config.SUPABASE_SERVICE_KEY else 'ANON_KEY'})")

    @property
    def client(self) -> Client:
        """Retorna la instancia del cliente de Supabase"""
        return self._client

    def get_students(self, limit=100):
        """
        Obtiene la lista de estudiantes con sus datos relacionados
        
        Args:
            limit: Número máximo de estudiantes a retornar
            
        Returns:
            Lista de estudiantes con datos socioeconómicos, asistencia y rendimiento
        """
        try:
            # Intentar primero con la sintaxis de join de Supabase
            response = (
                self._client.table("students")
                .select(
                    """
                    *,
                    socioeconomic_data(*),
                    academic_performance(*),
                    attendance(*)
                """
                )
                .limit(limit)
                .execute()
            )
            
            students = response.data
            
            # Verificar si los joins funcionaron (si el primer estudiante tiene datos relacionados)
            if students and not students[0].get("socioeconomic_data"):
                logger.info("Supabase joins not working, fetching related data separately...")
                students = self._fetch_students_with_related_data(limit)
            
            return students
        except Exception as e:
            logger.error(f"Error getting students: {str(e)}", exc_info=True)
            # Fallback: intentar obtener datos por separado
            try:
                return self._fetch_students_with_related_data(limit)
            except Exception as e2:
                logger.error(f"Fallback also failed: {str(e2)}", exc_info=True)
                return []

    def _fetch_students_with_related_data(self, limit=100):
        """
        Obtiene estudiantes y sus datos relacionados mediante queries separadas
        (Fallback cuando los joins de Supabase no funcionan)
        """
        # Obtener estudiantes base
        students_response = self._client.table("students").select("*").limit(limit).execute()
        students = students_response.data
        
        if not students:
            return []
        
        # Obtener IDs de estudiantes
        student_ids = [s["id"] for s in students]
        
        # Obtener datos socioeconómicos para todos los estudiantes
        socio_response = self._client.table("socioeconomic_data").select("*").in_("student_id", student_ids).execute()
        socio_by_student = {}
        for socio in socio_response.data:
            sid = socio["student_id"]
            if sid not in socio_by_student:
                socio_by_student[sid] = []
            socio_by_student[sid].append(socio)
        
        # Obtener datos de asistencia
        attendance_response = self._client.table("attendance").select("*").in_("student_id", student_ids).execute()
        attendance_by_student = {}
        for att in attendance_response.data:
            sid = att["student_id"]
            if sid not in attendance_by_student:
                attendance_by_student[sid] = []
            attendance_by_student[sid].append(att)
        
        # Obtener rendimiento académico
        academic_response = self._client.table("academic_performance").select("*").in_("student_id", student_ids).execute()
        academic_by_student = {}
        for acad in academic_response.data:
            sid = acad["student_id"]
            if sid not in academic_by_student:
                academic_by_student[sid] = []
            academic_by_student[sid].append(acad)
        
        # Combinar datos
        for student in students:
            sid = student["id"]
            student["socioeconomic_data"] = socio_by_student.get(sid, [])
            student["attendance"] = attendance_by_student.get(sid, [])
            student["academic_performance"] = academic_by_student.get(sid, [])
        
        logger.info(f"Fetched {len(students)} students with related data via separate queries")
        return students

    def get_student_by_id(self, student_id):
        """
        Obtiene un estudiante específico por ID con todos sus datos relacionados
        
        Args:
            student_id: ID del estudiante
            
        Returns:
            Datos del estudiante o None si no existe
        """
        try:
            # Intentar con join de Supabase
            response = (
                self._client.table("students")
                .select(
                    """
                    *,
                    socioeconomic_data(*),
                    academic_performance(*),
                    attendance(*)
                """
                )
                .eq("id", student_id)
                .maybe_single()
                .execute()
            )
            student = response.data
            
            # Verificar si los joins funcionaron
            if student and not student.get("socioeconomic_data"):
                logger.info(f"Supabase joins not working for student {student_id}, fetching separately...")
                student = self._fetch_student_with_related_data(student_id)
            
            return student
        except Exception as e:
            logger.error(f"Error getting student {student_id}: {str(e)}", exc_info=True)
            # Fallback
            try:
                return self._fetch_student_with_related_data(student_id)
            except Exception as e2:
                logger.error(f"Fallback also failed for {student_id}: {str(e2)}", exc_info=True)
                return None

    def _fetch_student_with_related_data(self, student_id):
        """
        Obtiene un estudiante con sus datos relacionados mediante queries separadas
        """
        # Obtener estudiante base
        student_response = self._client.table("students").select("*").eq("id", student_id).maybe_single().execute()
        student = student_response.data
        
        if not student:
            return None
        
        # Obtener datos relacionados
        socio_response = self._client.table("socioeconomic_data").select("*").eq("student_id", student_id).execute()
        student["socioeconomic_data"] = socio_response.data
        
        attendance_response = self._client.table("attendance").select("*").eq("student_id", student_id).execute()
        student["attendance"] = attendance_response.data
        
        academic_response = self._client.table("academic_performance").select("*").eq("student_id", student_id).execute()
        student["academic_performance"] = academic_response.data
        
        return student

    def get_institutional_stats(self):
        """
        Obtiene estadísticas institucionales agregadas
        
        Returns:
            Diccionario con estadísticas
        """
        try:
            # Obtener todos los estudiantes con sus datos
            students = self.get_students(limit=1000)

            stats = {
                "total_students": len(students),
                "quintil_distribution": self._calculate_quintil_distribution(students),
                "risk_distribution": self._calculate_risk_distribution(students),
                "average_grade": self._calculate_average_grade(students),
            }

            return stats
        except Exception as e:
            logger.error(f"Error getting institutional stats: {str(e)}")
            return None

    def _calculate_quintil_distribution(self, students):
        """Calcula la distribución por quintil"""
        distribution = {"Q1-Q2": 0, "Q3": 0, "Q4-Q5": 0}

        for student in students:
            quintil_group = (student.get("quintil_agrupado") or "").lower()
            if "bajo" in quintil_group:
                distribution["Q1-Q2"] += 1
            elif "medio" in quintil_group:
                distribution["Q3"] += 1
            elif "alto" in quintil_group or "acomodado" in quintil_group:
                distribution["Q4-Q5"] += 1

        return distribution

    def _calculate_risk_distribution(self, students):
        """Calcula la distribución por nivel de riesgo"""
        from services.risk_calculator import risk_calculator
        
        distribution = {"Alto": 0, "Medio": 0, "Bajo": 0}

        for student in students:
            try:
                _, risk_level, _ = risk_calculator.calculate_risk_score(student)
                distribution[risk_level] = distribution.get(risk_level, 0) + 1
            except Exception as e:
                logger.debug(f"Error calculating risk for student {student.get('id')}: {e}")
                distribution["Bajo"] += 1

        return distribution

    def _calculate_average_grade(self, students):
        """Calcula el promedio general de calificaciones"""
        total_grade = 0
        count = 0

        for student in students:
            grade = student.get("promedio_general")
            if grade:
                total_grade += float(grade)
                count += 1

        return round(total_grade / count, 2) if count > 0 else 0.0

    def save_prediction(self, student_id, risk_score, risk_level, predicted_quintil):
        """
        Guarda una predicción de riesgo en la base de datos
        
        Args:
            student_id: ID del estudiante
            risk_score: Score de riesgo calculado
            risk_level: Nivel de riesgo (Alto/Medio/Bajo)
            predicted_quintil: Quintil predicho por el modelo
        """
        try:
            config = get_config()
            data = {
                "student_id": student_id,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "predicted_quintil": predicted_quintil,
                "model_version": config.MODEL_VERSION,
            }

            response = self._client.table("risk_predictions").insert(data).execute()
            logger.info(f"Prediction saved for student {student_id}")
            return response.data
        except Exception as e:
            logger.error(f"Error saving prediction for {student_id}: {str(e)}")
            return None


# Instancia global del cliente
supabase_client = SupabaseClient()

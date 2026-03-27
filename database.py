"""
Database Manager
Gestiona el almacenamiento de predicciones y resultados
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestor de base de datos SQLite para el bot"""

    def __init__(self, db_path: str = './data/predictions.db'):
        """Inicializar base de datos"""
        self.db_path = db_path
        self._create_tables()

    def _create_tables(self):
        """Crear tablas si no existen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabla de predicciones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    league TEXT NOT NULL,
                    home_team TEXT NOT NULL,
                    away_team TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    confidence INTEGER NOT NULL,
                    description TEXT,
                    reason TEXT,
                    created_at TEXT NOT NULL,
                    result TEXT,
                    is_correct BOOLEAN,
                    checked_at TEXT
                )
            ''')

            # Tabla de usuarios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    chat_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    subscribed BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL,
                    last_interaction TEXT
                )
            ''')

            # Tabla de estadísticas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    total_predictions INTEGER DEFAULT 0,
                    correct_predictions INTEGER DEFAULT 0,
                    accuracy REAL DEFAULT 0.0,
                    by_type TEXT
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("✓ Base de datos inicializada")

        except Exception as e:
            logger.error(f"Error creando tablas: {e}")

    def save_prediction(self, prediction: Dict) -> Optional[int]:
        """
        Guardar una predicción en la base de datos

        Args:
            prediction: Diccionario con datos de la predicción

        Returns:
            ID de la predicción guardada o None si falla
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO predictions
                (date, league, home_team, away_team, prediction_type,
                 confidence, description, reason, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                prediction.get('date', datetime.now().date().isoformat()),
                prediction.get('league', ''),
                prediction.get('home_team', ''),
                prediction.get('away_team', ''),
                prediction.get('type', ''),
                prediction.get('confidence', 0),
                prediction.get('description', ''),
                prediction.get('reason', ''),
                datetime.now().isoformat()
            ))

            prediction_id = cursor.lastrowid
            conn.commit()
            conn.close()

            logger.info(f"Predicción guardada con ID: {prediction_id}")
            return prediction_id

        except Exception as e:
            logger.error(f"Error guardando predicción: {e}")
            return None

    def save_user(self, chat_id: int, user_data: Dict):
        """Guardar o actualizar usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO users
                (chat_id, username, first_name, last_name, subscribed, created_at, last_interaction)
                VALUES (?, ?, ?, ?, ?, COALESCE(
                    (SELECT created_at FROM users WHERE chat_id = ?),
                    ?
                ), ?)
            ''', (
                chat_id,
                user_data.get('username', ''),
                user_data.get('first_name', ''),
                user_data.get('last_name', ''),
                user_data.get('subscribed', True),
                chat_id,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))

            conn.commit()
            conn.close()

            logger.info(f"Usuario {chat_id} guardado/actualizado")

        except Exception as e:
            logger.error(f"Error guardando usuario: {e}")

    def get_subscribed_users(self) -> List[int]:
        """Obtener lista de usuarios suscritos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT chat_id FROM users WHERE subscribed = 1')
            users = [row[0] for row in cursor.fetchall()]

            conn.close()
            return users

        except Exception as e:
            logger.error(f"Error obteniendo usuarios: {e}")
            return []

    def update_prediction_result(self, prediction_id: int, result: str, is_correct: bool):
        """Actualizar resultado de una predicción"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE predictions
                SET result = ?, is_correct = ?, checked_at = ?
                WHERE id = ?
            ''', (result, is_correct, datetime.now().isoformat(), prediction_id))

            conn.commit()
            conn.close()

            logger.info(f"Resultado actualizado para predicción {prediction_id}")

        except Exception as e:
            logger.error(f"Error actualizando resultado: {e}")

    def get_statistics(self, days: int = 30) -> Dict:
        """
        Obtener estadísticas de predicciones

        Args:
            days: Número de días hacia atrás

        Returns:
            Diccionario con estadísticas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Total de predicciones
            cursor.execute('''
                SELECT COUNT(*) FROM predictions
                WHERE date >= date('now', '-' || ? || ' days')
            ''', (days,))
            total = cursor.fetchone()[0]

            # Predicciones verificadas
            cursor.execute('''
                SELECT COUNT(*), SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END)
                FROM predictions
                WHERE date >= date('now', '-' || ? || ' days')
                AND is_correct IS NOT NULL
            ''', (days,))
            verified, correct = cursor.fetchone()

            # Accuracy por tipo
            cursor.execute('''
                SELECT
                    prediction_type,
                    COUNT(*) as total,
                    SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
                FROM predictions
                WHERE date >= date('now', '-' || ? || ' days')
                AND is_correct IS NOT NULL
                GROUP BY prediction_type
            ''', (days,))

            by_type = {}
            for row in cursor.fetchall():
                pred_type, total, correct = row
                accuracy = (correct / total * 100) if total > 0 else 0
                by_type[pred_type] = {
                    'total': total,
                    'correct': correct,
                    'accuracy': round(accuracy, 1)
                }

            conn.close()

            accuracy = (correct / verified * 100) if verified and verified > 0 else 0

            return {
                'total_predictions': total,
                'verified_predictions': verified or 0,
                'correct_predictions': correct or 0,
                'accuracy': round(accuracy, 1),
                'by_type': by_type,
                'period_days': days
            }

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                'total_predictions': 0,
                'verified_predictions': 0,
                'correct_predictions': 0,
                'accuracy': 0,
                'by_type': {},
                'period_days': days
            }

    def get_recent_predictions(self, limit: int = 10) -> List[Dict]:
        """Obtener predicciones recientes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, date, league, home_team, away_team,
                       prediction_type, confidence, description,
                       is_correct, result
                FROM predictions
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            predictions = []
            for row in cursor.fetchall():
                predictions.append({
                    'id': row[0],
                    'date': row[1],
                    'league': row[2],
                    'home_team': row[3],
                    'away_team': row[4],
                    'type': row[5],
                    'confidence': row[6],
                    'description': row[7],
                    'is_correct': row[8],
                    'result': row[9]
                })

            conn.close()
            return predictions

        except Exception as e:
            logger.error(f"Error obteniendo predicciones recientes: {e}")
            return []

    def toggle_subscription(self, chat_id: int) -> bool:
        """Activar/desactivar suscripción de un usuario"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Obtener estado actual
            cursor.execute('SELECT subscribed FROM users WHERE chat_id = ?', (chat_id,))
            result = cursor.fetchone()

            if result:
                new_state = not result[0]
                cursor.execute(
                    'UPDATE users SET subscribed = ? WHERE chat_id = ?',
                    (new_state, chat_id)
                )
                conn.commit()
                conn.close()
                return new_state
            else:
                conn.close()
                return False

        except Exception as e:
            logger.error(f"Error cambiando suscripción: {e}")
            return False


if __name__ == '__main__':
    # Test de la base de datos
    print("🗄️  Testing Database Manager...")

    db = DatabaseManager()

    # Test: Guardar predicción
    test_prediction = {
        'date': '2026-03-27',
        'league': 'Premier League',
        'home_team': 'Manchester City',
        'away_team': 'Liverpool',
        'type': 'Over 2.5 goles',
        'confidence': 85,
        'description': 'Se esperan más de 2.5 goles',
        'reason': 'Promedio de 3.2 goles en últimos partidos'
    }

    pred_id = db.save_prediction(test_prediction)
    print(f"✓ Predicción guardada con ID: {pred_id}")

    # Test: Obtener estadísticas
    stats = db.get_statistics(30)
    print(f"✓ Estadísticas: {stats}")

    # Test: Predicciones recientes
    recent = db.get_recent_predictions(5)
    print(f"✓ Predicciones recientes: {len(recent)}")

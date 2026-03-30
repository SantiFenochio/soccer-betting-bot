"""
Database Manager
Sistema de base de datos SQLite para predicciones y suscripciones
"""

import sqlite3
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Gestor de base de datos SQLite para el bot"""

    def __init__(self):
        """Inicializar conexión a base de datos"""
        # Obtener path de .env o usar default
        db_path = os.getenv('DB_PATH', './data/predictions.db')

        # Crear directorio si no existe
        db_dir = os.path.dirname(db_path)
        if db_dir:
            Path(db_dir).mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self._init_db()
        logger.info(f"Database initialized at {self.db_path}")

    def _init_db(self):
        """Crear tablas si no existen"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Tabla de predicciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                league TEXT,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                confidence REAL,
                description TEXT,
                verified INTEGER DEFAULT 0,
                correct INTEGER,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # Tabla de suscripciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                chat_id INTEGER PRIMARY KEY,
                subscribed INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        conn.commit()
        conn.close()

    def save_prediction(self, data: dict) -> bool:
        """
        Guardar una predicción en la base de datos

        Args:
            data: Dict con date, league, home_team, away_team,
                  prediction_type, confidence, description

        Returns:
            bool: True si se guardó exitosamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO predictions
                (date, league, home_team, away_team, prediction_type, confidence, description)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('date', datetime.now().date().isoformat()),
                data.get('league', 'Unknown'),
                data.get('home_team', ''),
                data.get('away_team', ''),
                data.get('prediction_type', ''),
                data.get('confidence', 0),
                data.get('description', '')
            ))

            conn.commit()
            conn.close()

            logger.debug(f"Prediction saved: {data.get('home_team')} vs {data.get('away_team')}")
            return True

        except Exception as e:
            logger.error(f"Error saving prediction: {e}")
            return False

    def get_statistics(self, days: int = 30) -> Dict:
        """
        Obtener estadísticas de predicciones

        Args:
            days: Número de días atrás para calcular stats

        Returns:
            Dict con total_predictions, verified_predictions,
            correct_predictions, accuracy, by_type
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calcular fecha límite
            date_limit = (datetime.now() - timedelta(days=days)).date().isoformat()

            # Total de predicciones
            cursor.execute('''
                SELECT COUNT(*) FROM predictions
                WHERE date >= ?
            ''', (date_limit,))
            total_predictions = cursor.fetchone()[0]

            # Predicciones verificadas
            cursor.execute('''
                SELECT COUNT(*) FROM predictions
                WHERE date >= ? AND verified = 1
            ''', (date_limit,))
            verified_predictions = cursor.fetchone()[0]

            # Predicciones correctas
            cursor.execute('''
                SELECT COUNT(*) FROM predictions
                WHERE date >= ? AND verified = 1 AND correct = 1
            ''', (date_limit,))
            correct_predictions = cursor.fetchone()[0]

            # Calcular accuracy
            accuracy = 0
            if verified_predictions > 0:
                accuracy = round((correct_predictions / verified_predictions) * 100, 1)

            # Estadísticas por tipo
            by_type = {}
            cursor.execute('''
                SELECT
                    prediction_type,
                    COUNT(*) as total,
                    SUM(CASE WHEN verified = 1 AND correct = 1 THEN 1 ELSE 0 END) as correct
                FROM predictions
                WHERE date >= ? AND verified = 1
                GROUP BY prediction_type
            ''', (date_limit,))

            for row in cursor.fetchall():
                pred_type, total, correct = row
                type_accuracy = 0
                if total > 0:
                    type_accuracy = round((correct / total) * 100, 1)

                by_type[pred_type] = {
                    'total': total,
                    'correct': correct,
                    'accuracy': type_accuracy
                }

            conn.close()

            return {
                'total_predictions': total_predictions,
                'verified_predictions': verified_predictions,
                'correct_predictions': correct_predictions,
                'accuracy': accuracy,
                'by_type': by_type
            }

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                'total_predictions': 0,
                'verified_predictions': 0,
                'correct_predictions': 0,
                'accuracy': 0,
                'by_type': {}
            }

    def toggle_subscription(self, chat_id: int) -> bool:
        """
        Activar/desactivar suscripción de un chat

        Args:
            chat_id: ID del chat de Telegram

        Returns:
            bool: Nuevo estado de la suscripción (True = activo)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verificar si existe
            cursor.execute('''
                SELECT subscribed FROM subscriptions WHERE chat_id = ?
            ''', (chat_id,))

            result = cursor.fetchone()

            if result:
                # Toggle estado existente
                new_state = 0 if result[0] == 1 else 1
                cursor.execute('''
                    UPDATE subscriptions
                    SET subscribed = ?, updated_at = datetime('now')
                    WHERE chat_id = ?
                ''', (new_state, chat_id))
            else:
                # Crear nueva suscripción (por default activa)
                new_state = 1
                cursor.execute('''
                    INSERT INTO subscriptions (chat_id, subscribed)
                    VALUES (?, ?)
                ''', (chat_id, new_state))

            conn.commit()
            conn.close()

            logger.info(f"Subscription toggled for {chat_id}: {bool(new_state)}")
            return bool(new_state)

        except Exception as e:
            logger.error(f"Error toggling subscription: {e}")
            return False

    def get_subscribed_chats(self) -> List[int]:
        """
        Obtener lista de chat_ids suscritos

        Returns:
            List[int]: Lista de chat IDs activos
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT chat_id FROM subscriptions
                WHERE subscribed = 1
            ''')

            chat_ids = [row[0] for row in cursor.fetchall()]
            conn.close()

            logger.debug(f"Found {len(chat_ids)} subscribed chats")
            return chat_ids

        except Exception as e:
            logger.error(f"Error getting subscribed chats: {e}")
            return []

    def verify_prediction(self, prediction_id: int, correct: bool) -> bool:
        """
        Marcar una predicción como verificada

        Args:
            prediction_id: ID de la predicción
            correct: Si fue correcta o no

        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE predictions
                SET verified = 1, correct = ?
                WHERE id = ?
            ''', (1 if correct else 0, prediction_id))

            conn.commit()
            conn.close()

            logger.info(f"Prediction {prediction_id} verified: {correct}")
            return True

        except Exception as e:
            logger.error(f"Error verifying prediction: {e}")
            return False

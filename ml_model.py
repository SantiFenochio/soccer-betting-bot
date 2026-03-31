"""
ML Prediction Model
Sistema de Machine Learning con XGBoost para predicciones de fútbol
"""

import os
import logging
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Intentar importar dependencias ML
try:
    import xgboost as xgb
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError as e:
    logger.warning(f"ML dependencies not available: {e}")
    ML_AVAILABLE = False


class MLPredictor:
    """Predictor de partidos usando Machine Learning (XGBoost)"""

    def __init__(self):
        """Inicializar predictor ML"""
        self.model_result = None  # Modelo para resultado (1X2)
        self.model_goals = None   # Modelo para total de goles
        self.model_btts = None    # Modelo para BTTS
        self.scaler = StandardScaler()

        # Path para guardar modelos
        self.models_dir = Path(__file__).parent / 'models'
        self.models_dir.mkdir(exist_ok=True)

        # Paths de modelos específicos
        self.result_model_path = self.models_dir / 'xgb_result_model.pkl'
        self.goals_model_path = self.models_dir / 'xgb_goals_model.pkl'
        self.btts_model_path = self.models_dir / 'xgb_btts_model.pkl'
        self.scaler_path = self.models_dir / 'scaler.pkl'

        # Cargar modelos si existen
        self._load_models()

        logger.info("MLPredictor initialized")

    def _load_models(self):
        """Cargar modelos entrenados desde disco"""
        try:
            if self.result_model_path.exists():
                self.model_result = joblib.load(self.result_model_path)
                logger.info("✓ Modelo de resultado cargado")

            if self.goals_model_path.exists():
                self.model_goals = joblib.load(self.goals_model_path)
                logger.info("✓ Modelo de goles cargado")

            if self.btts_model_path.exists():
                self.model_btts = joblib.load(self.btts_model_path)
                logger.info("✓ Modelo BTTS cargado")

            if self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
                logger.info("✓ Scaler cargado")

        except Exception as e:
            logger.error(f"Error cargando modelos: {e}")

    def train_model(self, leagues: List[str] = None, seasons: int = 4, use_simple: bool = False):
        """
        Entrenar modelos ML con datos históricos de soccerdata

        Args:
            leagues: Lista de ligas a usar (None = todas las soportadas)
            seasons: Número de temporadas a usar (últimas N temporadas)
            use_simple: Si True, usa método simplificado con datos sintéticos
        """
        if not ML_AVAILABLE:
            logger.error("ML dependencies not installed. Run: pip install xgboost scikit-learn")
            return False

        # Si use_simple=True o falla el método normal, usar método simplificado
        if use_simple:
            logger.info("🤖 Usando método de entrenamiento simplificado con datos sintéticos...")
            return self.train_model_simple()

        logger.info("🤖 Iniciando entrenamiento de modelos ML...")

        try:
            import soccerdata as sd

            # Ligas a usar (códigos FBref)
            if leagues is None:
                fbref_leagues = ['ENG-Premier League', 'ESP-La Liga', 'GER-Bundesliga',
                                'ITA-Serie A', 'FRA-Ligue 1']
            else:
                fbref_leagues = leagues

            # Obtener datos históricos con FBref
            logger.info(f"Descargando datos de {len(fbref_leagues)} ligas, últimas {seasons} temporadas...")

            try:
                fbref = sd.FBref(leagues=fbref_leagues, no_cache=False)
            except Exception as e:
                logger.warning(f"Error inicializando FBref: {e}")
                logger.info("Intentando método simplificado...")
                return self.train_model_simple()

            # Obtener temporadas (formato FBref: 2023-2024)
            current_year = datetime.now().year
            seasons_list = [f"{year}-{year+1}" for year in range(current_year - seasons, current_year)]

            all_data = []

            for season in seasons_list:
                for league in fbref_leagues:
                    try:
                        logger.info(f"Procesando {league} - {season}...")
                        # Usar read_schedule para obtener resultados
                        matches = fbref.read_schedule(league=league, season=season)

                        if not matches.empty:
                            all_data.append(matches)
                            logger.info(f"  ✓ {len(matches)} partidos obtenidos")
                    except Exception as e:
                        logger.warning(f"  ✗ Error en {league} {season}: {e}")
                        continue

            if not all_data:
                logger.warning("No se pudieron obtener datos de FBref, usando método simplificado...")
                return self.train_model_simple()

            # Combinar todos los datos
            df = pd.concat(all_data, ignore_index=True)
            logger.info(f"✓ Total: {len(df)} partidos para entrenamiento")

            # Extraer features y targets
            X, y_result, y_goals, y_btts = self._prepare_training_data(df)

            if X is None or len(X) == 0:
                logger.error("No se pudieron preparar datos de entrenamiento")
                return False

            logger.info(f"✓ Features extraídas: {X.shape[1]} features, {len(X)} muestras")

            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)

            # Entrenar modelo de resultado (1X2)
            logger.info("Entrenando modelo de resultado...")
            self.model_result = self._train_result_model(X_scaled, y_result)

            # Entrenar modelo de goles
            logger.info("Entrenando modelo de goles...")
            self.model_goals = self._train_goals_model(X_scaled, y_goals)

            # Entrenar modelo de BTTS
            logger.info("Entrenando modelo BTTS...")
            self.model_btts = self._train_btts_model(X_scaled, y_btts)

            # Guardar modelos
            self._save_models()

            logger.info("✅ Entrenamiento completado exitosamente")
            return True

        except Exception as e:
            logger.error(f"Error en entrenamiento de modelos: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _prepare_training_data(self, df: pd.DataFrame) -> Tuple:
        """
        Preparar datos de entrenamiento: extraer features y targets

        Args:
            df: DataFrame con datos de partidos

        Returns:
            Tuple (X, y_result, y_goals, y_btts)
        """
        try:
            features_list = []
            targets_result = []
            targets_goals = []
            targets_btts = []

            # Procesar cada partido
            for idx, row in df.iterrows():
                try:
                    # Extraer features básicas del row
                    features = self._extract_features_from_row(row, df)

                    if features is None:
                        continue

                    # Target: resultado (1=home win, 0=draw, -1=away win)
                    home_score = row.get('scored', 0)
                    away_score = row.get('missed', 0)

                    if home_score > away_score:
                        result = 1  # Home win
                    elif home_score < away_score:
                        result = -1  # Away win
                    else:
                        result = 0  # Draw

                    # Target: total goles
                    total_goals = home_score + away_score

                    # Target: BTTS (ambos anotan)
                    btts = 1 if (home_score > 0 and away_score > 0) else 0

                    features_list.append(features)
                    targets_result.append(result)
                    targets_goals.append(total_goals)
                    targets_btts.append(btts)

                except Exception as e:
                    logger.debug(f"Error procesando fila {idx}: {e}")
                    continue

            if not features_list:
                return None, None, None, None

            X = np.array(features_list)
            y_result = np.array(targets_result)
            y_goals = np.array(targets_goals)
            y_btts = np.array(targets_btts)

            return X, y_result, y_goals, y_btts

        except Exception as e:
            logger.error(f"Error preparando datos: {e}")
            return None, None, None, None

    def _extract_features_from_row(self, row: pd.Series, full_df: pd.DataFrame) -> Optional[np.ndarray]:
        """
        Extraer features de una fila (partido)

        Features (15+):
        1. xG home
        2. xG away
        3. xG differential (home - away)
        4. xG against home
        5. xG against away
        6. Goals scored home (avg últimos 5)
        7. Goals conceded home (avg últimos 5)
        8. Goals scored away (avg últimos 5)
        9. Goals conceded away (avg últimos 5)
        10. Home advantage (1)
        11. Form home (puntos últimos 5)
        12. Form away (puntos últimos 5)
        13. Momentum home (diferencia primeros vs últimos 3)
        14. Momentum away
        15. League strength (encoded)
        """
        try:
            features = []

            # Features básicas de xG
            xg_home = row.get('xG', 1.5)
            xg_away = row.get('xGA', 1.5)  # xGA del equipo local es xG del visitante

            features.append(xg_home)  # 1
            features.append(xg_away)  # 2
            features.append(xg_home - xg_away)  # 3 - xG differential

            # xG defensivo
            xga_home = row.get('xGA', 1.2)
            xga_away = row.get('xG', 1.2)  # Aproximación

            features.append(xga_home)  # 4
            features.append(xga_away)  # 5

            # Goles (usar promedios o valores actuales)
            goals_scored_home = row.get('scored', 1.5)
            goals_conceded_home = row.get('missed', 1.2)

            features.append(goals_scored_home)  # 6
            features.append(goals_conceded_home)  # 7
            features.append(goals_scored_home)  # 8 - simplificación
            features.append(goals_conceded_home)  # 9 - simplificación

            # Home advantage
            features.append(1.0)  # 10 - siempre 1 para local

            # Form (aproximación con xG)
            form_home = min(xg_home * 3, 15)  # Escala a puntos
            form_away = min(xg_away * 3, 15)

            features.append(form_home)  # 11
            features.append(form_away)  # 12

            # Momentum (diferencia entre performance)
            momentum_home = xg_home - xga_home
            momentum_away = xg_away - xga_away

            features.append(momentum_home)  # 13
            features.append(momentum_away)  # 14

            # League strength (dummy encoding)
            league = row.get('league', 'Unknown')
            league_strength = {'EPL': 5, 'La Liga': 5, 'Bundesliga': 4,
                             'Serie A': 4, 'Ligue 1': 3}.get(league, 3)

            features.append(league_strength)  # 15

            return np.array(features, dtype=np.float32)

        except Exception as e:
            logger.debug(f"Error extrayendo features: {e}")
            return None

    def _train_result_model(self, X, y) -> xgb.XGBClassifier:
        """Entrenar modelo de resultado (clasificación 1X2)"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.05,
            random_state=42,
            eval_metric='mlogloss'
        )

        model.fit(X_train, y_train)

        # Evaluar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"  ✓ Accuracy resultado: {accuracy:.2%}")

        return model

    def _train_goals_model(self, X, y) -> xgb.XGBRegressor:
        """Entrenar modelo de total de goles (regresión)"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = xgb.XGBRegressor(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            random_state=42
        )

        model.fit(X_train, y_train)

        # Evaluar
        y_pred = model.predict(X_test)
        mae = np.mean(np.abs(y_test - y_pred))
        logger.info(f"  ✓ MAE goles: {mae:.2f}")

        return model

    def _train_btts_model(self, X, y) -> xgb.XGBClassifier:
        """Entrenar modelo de BTTS (clasificación binaria)"""
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = xgb.XGBClassifier(
            n_estimators=150,
            max_depth=5,
            learning_rate=0.05,
            random_state=42
        )

        model.fit(X_train, y_train)

        # Evaluar
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"  ✓ Accuracy BTTS: {accuracy:.2%}")

        return model

    def _save_models(self):
        """Guardar modelos entrenados"""
        try:
            if self.model_result:
                joblib.dump(self.model_result, self.result_model_path)
                logger.info(f"✓ Modelo de resultado guardado: {self.result_model_path}")

            if self.model_goals:
                joblib.dump(self.model_goals, self.goals_model_path)
                logger.info(f"✓ Modelo de goles guardado: {self.goals_model_path}")

            if self.model_btts:
                joblib.dump(self.model_btts, self.btts_model_path)
                logger.info(f"✓ Modelo BTTS guardado: {self.btts_model_path}")

            joblib.dump(self.scaler, self.scaler_path)
            logger.info(f"✓ Scaler guardado: {self.scaler_path}")

        except Exception as e:
            logger.error(f"Error guardando modelos: {e}")

    def predict_match(self, home_team: str, away_team: str, league: str = None,
                     xg_data: Dict = None, current_odds: Dict = None) -> Dict:
        """
        Predecir resultado de un partido usando ML

        Args:
            home_team: Equipo local
            away_team: Equipo visitante
            league: Liga del partido
            xg_data: Datos xG del partido (si están disponibles)
            current_odds: Odds actuales (opcional)

        Returns:
            Dict con predicciones ML y confidence score
        """
        # Verificar que los modelos estén cargados
        if self.model_result is None:
            logger.warning("Modelo ML no disponible, usando fallback")
            return self._fallback_prediction()

        try:
            # Extraer features del partido
            features = self._extract_match_features(home_team, away_team, league, xg_data, current_odds)

            if features is None:
                return self._fallback_prediction()

            # Normalizar
            features_scaled = self.scaler.transform([features])

            # Predicción de resultado (probabilidades)
            result_probs = self.model_result.predict_proba(features_scaled)[0]

            # Mapear probabilidades
            # Clases: 0=away win, 1=draw, 2=home win
            classes = self.model_result.classes_

            prob_away = result_probs[list(classes).index(0)] if 0 in classes else 0.33
            prob_draw = result_probs[list(classes).index(1)] if 1 in classes else 0.33
            prob_home = result_probs[list(classes).index(2)] if 2 in classes else 0.33

            # Predicción de goles
            total_goals_pred = self.model_goals.predict(features_scaled)[0]
            over_25_prob = 1 / (1 + np.exp(-(total_goals_pred - 2.5)))  # Sigmoid

            # Predicción BTTS
            btts_probs = self.model_btts.predict_proba(features_scaled)[0]
            btts_yes_prob = btts_probs[1] if len(btts_probs) > 1 else 0.5

            # Calcular confidence general (0-100)
            # Basado en la confianza de la predicción más fuerte
            max_prob = max(prob_home, prob_draw, prob_away)
            ml_confidence = int(min(max_prob * 100, 95))

            # Feature importance (top 5)
            feature_importance = self._get_feature_importance()

            return {
                'ml_home_win_prob': round(prob_home * 100, 1),
                'ml_draw_prob': round(prob_draw * 100, 1),
                'ml_away_win_prob': round(prob_away * 100, 1),
                'ml_over_2_5_prob': round(over_25_prob * 100, 1),
                'ml_btts_yes_prob': round(btts_yes_prob * 100, 1),
                'ml_confidence': ml_confidence,
                'ml_predicted_goals': round(total_goals_pred, 2),
                'feature_importance': feature_importance,
                'model_available': True
            }

        except Exception as e:
            logger.error(f"Error en predicción ML: {e}")
            return self._fallback_prediction()

    def _extract_match_features(self, home_team: str, away_team: str, league: str,
                                xg_data: Dict = None, current_odds: Dict = None) -> Optional[np.ndarray]:
        """Extraer features de un partido específico para predicción"""
        try:
            features = []

            # Si tenemos xG data real, usarlo
            if xg_data and 'home_stats' in xg_data and 'away_stats' in xg_data:
                home_stats = xg_data['home_stats']
                away_stats = xg_data['away_stats']

                xg_home = home_stats.get('xg_for_avg', 1.5)
                xg_away = away_stats.get('xg_for_avg', 1.5)
                xga_home = home_stats.get('xg_against_avg', 1.2)
                xga_away = away_stats.get('xg_against_avg', 1.2)

                goals_home = home_stats.get('goals_scored_avg', 1.5)
                goals_away = away_stats.get('goals_scored_avg', 1.5)
                conceded_home = home_stats.get('goals_conceded_avg', 1.2)
                conceded_away = away_stats.get('goals_conceded_avg', 1.2)
            else:
                # Fallback a valores por defecto
                xg_home = xg_away = 1.5
                xga_home = xga_away = 1.2
                goals_home = goals_away = 1.5
                conceded_home = conceded_away = 1.2

            # 15 features (mismo orden que en entrenamiento)
            features.append(xg_home)
            features.append(xg_away)
            features.append(xg_home - xg_away)
            features.append(xga_home)
            features.append(xga_away)
            features.append(goals_home)
            features.append(conceded_home)
            features.append(goals_away)
            features.append(conceded_away)
            features.append(1.0)  # Home advantage

            # Form
            form_home = min(xg_home * 3, 15)
            form_away = min(xg_away * 3, 15)
            features.append(form_home)
            features.append(form_away)

            # Momentum
            features.append(xg_home - xga_home)
            features.append(xg_away - xga_away)

            # League strength
            league_map = {'EPL': 5, 'ENG': 5, 'ESP': 5, 'La Liga': 5,
                         'GER': 4, 'Bundesliga': 4, 'ITA': 4, 'Serie A': 4,
                         'FRA': 3, 'Ligue 1': 3}
            league_strength = league_map.get(league, 3)
            features.append(league_strength)

            return np.array(features, dtype=np.float32)

        except Exception as e:
            logger.error(f"Error extrayendo features de partido: {e}")
            return None

    def _get_feature_importance(self) -> Dict:
        """Obtener top 5 features más importantes"""
        try:
            if self.model_result is None:
                return {}

            feature_names = [
                'xG_home', 'xG_away', 'xG_diff', 'xGA_home', 'xGA_away',
                'goals_home', 'conceded_home', 'goals_away', 'conceded_away',
                'home_adv', 'form_home', 'form_away', 'momentum_home',
                'momentum_away', 'league_strength'
            ]

            importances = self.model_result.feature_importances_

            # Top 5
            top_indices = np.argsort(importances)[-5:][::-1]

            top_features = {}
            for idx in top_indices:
                if idx < len(feature_names):
                    top_features[feature_names[idx]] = round(float(importances[idx]), 3)

            return top_features

        except Exception as e:
            logger.debug(f"Error obteniendo feature importance: {e}")
            return {}

    def _fallback_prediction(self) -> Dict:
        """Predicción fallback cuando ML no está disponible"""
        return {
            'ml_home_win_prob': 40.0,
            'ml_draw_prob': 30.0,
            'ml_away_win_prob': 30.0,
            'ml_over_2_5_prob': 50.0,
            'ml_btts_yes_prob': 50.0,
            'ml_confidence': 50,
            'ml_predicted_goals': 2.5,
            'feature_importance': {},
            'model_available': False
        }

    def is_model_trained(self) -> bool:
        """Verificar si hay modelos entrenados disponibles"""
        return self.model_result is not None

    def train_model_simple(self, n_samples: int = 2000):
        """
        Entrenar modelos con datos sintéticos realistas

        Este método genera datos sintéticos basados en estadísticas reales
        de fútbol para entrenar los modelos cuando no hay acceso a datos históricos.

        Args:
            n_samples: Número de partidos sintéticos a generar (default: 2000)

        Returns:
            bool: True si entrenamiento exitoso
        """
        if not ML_AVAILABLE:
            logger.error("ML dependencies not installed")
            return False

        logger.info(f"🤖 Generando {n_samples} partidos sintéticos para entrenamiento...")

        try:
            np.random.seed(42)  # Para reproducibilidad

            features_list = []
            targets_result = []
            targets_goals = []
            targets_btts = []

            for i in range(n_samples):
                # Generar features realistas
                # xG home/away (distribución normal alrededor de 1.5)
                xg_home = max(0.2, np.random.normal(1.5, 0.6))
                xg_away = max(0.2, np.random.normal(1.3, 0.5))  # Away ligeramente menor

                xga_home = max(0.2, np.random.normal(1.2, 0.5))
                xga_away = max(0.2, np.random.normal(1.4, 0.6))

                # Goals basados en xG con algo de ruido
                goals_home = max(0, xg_home + np.random.normal(0, 0.3))
                goals_away = max(0, xg_away + np.random.normal(0, 0.3))

                conceded_home = max(0, xga_home + np.random.normal(0, 0.3))
                conceded_away = max(0, xga_away + np.random.normal(0, 0.3))

                # Form (0-15 puntos)
                form_home = np.random.uniform(5, 15)
                form_away = np.random.uniform(5, 15)

                # Momentum
                momentum_home = xg_home - xga_home
                momentum_away = xg_away - xga_away

                # League strength (3-5)
                league_strength = np.random.choice([3, 4, 5])

                # Construir feature vector
                features = [
                    xg_home, xg_away, xg_home - xg_away,
                    xga_home, xga_away,
                    goals_home, conceded_home, goals_away, conceded_away,
                    1.0,  # Home advantage
                    form_home, form_away,
                    momentum_home, momentum_away,
                    league_strength
                ]

                # Generar targets basados en xG con probabilidades realistas
                xg_diff = xg_home - xg_away

                # Resultado (con ventaja de local)
                # Usar sigmoid para mantener probabilidades en rango válido
                home_base = 0.45  # Ventaja de local incluida
                away_base = 0.30
                draw_base = 0.25

                # Ajustar según xG differential
                home_prob = max(0.1, min(0.8, home_base + (xg_diff * 0.12)))
                away_prob = max(0.1, min(0.8, away_base - (xg_diff * 0.12)))
                draw_prob = max(0.1, 1.0 - home_prob - away_prob)

                # Normalizar para asegurar que suman 1
                total = home_prob + draw_prob + away_prob
                home_prob = max(0.01, home_prob / total)
                draw_prob = max(0.01, draw_prob / total)
                away_prob = max(0.01, away_prob / total)

                # Re-normalizar después de aplicar min
                total = home_prob + draw_prob + away_prob
                home_prob /= total
                draw_prob /= total
                away_prob /= total

                # result: 2=home win, 1=draw, 0=away win (para XGBoost)
                result_raw = np.random.choice([2, 1, 0], p=[home_prob, draw_prob, away_prob])

                # Total goles (Poisson aproximado)
                total_goals = int(np.random.poisson(xg_home + xg_away))

                # BTTS (probabilidad basada en xG de ambos)
                btts_prob = min(0.9, (xg_home * xg_away) / 4)  # Heurística
                btts = 1 if np.random.random() < btts_prob else 0

                features_list.append(features)
                targets_result.append(result_raw)
                targets_goals.append(total_goals)
                targets_btts.append(btts)

            # Convertir a numpy arrays
            X = np.array(features_list, dtype=np.float32)
            y_result = np.array(targets_result)
            y_goals = np.array(targets_goals)
            y_btts = np.array(targets_btts)

            logger.info(f"✓ {n_samples} partidos sintéticos generados")
            logger.info(f"  - Features: {X.shape[1]} dimensiones")
            logger.info(f"  - Resultados: {len(y_result)} etiquetas")

            # Normalizar features
            X_scaled = self.scaler.fit_transform(X)

            # Entrenar modelos
            logger.info("Entrenando modelo de resultado...")
            self.model_result = self._train_result_model(X_scaled, y_result)

            logger.info("Entrenando modelo de goles...")
            self.model_goals = self._train_goals_model(X_scaled, y_goals)

            logger.info("Entrenando modelo BTTS...")
            self.model_btts = self._train_btts_model(X_scaled, y_btts)

            # Guardar modelos
            self._save_models()

            logger.info("✅ Entrenamiento simplificado completado exitosamente")
            logger.info("⚠️  NOTA: Modelos entrenados con datos sintéticos. Considera reentrenar con datos reales cuando estén disponibles.")

            return True

        except Exception as e:
            logger.error(f"Error en entrenamiento simplificado: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == '__main__':
    import sys

    # Test del modelo ML
    print("🤖 ML Predictor - Soccer Betting Bot\n")

    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        # Modo entrenamiento
        print("🤖 Iniciando entrenamiento de modelos ML...")
        print("="*60)

        predictor = MLPredictor()

        # Preguntar qué método usar
        print("\nMétodos de entrenamiento disponibles:")
        print("1. Simplificado (datos sintéticos) - Rápido, 2-3 minutos")
        print("2. Completo (datos reales FBref) - Lento, 15-30 minutos")
        print("\nSi falla opción 2, se usará automáticamente opción 1.\n")

        choice = input("Elige método (1 o 2) [default: 1]: ").strip() or "1"

        if choice == "1":
            success = predictor.train_model(use_simple=True)
        else:
            print("\n⚠️  ADVERTENCIA: El método completo descarga datos históricos.")
            print("Puede tomar 15-30 minutos y requerir conexión a internet.\n")
            confirm = input("¿Continuar? (s/n): ").strip().lower()

            if confirm == 's' or confirm == 'si':
                success = predictor.train_model(use_simple=False)
            else:
                print("Cancelado. Usando método simplificado...")
                success = predictor.train_model(use_simple=True)

        if success:
            print("\n" + "="*60)
            print("✅ ¡ENTRENAMIENTO COMPLETADO EXITOSAMENTE!")
            print("="*60)
            print("\nLos modelos están listos para usar en el bot.")
            print("\nPrueba el bot con:")
            print("  python main.py")
            print("\nY luego en Telegram:")
            print("  /fijini")
            print("  /partido Real Madrid vs Barcelona")
        else:
            print("\n" + "="*60)
            print("❌ ERROR EN ENTRENAMIENTO")
            print("="*60)
            print("\nIntenta el método simplificado:")
            print("  python ml_model.py train")
            print("  (y elige opción 1)")

    else:
        # Modo test
        predictor = MLPredictor()

        if not predictor.is_model_trained():
            print("⚠️  No hay modelos entrenados.\n")
            print("Para entrenar:")
            print("  python ml_model.py train\n")
            print("O desde Python:")
            print("  from ml_model import MLPredictor")
            print("  p = MLPredictor()")
            print("  p.train_model(use_simple=True)  # Método rápido")
        else:
            print("✅ Modelos cargados exitosamente\n")

            # Test de predicción
            print("="*60)
            print("Test: Real Madrid vs Barcelona")
            print("="*60)

            result = predictor.predict_match('Real Madrid', 'Barcelona', 'ESP')

            print(f"\n🏠 Victoria local: {result['ml_home_win_prob']}%")
            print(f"➖ Empate: {result['ml_draw_prob']}%")
            print(f"🚗 Victoria visitante: {result['ml_away_win_prob']}%")
            print(f"\n⚽ Over 2.5 goles: {result['ml_over_2_5_prob']}%")
            print(f"🎯 BTTS: {result['ml_btts_yes_prob']}%")
            print(f"\n📊 Confidence: {result['ml_confidence']}/100")
            print(f"🔮 Goles predichos: {result['ml_predicted_goals']}")

            if result['feature_importance']:
                print(f"\n🔍 Top features:")
                for feat, imp in result['feature_importance'].items():
                    print(f"  - {feat}: {imp}")

            print("\n" + "="*60)

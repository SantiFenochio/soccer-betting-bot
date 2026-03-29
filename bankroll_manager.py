"""
Bankroll Management System
Sistema profesional de gestión de bankroll y tracking de apuestas
"""

import sqlite3
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class BankrollManager:
    """Gestor de bankroll y apuestas"""

    def __init__(self, db_path: str = './data/bankroll.db'):
        """
        Inicializar gestor de bankroll

        Args:
            db_path: Ruta a la base de datos
        """
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """Inicializar tablas de base de datos"""
        try:
            # Crear directorio si no existe
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Tabla de usuarios y sus bankrolls
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_bankrolls (
                    user_id INTEGER PRIMARY KEY,
                    initial_bankroll REAL NOT NULL,
                    current_bankroll REAL NOT NULL,
                    currency TEXT DEFAULT 'USD',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Tabla de apuestas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    match_description TEXT NOT NULL,
                    bet_type TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    stake REAL NOT NULL,
                    odds REAL NOT NULL,
                    confidence INTEGER,
                    status TEXT DEFAULT 'pending',
                    result TEXT,
                    profit_loss REAL DEFAULT 0,
                    placed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    settled_at TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES user_bankrolls(user_id)
                )
            ''')

            # Índices para mejor performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bets_user_id ON bets(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bets_status ON bets(status)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_bets_placed_at ON bets(placed_at)
            ''')

            conn.commit()
            conn.close()

            logger.info("✓ Base de datos de bankroll inicializada")

        except Exception as e:
            logger.error(f"Error inicializando DB bankroll: {e}")

    def set_bankroll(self, user_id: int, amount: float, currency: str = 'USD') -> bool:
        """
        Configurar bankroll inicial de un usuario

        Args:
            user_id: ID del usuario
            amount: Monto inicial
            currency: Moneda (USD, EUR, etc.)

        Returns:
            True si se configuró correctamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Verificar si ya existe
            cursor.execute('SELECT user_id FROM user_bankrolls WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()

            if exists:
                # Actualizar
                cursor.execute('''
                    UPDATE user_bankrolls
                    SET current_bankroll = ?,
                        currency = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (amount, currency, user_id))
            else:
                # Crear nuevo
                cursor.execute('''
                    INSERT INTO user_bankrolls (user_id, initial_bankroll, current_bankroll, currency)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, amount, amount, currency))

            conn.commit()
            conn.close()

            logger.info(f"✓ Bankroll configurado para user {user_id}: {amount} {currency}")
            return True

        except Exception as e:
            logger.error(f"Error configurando bankroll: {e}")
            return False

    def get_bankroll(self, user_id: int) -> Optional[Dict]:
        """
        Obtener bankroll de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Diccionario con información del bankroll
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM user_bankrolls WHERE user_id = ?
            ''', (user_id,))

            row = cursor.fetchone()
            conn.close()

            if row:
                return dict(row)
            return None

        except Exception as e:
            logger.error(f"Error obteniendo bankroll: {e}")
            return None

    def register_bet(self, user_id: int, match: str, bet_type: str,
                    prediction: str, stake: float, odds: float,
                    confidence: int = None, notes: str = None) -> Optional[int]:
        """
        Registrar una nueva apuesta

        Args:
            user_id: ID del usuario
            match: Descripción del partido
            bet_type: Tipo de apuesta (Resultado, Goles, BTTS, etc.)
            prediction: Predicción específica
            stake: Monto apostado
            odds: Cuota
            confidence: Nivel de confianza (0-100)
            notes: Notas adicionales

        Returns:
            ID de la apuesta o None si falla
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO bets (user_id, match_description, bet_type, prediction,
                                stake, odds, confidence, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, match, bet_type, prediction, stake, odds, confidence, notes))

            bet_id = cursor.lastrowid

            # Actualizar bankroll (restar stake)
            cursor.execute('''
                UPDATE user_bankrolls
                SET current_bankroll = current_bankroll - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (stake, user_id))

            conn.commit()
            conn.close()

            logger.info(f"✓ Apuesta registrada: {bet_id} para user {user_id}")
            return bet_id

        except Exception as e:
            logger.error(f"Error registrando apuesta: {e}")
            return None

    def settle_bet(self, bet_id: int, result: str) -> bool:
        """
        Liquidar una apuesta (marcar como ganada/perdida)

        Args:
            bet_id: ID de la apuesta
            result: 'won', 'lost', 'void', 'push'

        Returns:
            True si se liquidó correctamente
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Obtener datos de la apuesta
            cursor.execute('''
                SELECT user_id, stake, odds, status
                FROM bets WHERE id = ?
            ''', (bet_id,))

            bet_data = cursor.fetchone()

            if not bet_data:
                logger.error(f"Apuesta {bet_id} no encontrada")
                return False

            user_id, stake, odds, status = bet_data

            if status != 'pending':
                logger.warning(f"Apuesta {bet_id} ya fue liquidada")
                return False

            # Calcular profit/loss
            if result == 'won':
                profit_loss = stake * (odds - 1)  # Ganancia neta
                status = 'won'
            elif result == 'lost':
                profit_loss = -stake  # Pérdida total
                status = 'lost'
            elif result == 'void' or result == 'push':
                profit_loss = 0  # Stake devuelto
                status = result
            else:
                logger.error(f"Resultado inválido: {result}")
                return False

            # Actualizar apuesta
            cursor.execute('''
                UPDATE bets
                SET status = ?,
                    result = ?,
                    profit_loss = ?,
                    settled_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (status, result, profit_loss, bet_id))

            # Actualizar bankroll
            # Si ganó: devolver stake + ganancia
            # Si perdió: ya se restó al registrar, no hacer nada
            # Si void/push: devolver stake
            if result == 'won':
                bankroll_change = stake + profit_loss  # Stake + ganancia
            elif result == 'void' or result == 'push':
                bankroll_change = stake  # Solo devolver stake
            else:
                bankroll_change = 0  # Ya se restó

            if bankroll_change > 0:
                cursor.execute('''
                    UPDATE user_bankrolls
                    SET current_bankroll = current_bankroll + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (bankroll_change, user_id))

            conn.commit()
            conn.close()

            logger.info(f"✓ Apuesta {bet_id} liquidada: {result} (P/L: {profit_loss})")
            return True

        except Exception as e:
            logger.error(f"Error liquidando apuesta: {e}")
            return False

    def get_user_stats(self, user_id: int, days: int = None) -> Dict:
        """
        Obtener estadísticas de un usuario

        Args:
            user_id: ID del usuario
            days: Días hacia atrás (None = todo el historial)

        Returns:
            Diccionario con estadísticas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Filtro de fecha
            date_filter = ''
            if days:
                date_cutoff = (datetime.now() - timedelta(days=days)).isoformat()
                date_filter = f"AND placed_at >= '{date_cutoff}'"

            # Obtener bankroll
            cursor.execute('SELECT * FROM user_bankrolls WHERE user_id = ?', (user_id,))
            bankroll_row = cursor.fetchone()

            if not bankroll_row:
                return {'error': 'Usuario no tiene bankroll configurado'}

            initial_br, current_br, currency = bankroll_row[1], bankroll_row[2], bankroll_row[3]

            # Estadísticas generales
            cursor.execute(f'''
                SELECT
                    COUNT(*) as total_bets,
                    SUM(CASE WHEN status = 'won' THEN 1 ELSE 0 END) as wins,
                    SUM(CASE WHEN status = 'lost' THEN 1 ELSE 0 END) as losses,
                    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                    SUM(stake) as total_staked,
                    SUM(profit_loss) as total_profit_loss,
                    AVG(odds) as avg_odds,
                    AVG(CASE WHEN confidence IS NOT NULL THEN confidence ELSE NULL END) as avg_confidence
                FROM bets
                WHERE user_id = ? {date_filter}
            ''', (user_id,))

            stats_row = cursor.fetchone()

            total_bets = stats_row[0] or 0
            wins = stats_row[1] or 0
            losses = stats_row[2] or 0
            pending = stats_row[3] or 0
            total_staked = stats_row[4] or 0
            total_pl = stats_row[5] or 0
            avg_odds = stats_row[6] or 0
            avg_conf = stats_row[7] or 0

            # Calcular métricas
            settled_bets = wins + losses
            win_rate = (wins / settled_bets * 100) if settled_bets > 0 else 0
            roi = (total_pl / total_staked * 100) if total_staked > 0 else 0
            bankroll_change = current_br - initial_br
            bankroll_change_pct = (bankroll_change / initial_br * 100) if initial_br > 0 else 0

            # Racha actual
            cursor.execute(f'''
                SELECT status FROM bets
                WHERE user_id = ? AND status IN ('won', 'lost')
                ORDER BY settled_at DESC
                LIMIT 10
            ''', (user_id,))

            recent_results = [row[0] for row in cursor.fetchall()]
            current_streak = self._calculate_streak(recent_results)

            # Mejor/Peor apuesta
            cursor.execute(f'''
                SELECT match_description, profit_loss
                FROM bets
                WHERE user_id = ? AND status = 'won'
                ORDER BY profit_loss DESC
                LIMIT 1
            ''', (user_id,))
            best_bet = cursor.fetchone()

            cursor.execute(f'''
                SELECT match_description, profit_loss
                FROM bets
                WHERE user_id = ? AND status = 'lost'
                ORDER BY profit_loss ASC
                LIMIT 1
            ''', (user_id,))
            worst_bet = cursor.fetchone()

            conn.close()

            return {
                'user_id': user_id,
                'bankroll': {
                    'initial': initial_br,
                    'current': current_br,
                    'currency': currency,
                    'change': bankroll_change,
                    'change_percentage': bankroll_change_pct
                },
                'bets': {
                    'total': total_bets,
                    'won': wins,
                    'lost': losses,
                    'pending': pending,
                    'settled': settled_bets
                },
                'performance': {
                    'win_rate': round(win_rate, 1),
                    'roi': round(roi, 1),
                    'total_staked': round(total_staked, 2),
                    'total_profit_loss': round(total_pl, 2),
                    'avg_odds': round(avg_odds, 2),
                    'avg_confidence': round(avg_conf, 1)
                },
                'streaks': current_streak,
                'best_bet': best_bet,
                'worst_bet': worst_bet,
                'period_days': days or 'All time'
            }

        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {'error': str(e)}

    def get_bet_history(self, user_id: int, limit: int = 20, status: str = None) -> List[Dict]:
        """
        Obtener historial de apuestas

        Args:
            user_id: ID del usuario
            limit: Número máximo de apuestas a retornar
            status: Filtrar por status (pending, won, lost, etc.)

        Returns:
            Lista de apuestas
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = 'SELECT * FROM bets WHERE user_id = ?'
            params = [user_id]

            if status:
                query += ' AND status = ?'
                params.append(status)

            query += ' ORDER BY placed_at DESC LIMIT ?'
            params.append(limit)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []

    def _calculate_streak(self, results: List[str]) -> Dict:
        """Calcular racha actual"""
        if not results:
            return {'type': 'none', 'count': 0}

        current = results[0]
        count = 1

        for result in results[1:]:
            if result == current:
                count += 1
            else:
                break

        return {
            'type': 'winning' if current == 'won' else 'losing',
            'count': count
        }

    def format_stats_for_telegram(self, stats: Dict) -> str:
        """Formatear estadísticas para Telegram"""
        if 'error' in stats:
            return f"❌ {stats['error']}"

        br = stats['bankroll']
        bets = stats['bets']
        perf = stats['performance']
        streak = stats['streaks']

        # Emoji según cambio de bankroll
        br_emoji = "📈" if br['change'] > 0 else "📉" if br['change'] < 0 else "➖"

        # Emoji según ROI
        roi_emoji = "🔥" if perf['roi'] > 10 else "✅" if perf['roi'] > 0 else "⚠️"

        msg = f"💰 *TU BANKROLL*\n\n"
        msg += f"💵 Inicial: {br['initial']:.2f} {br['currency']}\n"
        msg += f"💰 Actual: *{br['current']:.2f} {br['currency']}*\n"
        msg += f"{br_emoji} Cambio: {br['change']:+.2f} ({br['change_percentage']:+.1f}%)\n\n"

        msg += f"📊 *ESTADÍSTICAS DE APUESTAS*\n\n"
        msg += f"🎲 Total de apuestas: {bets['total']}\n"
        msg += f"✅ Ganadas: {bets['won']}\n"
        msg += f"❌ Perdidas: {bets['lost']}\n"
        msg += f"⏳ Pendientes: {bets['pending']}\n\n"

        msg += f"📈 *RENDIMIENTO*\n\n"
        msg += f"🎯 Win Rate: {perf['win_rate']}%\n"
        msg += f"{roi_emoji} ROI: *{perf['roi']:+.1f}%*\n"
        msg += f"💸 Total apostado: {perf['total_staked']:.2f}\n"
        msg += f"💰 Ganancia/Pérdida: *{perf['total_profit_loss']:+.2f}*\n"
        msg += f"📊 Cuota promedio: {perf['avg_odds']:.2f}\n"

        if perf['avg_confidence']:
            msg += f"🎲 Confianza promedio: {perf['avg_confidence']:.0f}%\n"

        # Racha
        if streak['count'] > 0:
            streak_emoji = "🔥" if streak['type'] == 'winning' else "❄️"
            streak_text = f"{streak['count']} {'victorias' if streak['type'] == 'winning' else 'derrotas'}"
            msg += f"\n{streak_emoji} Racha actual: {streak_text}\n"

        # Mejor/Peor apuesta
        if stats['best_bet']:
            match, pl = stats['best_bet']
            msg += f"\n🏆 Mejor apuesta: +{pl:.2f}\n   _{match}_\n"

        if stats['worst_bet']:
            match, pl = stats['worst_bet']
            msg += f"💔 Peor apuesta: {pl:.2f}\n   _{match}_\n"

        period = stats['period_days']
        if period != 'All time':
            msg += f"\n📅 _Período: Últimos {period} días_"

        return msg


if __name__ == '__main__':
    # Test del bankroll manager
    print("🧪 Testing Bankroll Manager...\n")

    manager = BankrollManager()

    # Test: Configurar bankroll
    print("Test 1: Configurar bankroll")
    success = manager.set_bankroll(12345, 1000.0, 'USD')
    print(f"✓ Bankroll configurado: {success}\n")

    # Test: Registrar apuesta
    print("Test 2: Registrar apuesta")
    bet_id = manager.register_bet(
        user_id=12345,
        match="Barcelona vs Real Madrid",
        bet_type="Goles",
        prediction="Over 2.5",
        stake=50.0,
        odds=1.85,
        confidence=80
    )
    print(f"✓ Apuesta registrada: ID {bet_id}\n")

    # Test: Obtener stats
    print("Test 3: Estadísticas")
    stats = manager.get_user_stats(12345)
    formatted = manager.format_stats_for_telegram(stats)
    print(formatted)

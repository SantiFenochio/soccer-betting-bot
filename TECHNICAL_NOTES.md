# 🔧 Notas Técnicas

## 📐 Arquitectura del Sistema

```
soccer-betting-bot/
│
├── main.py              # Punto de entrada principal
├── bot.py               # Bot de Telegram (comandos interactivos)
├── scheduler.py         # Sistema de notificaciones automáticas
├── analyzer.py          # Motor de análisis y predicciones
├── database.py          # Gestión de base de datos SQLite
├── config.py            # Configuración centralizada
│
├── data/                # Cache de datos y base de datos
│   └── predictions.db   # SQLite database
│
├── logs/                # Archivos de log
│   ├── bot.log
│   └── app.log
│
└── .env                 # Variables de entorno (NO subir a git!)
```

## 🧠 Lógica de Predicciones

### Fuentes de Datos

1. **FBref** - Estadísticas generales
   - Resultados de partidos
   - Goles a favor/contra
   - Clean sheets
   - Datos de las últimas 5 temporadas

2. **Understat** - Métricas avanzadas
   - xG (Expected Goals)
   - xGA (Expected Goals Against)
   - Calidad de tiros
   - Performance vs expectativas

### Algoritmo de Predicción

El bot analiza los últimos **10 partidos** de cada equipo y calcula:

1. **Over 2.5 goles**
   - Promedio de goles combinado > 2.8
   - Histórico Over 2.5 > 60%
   - Confianza: proporcional al histórico

2. **BTTS (Both Teams To Score)**
   - BTTS histórico > 55%
   - Ambos equipos con promedio > 0.8 goles
   - Confianza: media del histórico BTTS

3. **Victoria del local**
   - Win rate local > 60%
   - Win rate visitante < 40%
   - Diferencia de goles positiva
   - Confianza: win percentage del local

4. **Under 2.5 goles**
   - Promedio combinado < 2.0
   - Ambos equipos con Over 2.5 < 40%
   - Confianza: fija en 70%

### Umbrales de Confianza

```python
🔥 Alta (80%+)   - Predicción muy confiable
✅ Media (70-79%) - Predicción confiable
⚠️ Baja (60-69%)  - Predicción moderada
```

## 📊 Base de Datos

### Tabla: predictions

```sql
id INTEGER PRIMARY KEY
date TEXT                 -- Fecha del partido
league TEXT               -- Liga
home_team TEXT            -- Equipo local
away_team TEXT            -- Equipo visitante
prediction_type TEXT      -- Tipo (Over 2.5, BTTS, etc.)
confidence INTEGER        -- Confianza (0-100)
description TEXT          -- Descripción de la predicción
reason TEXT               -- Razón estadística
created_at TEXT           -- Timestamp de creación
result TEXT               -- Resultado real (NULL si no verificado)
is_correct BOOLEAN        -- Si fue correcta (NULL si no verificado)
checked_at TEXT           -- Cuándo se verificó
```

### Tabla: users

```sql
chat_id INTEGER PRIMARY KEY  -- Telegram Chat ID
username TEXT                -- Usuario de Telegram
first_name TEXT              -- Nombre
last_name TEXT               -- Apellido
subscribed BOOLEAN           -- Si recibe notificaciones
created_at TEXT              -- Fecha de registro
last_interaction TEXT        -- Última interacción
```

### Tabla: statistics

```sql
id INTEGER PRIMARY KEY
date TEXT                    -- Fecha del reporte
total_predictions INTEGER    -- Total de predicciones
correct_predictions INTEGER  -- Correctas
accuracy REAL                -- Precisión (%)
by_type TEXT                 -- JSON con stats por tipo
```

## 🔄 Flujo de Trabajo

### 1. Inicialización
```python
main.py
  → Verifica entorno
  → Crea directorios
  → Instala dependencias
  → Inicia bot/scheduler
```

### 2. Procesamiento de Comando
```python
Usuario envía: /partido Real Madrid vs Barcelona
  → bot.py recibe comando
  → Parsea equipos
  → analyzer.py obtiene datos (FBref/Understat)
  → Calcula estadísticas
  → Genera predicciones
  → Guarda en database.py
  → Envía respuesta formateada
```

### 3. Notificaciones Automáticas
```python
scheduler.py ejecuta cada día a las 09:00
  → Obtiene partidos de hoy
  → Filtra por confianza mínima (70%)
  → Selecciona top 5
  → Obtiene usuarios suscritos
  → Envía mensaje a cada usuario
  → Guarda predicciones en DB
```

## 🚀 Optimizaciones Implementadas

1. **Cache de datos**
   - soccerdata cachea automáticamente en `~/soccerdata`
   - Reduce requests a servidores externos
   - Expira después de 24h

2. **Rate limiting**
   - Delay de 0.5s entre envíos masivos
   - Previene bans de Telegram

3. **Lazy loading**
   - Scrapers se inicializan solo cuando se necesitan
   - Reduce tiempo de startup

4. **Async/await**
   - Bot usa asyncio para mejor performance
   - Maneja múltiples usuarios simultáneamente

## 🔐 Seguridad

1. **Variables sensibles en .env**
   - Tokens no hardcodeados
   - .env en .gitignore

2. **Validación de entrada**
   - Comandos parseados y sanitizados
   - Protección contra injection

3. **Error handling**
   - Try-catch en todas las operaciones críticas
   - Logs detallados para debugging

## 📈 Escalabilidad

### Actual
- ✅ Soporta múltiples usuarios
- ✅ 6 ligas simultáneas
- ✅ ~50-100 partidos por día

### Futuras Mejoras

1. **PostgreSQL en lugar de SQLite**
   - Mayor capacidad
   - Mejores queries concurrentes

2. **Redis para cache**
   - Cache distribuido
   - Reducir carga en scrapers

3. **Machine Learning**
   - Modelos predictivos más avanzados
   - Scikit-learn / TensorFlow
   - Features: forma del equipo, lesiones, clima, etc.

4. **API REST**
   - Exponer predicciones vía API
   - Frontend web
   - Apps móviles nativas

5. **WebSocket para live updates**
   - Predicciones en tiempo real
   - Cambios de odds
   - Goles y eventos del partido

## 🛠️ Debugging

### Ver logs en tiempo real

**Linux/Mac:**
```bash
tail -f logs/bot.log
tail -f logs/app.log
```

**Windows (PowerShell):**
```powershell
Get-Content logs\bot.log -Wait
```

### Testear componentes individualmente

```bash
# Test del analizador
python analyzer.py

# Test de la base de datos
python database.py

# Test del bot (requiere token)
python bot.py

# Test de notificaciones
python scheduler.py test
```

### Modo Debug

Edita `.env` y agrega:
```
LOG_LEVEL=DEBUG
```

Reinicia el bot para ver logs más detallados.

## 🔧 Mantenimiento

### Actualizar dependencias

```bash
pip install -r requirements.txt --upgrade
```

### Limpiar cache

```bash
# Linux/Mac
rm -rf ~/soccerdata

# Windows
rmdir /s %USERPROFILE%\soccerdata
```

### Backup de base de datos

```bash
cp data/predictions.db data/predictions_backup_$(date +%Y%m%d).db
```

### Verificar integridad

```bash
sqlite3 data/predictions.db "PRAGMA integrity_check;"
```

## 📝 Convenciones de Código

- **Docstrings**: Todas las funciones públicas
- **Type hints**: Argumentos y retornos
- **Logging**: Info para eventos, Error para fallos
- **Formato**: PEP 8
- **Nombres**: snake_case para funciones/variables

## 🧪 Testing

### Manual Testing Checklist

- [ ] Bot responde a `/start`
- [ ] Comando `/hoy` muestra partidos
- [ ] Comando `/partido` genera predicción
- [ ] Comando `/analizar` muestra stats
- [ ] Notificaciones se envían correctamente
- [ ] Base de datos guarda predicciones
- [ ] Logs se generan sin errores
- [ ] Cache funciona correctamente

### Casos de Prueba

1. **Equipo no encontrado**
   - Input: `/analizar EquipoInexistente`
   - Expected: Mensaje de error amigable

2. **Comando malformado**
   - Input: `/partido Real Madrid`
   - Expected: Instrucciones de uso

3. **Sin partidos hoy**
   - Input: `/hoy` (día sin partidos)
   - Expected: Mensaje informativo

4. **Múltiples usuarios**
   - Varios usuarios envían comandos simultáneamente
   - Expected: Todos reciben respuestas correctas

## 🌍 Internacionalización (Futuro)

Actualmente en español. Para agregar idiomas:

1. Crear `i18n/` directory
2. Archivos JSON por idioma
3. Detectar idioma del usuario
4. Cargar strings correspondientes

## 📱 Telegram Bot Limits

- Mensajes: 30/segundo
- Grupos: 20/minuto
- Tamaño mensaje: 4096 caracteres
- File size: 50MB

**Nuestras precauciones:**
- Delay de 0.5s entre mensajes masivos
- Mensajes < 2000 caracteres
- No enviamos archivos

## 🔄 Ciclo de Release

1. Desarrollar feature en rama
2. Testing manual
3. Merge a main
4. Actualizar versión
5. Reiniciar bot en producción

## 📚 Recursos

- [python-telegram-bot docs](https://docs.python-telegram-bot.org/)
- [soccerdata docs](https://soccerdata.readthedocs.io/)
- [FBref](https://fbref.com/)
- [Understat](https://understat.com/)

## 💡 Tips para Desarrolladores

1. **Prueba primero localmente**
   - Usa un bot de test diferente
   - No spamees tu bot de producción

2. **Commita frecuentemente**
   - Cambios pequeños son más fáciles de debuggear
   - Usa mensajes descriptivos

3. **Documenta cambios importantes**
   - Actualiza README cuando cambies funcionalidad
   - Agrega comentarios en código complejo

4. **Monitorea los logs**
   - Los errores aparecen primero en logs
   - Configura alertas para errores críticos

---

**Versión:** 1.0.0
**Fecha:** Marzo 2026
**Autor:** Creado con Claude Code

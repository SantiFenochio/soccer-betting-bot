# 🚀 Guía de Instalación Rápida

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta de Telegram
- Token de Bot de Telegram

## 🤖 Obtener Token de Telegram

1. Abre Telegram y busca [@BotFather](https://t.me/botfather)
2. Envía `/newbot` y sigue las instrucciones
3. Copia el token que te da (formato: `123456:ABC-DEF1234ghIkl`)
4. Ya lo tienes configurado en `.env` ✅

## 📥 Instalación

### Opción 1: Instalación Automática (Recomendada)

**Windows:**
```bash
# Doble clic en run.bat o ejecuta:
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

### Opción 2: Instalación Manual

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
   - Edita el archivo `.env`
   - Asegúrate de tener tu `TELEGRAM_BOT_TOKEN`
   - Opcional: Agrega tu `TELEGRAM_CHAT_ID` para recibir notificaciones

3. **Ejecutar el bot:**
```bash
python main.py
```

## 🔧 Configuración

### 1. Obtener tu Chat ID

1. Inicia el bot ejecutando `python main.py` y seleccionando opción 1
2. En Telegram, busca tu bot por el nombre que le diste
3. Envía `/start`
4. El bot te mostrará tu Chat ID
5. Copia ese número y pégalo en `.env` en la línea `TELEGRAM_CHAT_ID=`

### 2. Configurar Notificaciones

Edita `.env` para personalizar:

```env
# Hora de notificaciones diarias (formato 24h)
NOTIFICATION_TIME=09:00

# Zona horaria
NOTIFICATION_TIMEZONE=America/Argentina/Buenos_Aires

# Confianza mínima para predicciones (0-100)
MIN_CONFIDENCE=70
```

## ▶️ Ejecutar el Bot

Al ejecutar `python main.py`, verás un menú:

```
1. Bot de Telegram (interactivo)
   → Solo comandos manuales, sin notificaciones automáticas

2. Scheduler (notificaciones automáticas)
   → Solo notificaciones automáticas, sin comandos

3. Ambos (recomendado)
   → Comandos + notificaciones automáticas

4. Test de conexión
   → Verifica que el bot funciona correctamente
```

**Recomendación:** Selecciona opción **3** para tener todas las funcionalidades.

## 🧪 Verificar Instalación

1. Ejecuta el test:
```bash
python main.py
# Selecciona opción 4
```

2. Si recibes un mensaje en Telegram, ¡todo funciona! ✅

## 📱 Primeros Pasos

Una vez iniciado el bot:

1. Abre Telegram y busca tu bot
2. Envía `/start`
3. Prueba algunos comandos:
   - `/hoy` - Ver partidos de hoy
   - `/analizar Manchester City` - Analizar un equipo
   - `/partido Barcelona vs Real Madrid` - Predicción
   - `/tendencias` - Ver patrones confiables

## 🐛 Problemas Comunes

### "ModuleNotFoundError: No module named 'telegram'"

**Solución:**
```bash
pip install python-telegram-bot --upgrade
```

### "Error: TELEGRAM_BOT_TOKEN no encontrado"

**Solución:**
- Verifica que el archivo `.env` existe en la carpeta del bot
- Asegúrate de que la línea `TELEGRAM_BOT_TOKEN=` tenga tu token
- NO debe tener espacios: ❌ `TELEGRAM_BOT_TOKEN = 123...`
- Correcto: ✅ `TELEGRAM_BOT_TOKEN=123...`

### "Forbidden: bot was blocked by the user"

**Solución:**
- Abre Telegram y busca tu bot
- Si lo bloqueaste, desbloquealo
- Envía `/start` de nuevo

### El bot no responde

**Solución:**
1. Verifica que el bot esté ejecutándose (debe mostrar "Bot configurado. Iniciando polling...")
2. Envía `/start` en Telegram
3. Verifica tu conexión a Internet
4. Revisa los logs en `logs/bot.log`

## 🔄 Mantener el Bot Ejecutándose 24/7

### Windows

Usa el Programador de Tareas:
1. Abre "Programador de tareas"
2. Crear tarea básica
3. Acción: Iniciar programa
4. Programa: `C:\ruta\a\python.exe`
5. Argumentos: `C:\ruta\a\soccer-betting-bot\main.py`

### Linux (con systemd)

Crea un servicio:

```bash
sudo nano /etc/systemd/system/soccer-bot.service
```

Contenido:
```ini
[Unit]
Description=Soccer Betting Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/a/soccer-betting-bot
ExecStart=/usr/bin/python3 /ruta/a/soccer-betting-bot/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Activar:
```bash
sudo systemctl enable soccer-bot
sudo systemctl start soccer-bot
sudo systemctl status soccer-bot
```

### Con screen (Linux/Mac)

```bash
screen -S soccer-bot
python3 main.py
# Presiona Ctrl+A, luego D para detach
# Para volver: screen -r soccer-bot
```

## 📊 Ligas Disponibles

El bot soporta:
- 🇪🇸 La Liga (España)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League (Inglaterra)
- 🇩🇪 Bundesliga (Alemania)
- 🇮🇹 Serie A (Italia)
- 🇫🇷 Ligue 1 (Francia)
- 🇦🇷 Liga Profesional (Argentina)

## 💡 Tips

- Las predicciones se generan analizando los últimos 10 partidos de cada equipo
- La confianza se calcula basándose en estadísticas históricas
- Usa `/stats` para ver la precisión del bot
- El bot mejora con el tiempo al acumular más datos

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs en `logs/bot.log` y `logs/app.log`
2. Verifica tu archivo `.env`
3. Asegúrate de tener la última versión de las dependencias:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

## 🎉 ¡Listo!

Tu bot está configurado y listo para usar. ¡Disfruta las predicciones! ⚽🔥

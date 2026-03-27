# 📝 Pasos que Debes Hacer Manualmente

## ✅ Ya Hecho (Automático)
- ✅ Token de Telegram configurado
- ✅ Chat ID configurado
- ✅ Python instalado (3.14.3)
- ✅ pip actualizado
- ✅ Dependencias instalándose
- ✅ Estructura del proyecto completa
- ✅ Soporte para selecciones agregado

---

## 📋 Lo que Debes Hacer TÚ

### 1. ⏳ Esperar que Terminen de Instalarse las Dependencias

Las dependencias se están instalando ahora mismo. Tomará 2-5 minutos.

**Verifica que terminó:**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
python -m pip list
```

Deberías ver instalado:
- python-telegram-bot
- soccerdata
- pandas
- numpy
- schedule
- etc.

---

### 2. 🚀 Ejecutar el Bot por Primera Vez

**Opción A - Usando el script (Recomendado):**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
run.bat
```

**Opción B - Manual:**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
python main.py
```

Cuando te pregunte qué opción, selecciona **3** (Bot + Notificaciones)

---

### 3. 📱 Probar el Bot en Telegram

1. Abre Telegram en tu celular/computadora
2. Busca tu bot (el nombre que le diste a @BotFather)
3. Envía: `/start`
4. Deberías ver el mensaje de bienvenida

---

### 4. 🧪 Probar los Comandos

Prueba cada comando para verificar que funciona:

**Comandos de Clubes:**
```
/hoy
/partido Manchester City vs Liverpool
/analizar Real Madrid
```

**Comandos de Selecciones (NUEVO):**
```
/selecciones Argentina vs Brasil
/selecciones España vs Francia
/mundial
```

**Otros:**
```
/tendencias
/ligas
/stats
/help
```

---

### 5. 🔧 Configuración Opcional

Si querés personalizar el bot, edita `.env`:

```env
# Cambiar hora de notificaciones
NOTIFICATION_TIME=09:00

# Cambiar confianza mínima (60-90)
MIN_CONFIDENCE=70

# Tu Chat ID (ya configurado)
TELEGRAM_CHAT_ID=882530352
```

Después de cambiar `.env`, reinicia el bot.

---

### 6. ⚠️ Si Algo Falla

**Error: "Module not found"**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
python -m pip install -r requirements.txt --upgrade
```

**Error: "Bot token is invalid"**
- Verifica que el token en `.env` no tenga espacios
- Debe ser: `TELEGRAM_BOT_TOKEN=123456:ABC...`

**Bot no responde en Telegram:**
- Verifica que el bot esté corriendo (debe decir "Iniciando polling...")
- Envía `/start` de nuevo
- Verifica tu conexión a Internet

**Ver los logs:**
```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
type logs\bot.log
type logs\app.log
```

---

### 7. 🎯 Mantener el Bot Corriendo

**Para desarrollo/pruebas:**
- Simplemente deja abierta la terminal
- Presiona `Ctrl+C` para detener

**Para producción (24/7):**

**Opción A - Segundo plano (Windows):**
1. Descarga [NSSM](https://nssm.cc/download)
2. Ejecuta: `nssm install SoccerBot`
3. Program: `C:\Users\Fer 1\AppData\Local\Python\pythoncore-3.14-64\python.exe`
4. Arguments: `C:\Users\Fer 1\soccer-betting-bot\main.py`
5. Click "Install service"
6. Inicia el servicio desde Servicios de Windows

**Opción B - Programador de Tareas:**
1. Abre "Programador de tareas"
2. "Crear tarea básica"
3. Nombre: "Soccer Bot"
4. Desencadenador: Al iniciar sesión
5. Acción: Iniciar programa
6. Programa: `C:\Users\Fer 1\AppData\Local\Python\pythoncore-3.14-64\python.exe`
7. Argumentos: `C:\Users\Fer 1\soccer-betting-bot\main.py`

**Opción C - Servidor VPS (Recomendado para 24/7):**
- Alquila un VPS barato (DigitalOcean, Vultr, etc.)
- Instala el bot ahí
- Úsalo con screen o systemd

---

### 8. 📊 Verificar que Todo Funciona

**Checklist:**
- [ ] Bot responde a `/start`
- [ ] `/hoy` muestra partidos (si los hay)
- [ ] `/partido Real Madrid vs Barcelona` genera predicción
- [ ] `/selecciones Argentina vs Brasil` funciona (NUEVO)
- [ ] `/analizar Manchester City` muestra estadísticas
- [ ] `/mundial` muestra info del Mundial 2026 (NUEVO)
- [ ] `/stats` muestra estadísticas del bot
- [ ] Base de datos se crea en `data/predictions.db`
- [ ] Logs se escriben en `logs/bot.log`

---

## 🎉 ¡Y Eso Es Todo!

Una vez que completes estos pasos, tu bot estará **100% funcional** con:

✅ Análisis de 6 ligas principales
✅ Análisis de selecciones nacionales (NUEVO)
✅ Predicciones automáticas
✅ Notificaciones diarias
✅ Tracking de precisión
✅ Soporte multi-usuario
✅ Info del Mundial 2026 (NUEVO)

---

## 💡 Tips Finales

1. **Revisa los logs regularmente:**
   - `logs/bot.log` - Actividad del bot
   - `logs/app.log` - Errores y eventos

2. **Actualiza las dependencias cada mes:**
   ```bash
   python -m pip install -r requirements.txt --upgrade
   ```

3. **Backup de la base de datos:**
   ```bash
   copy data\predictions.db data\backup_predictions.db
   ```

4. **Lee la documentación:**
   - `QUICKSTART.md` - Inicio rápido
   - `INSTALL.md` - Instalación completa
   - `NUEVAS_FUNCIONES.md` - Selecciones nacionales (NUEVO)
   - `TECHNICAL_NOTES.md` - Detalles técnicos

---

## 🆘 Soporte

Si necesitas ayuda:
1. Revisa `INSTALL.md` - Troubleshooting
2. Revisa los logs en `logs/`
3. Verifica que Python y todas las dependencias estén instaladas

---

**¿Dudas?** Preguntame y te ayudo! 😄

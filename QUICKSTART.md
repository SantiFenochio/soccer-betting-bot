# ⚡ Inicio Rápido en 5 Minutos

## 1️⃣ Instalar Dependencias (1 min)

```bash
pip install -r requirements.txt
```

## 2️⃣ Verificar Token (30 seg)

Tu token ya está configurado en `.env`:
```
TELEGRAM_BOT_TOKEN=8649351013:AAFDkx66VTiWFI38b5u6f4VxdxtbZAj65cQ
```

✅ Listo para usar!

## 3️⃣ Iniciar Bot (30 seg)

**Opción A - Automático (Windows):**
```bash
run.bat
```

**Opción B - Automático (Linux/Mac):**
```bash
./run.sh
```

**Opción C - Manual:**
```bash
python main.py
```

Selecciona opción **3** (Bot + Notificaciones)

## 4️⃣ Configurar Telegram (2 min)

1. Abre Telegram
2. Busca tu bot (el nombre que le diste a @BotFather)
3. Envía: `/start`
4. Copia tu Chat ID del mensaje
5. Pégalo en `.env`:
   ```
   TELEGRAM_CHAT_ID=tu_chat_id_aqui
   ```
6. Reinicia el bot

## 5️⃣ Probar Comandos (1 min)

En Telegram, envía:

```
/hoy
```

¡Deberías ver partidos y predicciones! 🎉

## 🎯 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `/hoy` | Partidos y predicciones de hoy |
| `/partido [equipo1] vs [equipo2]` | Analizar partido específico |
| `/analizar [equipo]` | Estadísticas del equipo |
| `/tendencias` | Patrones más confiables |
| `/stats` | Precisión del bot |

## 💡 Ejemplos Reales

```
/partido Real Madrid vs Barcelona
/analizar Manchester City
/partido River vs Boca
```

## 🔥 Tips Pro

- **Notificaciones diarias**: Cambia `NOTIFICATION_TIME=09:00` en `.env`
- **Más predicciones**: Baja `MIN_CONFIDENCE=60` en `.env`
- **Menos predicciones**: Sube `MIN_CONFIDENCE=80` en `.env`

## ⚠️ Si Algo Falla

### Bot no responde
```bash
# Verifica que esté corriendo
python main.py
# Selecciona opción 4 para test
```

### Error de módulos
```bash
pip install -r requirements.txt --upgrade
```

### Token inválido
Verifica que en `.env` no haya espacios:
- ❌ `TELEGRAM_BOT_TOKEN = 123...`
- ✅ `TELEGRAM_BOT_TOKEN=123...`

## 📚 Más Info

- [Guía completa de instalación](INSTALL.md)
- [README con todas las features](README.md)

## 🎉 ¡Ya estás listo!

Tu bot está funcionando. Ahora solo:
1. Abre Telegram
2. Envía `/hoy`
3. ¡Disfruta las predicciones! ⚽🔥

---

**Siguiente paso:** Lee [INSTALL.md](INSTALL.md) para configuración avanzada (mantenerlo 24/7, personalizar ligas, etc.)

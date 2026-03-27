# 🔑 Guía de API Keys Opcionales

## ¿Por qué usar APIs adicionales?

El bot funciona **sin API keys** usando solo FBref y Understat, pero agregar estas APIs **mejora significativamente** el análisis:

### ✅ Con APIs adicionales obtienes:
- 📅 **Partidos de los próximos días** (no solo hoy)
- 💰 **Cuotas de casas de apuestas** en tiempo real
- 🎯 **Value bets** (apuestas con valor positivo)
- 📊 **Más fuentes de datos** = predicciones más precisas
- 🔄 **Actualizaciones en tiempo real**

### ⚠️ Sin APIs adicionales:
- Solo partidos de hoy (limitado)
- Sin cuotas de apuestas
- Solo datos históricos de FBref
- Análisis más básico

---

## 🆓 APIs Gratuitas Recomendadas

### 1. API-Football ⚽ (RECOMENDADA)

**¿Qué ofrece?**
- Partidos próximos de 1000+ ligas
- Live scores y estadísticas
- Formaciones y alineaciones
- Lesiones y suspensiones
- Historial head-to-head

**Tier Gratuito:**
- ✅ 100 requests por día
- ✅ Todas las funcionalidades
- ✅ Sin tarjeta de crédito

**Cómo obtenerla:**

1. Ve a: https://www.api-football.com/
2. Click en "Get Started" → "Free Plan"
3. Registrate con email
4. Confirma tu email
5. Ve al Dashboard
6. Copia tu API Key

**Configuración:**
```env
API_FOOTBALL_KEY=3201688d6cc003ea8445d01e0dcd952b
```
URL: v3.football.api-sports.io
---

### 2. The Odds API 💰 (OPCIONAL)

**¿Qué ofrece?**
- Cuotas de +20 casas de apuestas
- Mercados: 1X2, Over/Under, BTTS
- Ligas principales de Europa y Sudamérica
- Actualización cada 10 minutos

**Tier Gratuito:**
- ✅ 500 requests por mes
- ✅ Todas las casas de apuestas
- ✅ Sin tarjeta de crédito

**Cómo obtenerla:**

1. Ve a: https://the-odds-api.com/
2. Click en "Get a Free API Key"
3. Completa el formulario
4. Revisa tu email
5. Copia tu API Key del email

**Configuración:**
```env
ODDS_API_KEY=e6a1deaad1ead644f03dec0e700265d9
```

---

### 3. Football-Data.org 📊 (OPCIONAL)

**¿Qué ofrece?**
- Fixtures y resultados
- Clasificaciones
- Goleadores
- Datos limpios en JSON

**Tier Gratuito:**
- ✅ 10 requests por minuto
- ✅ Ligas principales europeas
- ✅ Sin tarjeta de crédito

**Cómo obtenerla:**

1. Ve a: https://www.football-data.org/client/register
2. Completa el formulario de registro
3. Confirma tu email
4. Login y ve a "My Account"
5. Copia tu API Token

**Configuración:**
```env
FOOTBALL_DATA_KEY=508c963707a644ffa0bd41506fc3bd8f
```

---

## ⚙️ Configuración en el Bot

### Paso 1: Agregar las Keys

Edita el archivo `.env` en la carpeta del bot:

```bash
cd "C:\Users\Fer 1\soccer-betting-bot"
notepad .env
```

Agrega tus API keys:

```env
# APIS OPCIONALES
API_FOOTBALL_KEY=abc123xyz456
ODDS_API_KEY=def789ghi012
FOOTBALL_DATA_KEY=jkl345mno678
```

### Paso 2: Reiniciar el Bot

Si el bot está corriendo, reinicialo para que cargue las nuevas keys:

1. Presiona `Ctrl+C` para detenerlo
2. Ejecuta de nuevo: `python main.py`
3. Selecciona opción 3

---

## 🧪 Verificar que Funcionan

Una vez configuradas, el bot usará automáticamente las APIs disponibles.

**Para verificar:**

1. Ejecuta el bot
2. En Telegram, envía: `/proximos 7`
3. Deberías ver:
   - Partidos de los próximos 7 días
   - Más detalles por partido
   - (Si configuraste Odds API) Cuotas de apuestas

**Sin APIs:**
- `/proximos` mostrará "No hay partidos" o datos limitados

**Con APIs:**
- `/proximos` mostrará muchos partidos con predicciones

---

## 📊 Comparación de Features

| Feature | Sin APIs | Con API-Football | + Odds API | + Todas |
|---------|----------|------------------|------------|---------|
| Partidos de hoy | ✅ | ✅ | ✅ | ✅ |
| Partidos próximos | ⚠️ Limitado | ✅ Completo | ✅ | ✅ |
| Predicciones básicas | ✅ | ✅ | ✅ | ✅ |
| Cuotas de apuestas | ❌ | ❌ | ✅ | ✅ |
| Value bets | ❌ | ❌ | ✅ | ✅ |
| Live scores | ❌ | ✅ | ✅ | ✅ |
| Alineaciones | ❌ | ✅ | ❌ | ✅ |
| Lesiones | ❌ | ✅ | ❌ | ✅ |

---

## 💡 Recomendación

**Para empezar:**
- Usa el bot sin APIs (funciona perfecto)
- Cuando quieras más features, agrega **API-Football** primero

**Para análisis completo:**
- API-Football + The Odds API
- Te dará predicciones + cuotas + value bets

**Solo si quieres TODO:**
- Las 3 APIs
- Máxima precisión y funcionalidades

---

## ⚠️ Límites de Rate

**API-Football:**
- 100 requests/día gratis
- El bot hace ~1 request por liga consultada
- `/proximos` = 6 requests (6 ligas)
- Puedes hacer ~16 consultas por día

**The Odds API:**
- 500 requests/mes gratis
- ~17 requests/día
- Solo se usa cuando pides cuotas específicas

**Football-Data.org:**
- 10 requests/minuto
- Más que suficiente para uso normal

---

## 🔐 Seguridad

**Tus API Keys son privadas:**
- Nunca las compartas
- Están en `.env` (no se suben a git)
- Si las expones, regeneralas desde el dashboard

---

## 🆘 Problemas Comunes

### "Invalid API Key"
- Verifica que copiaste bien la key
- Asegúrate de que no haya espacios
- Confirma tu email en el servicio

### "Rate limit exceeded"
- Esperaste el límite diario/mensual
- Usa menos el comando `/proximos`
- Considera reducir el número de días

### "No data available"
- Verifica que la API key sea válida
- Revisa los logs: `logs/app.log`
- La API puede estar caída temporalmente

---

## 📚 Recursos

- [API-Football Documentation](https://www.api-football.com/documentation-v3)
- [The Odds API Documentation](https://the-odds-api.com/liveapi/guides/v4/)
- [Football-Data.org Docs](https://www.football-data.org/documentation/quickstart)

---

## 🎉 ¡Listo!

Con estas APIs configuradas, tu bot tendrá **análisis profesional** con:
- Partidos de toda la semana
- Cuotas en tiempo real
- Value bets automáticos
- Predicciones más precisas

**¿Dudas?** Revisa los logs en `logs/app.log` o preguntame! 😄

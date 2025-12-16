# Scraper de Following con Instaloader (Cookies v2)

Este proyecto permite **extraer la lista de cuentas que sigue un usuario objetivo (followees / following)** en Instagram usando **Instaloader** y autenticación mediante **cookies** (SessionID + CSRF Token), sin necesidad de iniciar sesión con usuario/contraseña dentro del script.

Además, el script recopila datos básicos de cada cuenta seguida y, opcionalmente, **exporta el resultado a Excel (.xlsx)**.

> ⚠️ Nota: el funcionamiento depende de cookies válidas. Si expiran o Instagram exige re-autenticación, puede aparecer `LoginRequiredException`.

---

## ✅ Características

- Login usando cookies (`sessionid` y `csrftoken`).
- **Fix aplicado (Cookies v2):** asigna `context.username` para que Instaloader considere la sesión como logueada.
- Extracción del *following* (seguidos) del usuario objetivo.
- Manejo de errores comunes:
  - Cookies expiradas / login requerido
  - Perfil no existe
  - Errores al leer datos de un perfil específico
- Control de velocidad con delays para reducir bloqueos.
- Exportación opcional a **Excel** con columnas ordenadas.

---
## ✅ Uso
El programa te pedirá:

Tu usuario (dueño de las cookies)

SessionID

CSRF Token

Username objetivo a analizar

Límite opcional de usuarios a extraer

Si deseas guardar a Excel

```bash
python scraper_instaloader.py
```

## 📦 Requisitos

- Python 3.9+ (recomendado)
- Dependencias:
  - `instaloader`
  - `pandas`
  - `openpyxl`

Instalación:

```bash
pip install instaloader pandas openpyxl

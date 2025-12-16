import time
import pandas as pd
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURACIÓN ---
def iniciar_navegador():
    print("🚀 Abriendo navegador...")
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Descomenta si no quieres ver la ventana
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def obtener_detalle_perfil(username, cookies_dict):
    """Consulta el endpoint web_profile_info para obtener detalles del usuario."""
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "user-agent": "Mozilla/5.0",
        "x-requested-with": "XMLHttpRequest",
        "referer": f"https://www.instagram.com/{username}/",
    }
    try:
        resp = requests.get(url, headers=headers, cookies=cookies_dict, timeout=15)
        if resp.status_code != 200:
            return None
        user = resp.json().get("data", {}).get("user", {})
        if not user:
            return None

        account_type = "Empresa" if user.get("is_business_account") else "Creador" if user.get("is_professional_account") else "Personal"
        follower_count = user.get("edge_followed_by", {}).get("count", 0)
        following_count = user.get("edge_follow", {}).get("count", 0)

        return {
            "full_name": user.get("full_name", ""),
            "username": username,
            "biography": user.get("biography", "").replace("\n", " "),
            "account_type": account_type,
            "category": user.get("category_name", ""),
            "follower_count": follower_count,
            "following_count": following_count,
            "profile_url": f"https://www.instagram.com/{username}/",
            "is_verified": user.get("is_verified", False),
            "is_private": user.get("is_private", False),
        }
    except Exception:
        return None

def extraer_seguidos(target_username, max_limite=None):
    driver = iniciar_navegador()
    datos_obtenidos = []  # usernames crudos
    vistos = set()
    ultimos_contados = 0
    sin_cambios = 0

    try:
        # 1. Login Manual (Más seguro y evita problemas de código de 2 factores)
        print("🔑 Paso 1: Inicia sesión en Instagram manualmente en la ventana que se abrió.")
        driver.get("https://www.instagram.com/")
        input("⚠️  Presiona ENTER en esta consola cuando ya hayas iniciado sesión y veas el inicio...")

        # 2. Ir al perfil objetivo
        print(f"🔍 Yendo al perfil de @{target_username}...")
        driver.get(f"https://www.instagram.com/{target_username}/")
        time.sleep(3)

        # 3. Detectar botón de "Seguidos" y hacer click
        # Buscamos el enlace que contiene la palabra "following" en el href
        try:
            boton_seguidos = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "seguidos")) 
                # Nota: Si tu instagram está en inglés, cambia "seguidos" por "following"
            )
            boton_seguidos.click()
        except:
            # Intento alternativo por URL si falla el click
            print("⚠️ Botón no detectado, intentando forzar URL...")
            driver.get(f"https://www.instagram.com/{target_username}/following/")
        
        print("⏳ Esperando que cargue la lista...")
        time.sleep(4)

        # 4. Scroll dentro del modal (la ventana emergente)
        # En Instagram web, la lista está dentro de un div con rol 'dialog' y overflow scroll
        scroll_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@role='dialog']//div[contains(@style, 'overflow')]"
            ))
        )
        
        print("⬇️  Iniciando scroll infinito...")
        while True:
            # Bajar el scroll al fondo del contenedor
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
            time.sleep(2.0)  # Espera para cargar nuevos elementos

            links = scroll_box.find_elements(By.TAG_NAME, "a")
            # Filtramos solo perfiles (excluimos posts /p/ y exploración)
            for l in links:
                href = l.get_attribute('href')
                if not href or "/p/" in href or "/explore/" in href:
                    continue
                username_href = href.rstrip('/').split('/')[-1]
                if username_href:
                    vistos.add(username_href)
            usuarios_unicos = len(vistos)
            print(f"👀 Usuarios detectados hasta ahora: {usuarios_unicos}")

            if max_limite and usuarios_unicos >= max_limite:
                print("🛑 Límite alcanzado.")
                break

            # Si no aumenta el conteo tras varios intentos, asumimos fin de la lista
            if usuarios_unicos == ultimos_contados:
                sin_cambios += 1
            else:
                sin_cambios = 0
                ultimos_contados = usuarios_unicos

            if sin_cambios >= 3:
                print("✅ Fin de la lista (no aparecen más usuarios).")
                break

        # 5. Extracción Final de Datos
        print("⛏️  Extrayendo detalles de los perfiles...")
        cookies_dict = {c['name']: c['value'] for c in driver.get_cookies()}
        # Lista final enriquecida
        enriquecidos = []
        limite_iter = list(vistos)
        if max_limite:
            limite_iter = limite_iter[:max_limite]

        for uname in limite_iter:
            info = obtener_detalle_perfil(uname, cookies_dict)
            if info:
                enriquecidos.append(info)
            else:
                # Fallback con datos mínimos
                enriquecidos.append({
                    "full_name": "",
                    "username": uname,
                    "biography": "",
                    "account_type": "Personal",
                    "category": "",
                    "follower_count": 0,
                    "following_count": 0,
                    "profile_url": f"https://www.instagram.com/{uname}/",
                    "is_verified": False,
                    "is_private": False,
                })
        datos_obtenidos = enriquecidos

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
    
    # Espera a que el usuario revise el navegador antes de cerrarlo
    input("\n🔒 Revisión lista. Presiona ENTER para cerrar el navegador y finalizar...")
    driver.quit()
    return datos_obtenidos

# --- BLOQUE PRINCIPAL ---
if __name__ == "__main__":
    print("--- EXTRACTOR VISUAL DE INSTAGRAM ---")
    usuario_objetivo = input("👤 Ingresa el usuario objetivo (sin @): ")
    try:
        limite = int(input("🔢 ¿Cuántos quieres extraer? (0 para todos): "))
    except:
        limite = 0
    
    lista_final = extraer_seguidos(usuario_objetivo, max_limite=limite if limite > 0 else None)

    if lista_final:
        df = pd.DataFrame(lista_final).drop_duplicates(subset=['username'])

        # Ordenar columnas si existen
        columnas = [
            'full_name',
            'username',
            'biography',
            'account_type',
            'category',
            'follower_count',
            'following_count',
            'profile_url',
            'is_verified',
            'is_private'
        ]
        columnas_presentes = [c for c in columnas if c in df.columns]
        df = df[columnas_presentes]

        nombre_archivo = f"reporte_seguidos_{usuario_objetivo}.xlsx"
        df.to_excel(nombre_archivo, index=False)
        print(f"\n🎉 Éxito. Guardado en: {nombre_archivo}")
        print(df.head())
    else:
        print("\n⚠️ No se pudieron extraer datos.")

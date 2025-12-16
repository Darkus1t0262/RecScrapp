import instaloader
import pandas as pd
import time
from datetime import datetime

class MiScraperInstaloader:
    def __init__(self):
        # Inicializamos Instaloader
        self.L = instaloader.Instaloader(
            user_agent='Instagram 269.0.0.18.75 Android',
            sleep=True,
            quiet=True
        )

    def login_con_cookies_v2(self, my_username, session_id, csrf_token):
        """
        Inyecta cookies y configura el usuario manualmente para
        satisfacer los chequeos internos de Instaloader.
        """
        print(f"💉 Inyectando sesión para el usuario: {my_username}...")
        try:
            # 1. Inyectamos las cookies en la sesión de requests
            self.L.context._session.cookies.set('sessionid', session_id)
            self.L.context._session.cookies.set('csrftoken', csrf_token)
            
            # 2. SOLUCIÓN AL ERROR: Asignamos el username al contexto.
            # Instaloader calcula 'is_logged_in' automáticamente si esto tiene valor.
            self.L.context.username = my_username
            
            # 3. Verificación rápida intentando obtener tu propio ID
            # Esto confirma que las cookies corresponden al usuario y funcionan.
            print("🔍 Verificando conectividad...")
            profile = instaloader.Profile.from_username(self.L.context, my_username)
            print(f"✅ Login verificado. ID de sesión: {profile.userid}")
            return True
            
        except Exception as e:
            print(f"❌ Error al validar sesión: {e}")
            print("⚠️ Verifica que el Usuario coincida con el SessionID.")
            return False

    def get_following(self, target_username, max_users=None, batch_delay=2, individual_delay=5):
        """Obtiene la lista de seguidos"""
        all_profiles = []
        
        print(f"\n🔄 Buscando perfil objetivo: {target_username}")
        
        try:
            profile = instaloader.Profile.from_username(self.L.context, target_username)
            print(f"✅ Objetivo encontrado: ID {profile.userid}")
            print(f"📊 Seguidos totales (aprox): {profile.followees}")

            print(f"\n🔄 Iniciando extracción...")
            
            followees_iterator = profile.get_followees()

            count = 0
            for person in followees_iterator:
                if max_users and count >= max_users:
                    break

                print(f"[{count + 1}/{max_users or '?'}] @{person.username}", end=" ", flush=True)

                try:
                    # Determinar tipo de cuenta
                    account_type = "Personal"
                    if person.is_business_account:
                        account_type = "Empresa/Creador"
                    
                    user_data = {
                        'full_name': person.full_name,
                        'username': person.username,
                        'biography': person.biography.replace('\n', ' ') if person.biography else '',
                        'account_type': account_type,
                        'category': person.business_category_name or '',
                        'follower_count': person.followers,
                        'following_count': person.followees,
                        'profile_url': f"https://www.instagram.com/{person.username}/",
                        'is_verified': person.is_verified,
                        'is_private': person.is_private
                    }
                    
                    all_profiles.append(user_data)
                    print(f"✓") # Solo check simple para no ensuciar consola
                    
                except Exception as e:
                    print(f"❌ (Error leyendo datos)")
                
                count += 1
                time.sleep(individual_delay)
                
                if count % 50 == 0:
                    print(f"⏳ Pausa de lote ({batch_delay}s)...")
                    time.sleep(batch_delay)

        except instaloader.LoginRequiredException:
            print("❌ Error: Instagram pide login. Tus cookies pueden haber expirado.")
        except instaloader.ProfileNotExistsException:
            print("❌ El perfil no existe.")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")

        return all_profiles

def main():
    print("=" * 60)
    print("SCRAPER INSTALOADER (COOKIES V2 - FIXED) v1.2")
    print("=" * 60)
    print()

    # 1. Datos manuales
    # NECESITAMOS TU USUARIO para que Instaloader valide el contexto
    my_username = input("👤 TU Usuario (dueño de las cookies): ").strip()
    session_id = input("🔑 Tu SessionID: ").strip()
    csrf_token = input("🛡️  Tu CSRF Token: ").strip()
    
    # 2. Objetivo
    target_username = input("\n🎯 Username del OBJETIVO a analizar: ").strip()

    scraper = MiScraperInstaloader()
    
    # Login corregido
    if not scraper.login_con_cookies_v2(my_username, session_id, csrf_token):
        return

    # Configuración
    max_users_input = input("🔢 Máximo usuarios (Enter = sin límite): ").strip()
    max_users = int(max_users_input) if max_users_input else None
    
    # Delays seguros
    batch_delay = 5
    individual_delay = 4 # Un poco más rápido, instaloader es seguro

    # Ejecutar
    profiles = scraper.get_following(
        target_username,
        max_users=max_users,
        batch_delay=batch_delay,
        individual_delay=individual_delay
    )

    # 3. Guardado
    if profiles:
        print(f"\n✅ Extracción completada. {len(profiles)} perfiles.")

        save = input("\n💾 Guardar en Excel? (s/n): ")
        if save.lower() == 's':
            try:
                df = pd.DataFrame(profiles)
                # Ordenar
                cols = ['full_name', 'username', 'biography', 'account_type',
                        'category', 'follower_count', 'following_count',
                        'profile_url', 'is_verified', 'is_private']
                for c in cols: 
                    if c not in df.columns: df[c] = ''
                df = df[cols]

                filename = f"following_{target_username}_{datetime.now().strftime('%H%M%S')}.xlsx"

                with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Data', index=False)
                    # Ajuste ancho columnas
                    ws = writer.sheets['Data']
                    ws.column_dimensions['A'].width = 20
                    ws.column_dimensions['C'].width = 30

                print(f"✅ Guardado: {filename}")

            except Exception as e:
                print(f"❌ Error al guardar: {e}")
    else:
        print("\n❌ No se obtuvieron datos.")

if __name__ == "__main__":
    main()
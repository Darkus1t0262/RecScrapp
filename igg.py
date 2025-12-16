# igg.py
import instaloader
import pandas as pd
from datetime import datetime

TARGET = "esedgarcia"                 # objetivo
SESSIONID = "53368661124%3AY5eDn6Tt51l6Q2%3A21%3AAYif2HcKsSIaOaamfkIqsnfhLIyPEB-AGgmxyRIqXQ"            # cookie sessionid de tu sesión activa
CSRFTOKEN = "WfR-kr-5qOEvMWmCprDvIN"            # copia de la misma sesión
DS_USER_ID = "53368661124"          # opcional, de la misma sesión
LOGGED_USERNAME = "joshepxrodriguez"        # tu username logueado (asociado al sessionid)

def main():
    L = instaloader.Instaloader()
    # inyectar cookies
    L.context._session.cookies.set("sessionid", SESSIONID)
    L.context._session.cookies.set("csrftoken", CSRFTOKEN)
    if DS_USER_ID:
        L.context._session.cookies.set("ds_user_id", DS_USER_ID)
    # informar al contexto quién eres
    L.context.username = LOGGED_USERNAME

    # verificar login
    logged_as = L.test_login()
    if not logged_as:
        raise SystemExit("❌ Login inválido: revisa sessionid/csrftoken/ds_user_id.")
    print(f"✅ Autenticado como {logged_as}")

    profile = instaloader.Profile.from_username(L.context, TARGET)

    rows = []
    for p in profile.get_followees():  # seguidos del objetivo
        rows.append({
            "full_name": p.full_name or "",
            "username": p.username,
            "biography": (p.biography or "").replace("\n", " "),
            "account_type": "Empresa" if getattr(p, "is_business_account", False) else "Personal",
            "category": getattr(p, "business_category_name", "") or "",
            "follower_count": p.followers,
            "following_count": p.followees,
            "profile_url": f"https://www.instagram.com/{p.username}/",
            "is_verified": p.is_verified,
            "is_private": p.is_private,
        })

    df = pd.DataFrame(rows)
    outfile = f"following_{TARGET}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    df.to_excel(outfile, index=False)
    print(f"Guardado: {outfile}")
    print(df.head())

if __name__ == "__main__":
    main()

import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import random
import uuid
import base64
import streamlit.components.v1 as components

st.set_page_config(layout="wide")

st.markdown("""
<style>
div.stButton > button {
    background: linear-gradient(135deg, #e30613, #ff2b2b);
    color: white;
    padding: 16px 45px;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 600;
    border: none;
    box-shadow: 0 10px 25px rgba(227,6,19,0.35);
}
</style>
""", unsafe_allow_html=True)

# CARGAR VARIABLES
load_dotenv()

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Faltan variables del entorno de Supabase")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------------------
# CONTROL DE PANTALLAS
# ---------------------
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "landing"

if st.session_state.pantalla == "landing":

    bg_img = img_to_base64("ilustracion.png")
    logo_img = img_to_base64("acciona_logo.png")

    html = f"""
    <style>
    body {{
        margin: 0;
        font-family: 'Segoe UI', Arial, sans-serif;
    }}

    .hero {{
        width: 100vw;
        height: 100vh;
        background: url("data:image/png;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        display: flex;
    }}

    @media (min-width: 901px) {{
        .hero {{
            position: fixed;
            top: 0;
            left: 0;
            align-items: flex-start;
            padding-top: 120px;
        }}
    }}

    @media (max-width: 900px) {{
        .hero {{
            position: relative;
            align-items: flex-start;
            justify-content: flex-start;
            padding-top: 80px;
            text-align: center;
        }}

        .content {{
            margin-left: 0;
            padding: 0 20px;
        }}

        .title {{
            font-size: clamp(26px, 7vw, 40px);
        }}

        .logo {{
            left: 20px;
            width: 140px;
        }}

    }}

    .hero::after {{
        content: "";
        position: absolute;
        width: 100%;
        height: 100%;
        background: rgba(255,255,255,0.25);
        backdrop-filter: blur(0.5px);
    }}

    .logo {{
        position: absolute;
        top: 30px;
        left: 70px;
        width: 220px;
        z-index: 3;
    }}

    .content {{
        position: relative;
        z-index: 2;
        max-width: 600px;
        margin-left: 80px;
    }}

    .title {{
        font-size: clamp(28px, 5vw, 54px);
        font-weight: 900;
        line-height: 1.05;
        color: #111;
    }}

    .subtitle {{
        font-size: clamp(16px, 2vw, 24px);
        margin-top: 15px;
        color: #555;
    }}

    .btn {{
        margin-top: 40px;
        display: inline-block;
        background: linear-gradient(135deg, #e30613, #ff2b2b);
        color: white;
        padding: 16px 45px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        text-decoration: none;
        box-shadow: 0 10px 25px rgba(227,6,19,0.35);
        transition: all 0.25s ease;
    }}

    .btn:hover {{
        transform: translateY(-4px) scale(1.02);
        box-shadow: 0 15px 35px rgba(227,6,19,0.5);
    }}

    .card {{
        position: absolute;
        background: rgba(255,255,255,0.75);
        backdrop-filter: blur(6px);
        border-radius: 14px;
        width: 240px;
        height: 130px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
        z-index: 1;
    }}

    .card1 {{
        bottom: 90px;
        left: 120px;
    }}

    .card2 {{
        bottom: 70px;
        right: 140px;
    }}

    /* ANIMACION */
    @keyframes fadeIn {{
        from {{
            opacity: 0;
            transform: translateY(30px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}
    </style>

    <div class="hero">

        <img src="data:image/png;base64,{logo_img}" class="logo">

        <div class="content">

            <div class="title">
                <span class="line1">ACCIONA SERVICIOS URBANOS</span> 
                <span class="line2">Y MEDIOAMBIENTALES</span>
            </div>

            <div class="subtitle">
                Sistema de gestión de mantenimiento
            </div>

        </div>

        <div class="card card1"></div>
        <div class="card card2"></div>

    </div>
    """

    valor = components.html(html, height=1000, scrolling=False)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<div style='margin-top:-80px'></div>",
                    unsafe_allow_html=True)

        if st.button("Acceder", key="btn_logic_real", use_container_width=True):
            st.session_state.pantalla = "login"
            st.rerun()

    st.stop()

if st.session_state.pantalla == "login":
    colum1, colum2, colum3 = st.columns([1, 2, 1])

    with colum2:
        st.subheader("👷‍♂️ Login")

        usuario_input = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": usuario_input,
                    "password": password
                })

                if res.user:
                    tecnico_db = supabase.table("tecnicos") \
                        .select("*") \
                        .eq("email", usuario_input) \
                        .execute().data

                    if tecnico_db:
                        st.session_state.user = res.user
                        st.session_state.tipo = "tecnico"
                        st.session_state.tecnico = tecnico_db[0]
                        st.session_state.pantalla = "app"
                        st.rerun()
                    else:
                        st.error("Usuario no registrado.")
            except Exception as e:
                if "Invalid login credentials" in str(e):
                    st.error("Credenciales incorrectas.")
                else:
                    st.error("Error del sistema. Contacte a soporte.")
                    print(e)

        st.markdown("---")

        # ADMIN
        if st.button("Admin", use_container_width=True):
            st.session_state.pantalla = "admin_login"
            st.rerun()

        if st.button("Volver", use_container_width=True):
            st.session_state.pantalla = "landing"
            st.rerun()

    st.stop()

if st.session_state.pantalla == "admin_login":
    column1, column2, column3 = st.columns([2, 2, 2])

    with column2:
        st.subheader("Login Admin")

        email = st.text_input("Correo")
        password = st.text_input("Contraseña", type="password")

        if st.button("Ingresar Admin"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if res.user and res.user.email:
                    st.success("Login correcto")

                    email_login = res.user.email.strip().lower()

                    st.write("Email logeado:", email_login)

                    if email_login == "ethanmijail22@gmail.com":
                        st.session_state.user = res.user
                        st.session_state.tipo = "admin"
                        st.session_state.pantalla = "app"
                        st.rerun()
                    else:
                        st.error("No autorizado")

                else:
                    st.error("No se pudo iniciar sesion")

            except Exception as e:
                if "Invalid login credentials" in str(e):
                    st.error("Usuario o contraseña incorrectas.")
                else:
                    st.error("Error del sistema. Por favor contacta con soporte.")
                    print(e)

        if st.button("⬅️ Volver"):
            st.session_state.pantalla = "login"
            st.rerun()

    st.stop()
# ---------------------
# MODO ADMINISTRADOR
# ---------------------
# ----------------
# LOGIN SUPABASE
# ----------------

usuario = st.session_state.get("user")
tipo = st.session_state.get("tipo")

if not st.session_state.get("user"):
    st.session_state.pantalla = "login"
    st.rerun()


@st.cache_data(ttl=60)
def get_tecnicos():
    return supabase.table("tecnicos").select("*").execute().data


tecnicos = get_tecnicos()

if tipo == "admin":
    st.success("Modo administrador")
    modo = "Admin"
else:
    st.info("Modo tecnico")
    modo = "🌎 General"

with st.sidebar:
    st.markdown("---")
    st.write("Sesion activa")

    if tipo == "admin":
        st.caption(f"Admin: {usuario.email}")
    else:
        st.caption(f"Técnico: {st.session_state.tecnico['nombre']}")

    if st.button("🔒 Cerrar sesion", use_container_width=True):
        supabase.auth.sign_out()
        st.session_state.clear()
        st.session_state.pantalla = "landing"
        st.rerun()

if modo != "Admin":
    tecnico_sel = st.session_state.tecnico

if modo == "Admin":

    tab1, tab2, tab3 = st.tabs([
        "📩 Carga a sistema",
        "👷‍♂️ Vista técnico",
        "📸 Evidencias"
    ])

    # ---------------
    # PRIMERA PESTAÑA
    # ---------------
    with tab1:
        st.subheader("📩 Cargar preventivos desde Máximo")

        archivo = st.file_uploader(
            "Sube archivos de Máximo", type=["csv", "xlsx"])
        if archivo:
            if archivo.name.endswith(".csv"):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            df.columns = df.columns.str.lower().str.strip()
            st.write("Vista previo:", df.head())

            df_carga = pd.DataFrame({
                "numero_ot": df["wonum"],
                "descripcion": df["description"],
                "estatus": "PENDIENTE",
                "tecnico_id": [
                    random.choice(tecnicos)["id"] for _ in range(len(df))
                ]
            })

            if st.button("🚀 Cargar preventivos al sistema"):
                supabase.table("preventivos").insert(
                    df_carga.to_dict(orient="records")).execute()

                st.success(f"✅ {len(df_carga)} preventivos cargados.")

    # ----------------
    # SEGUNDA PESTAÑA
    # ----------------
    with tab2:
        st.subheader("Visualizacion modo técnico.")

        # Selector de técnico
        tec_sel_admin = st.selectbox(
            "Visualizar:",
            tecnicos,
            format_func=lambda x: x["nombre"]
        )

        # Traer preventivos de ese técnico
        prev_admin = supabase.table("preventivos") \
            .select("*") \
            .eq("tecnico_id", tec_sel_admin["id"]) \
            .execute().data

        df_admin_prev = pd.DataFrame(prev_admin)

        st.write(f"Preventivos de {tec_sel_admin['nombre']}")
        st.dataframe(df_admin_prev)

        if not df_admin_prev.empty:
            ot_sel_admin = st.selectbox(
                "Selecciona OT",
                df_admin_prev["numero_ot"],
                key="admin_ot"
            )

            fila = df_admin_prev[df_admin_prev["numero_ot"] == ot_sel_admin]

            if not fila.empty:
                estado_actual = fila.iloc[0]["estatus"]
                evidencia = fila.iloc[0].get("evidencia_url")

                st.write(f"Estado actual: **{estado_actual}**")

                if estado_actual == "REALIZADO":
                    st.warning("Esta OT ya está cerrada")
                if estado_actual == "PENDIENTE":
                    st.info("Esta OT esta abierta")

            # Mostrar evidencia si existe
                if evidencia and pd.notna(evidencia):
                    st.image(evidencia, caption="Evidencia", width=300)

                col1, col2 = st.columns(2)

        # -------------
        # CERRAR OT
        # -------------
                with col1:
                    if st.button("✅ Forzar cierre"):
                        supabase.table("preventivos").update({
                            "estatus": "REALIZADO",
                            "fecha_cierre": datetime.now().date().isoformat()
                        }).eq("numero_ot", ot_sel_admin).execute()

                        st.success("OT cerrada por Admin")
                        st.rerun()

        # -------------
        # REABRIR OT
        # -------------
                with col2:
                    if st.button("🔄️ Reabrir OT"):
                        supabase.table("preventivos").update({
                            "estatus": "PENDIENTE",
                            "fecha_cierre": None
                        }).eq("numero_ot", ot_sel_admin).execute()

                        st.success("OT reabierta")
                        st.rerun()
        else:
            st.warning("No hay preventivos para este tecnico")

    # ---------------
    # TERCERA PESTAÑA
    # ---------------
    with tab3:
        st.subheader("📸 Evidencias")

        tec_ev = st.selectbox(
            "Selecciona técnico",
            tecnicos,
            format_func=lambda x: x["nombre"],
            key="tec_ev"
        )

        prev_ev = supabase.table("preventivos") \
            .select("*") \
            .eq("tecnico_id", tec_ev["id"]) \
            .execute().data

        df_ev = pd.DataFrame(prev_ev)

        if df_ev.empty:
            st.warning("No hay OTs")
            st.stop()

        # Mostrar todas
        st.dataframe(df_ev)

        # SOLO OTs cerradas
        df_cerradas = df_ev[df_ev["estatus"] == "REALIZADO"]

        if df_cerradas.empty:
            st.info("No hay OTs cerradas con evidencia")
            st.stop()

        ot_ev = st.selectbox(
            "Selecciona OT para ver evidencia",
            df_cerradas["numero_ot"]
        )

        fila = df_cerradas[df_cerradas["numero_ot"] == ot_ev]

        evidencia = fila.iloc[0].get("evidencia_url")

        if st.button("Ver evidencia"):
            if evidencia and pd.notna(evidencia):
                st.image(evidencia, caption=f"OT: {ot_ev}", width=400)
            else:
                st.error("Esta OT no tiene evidencia.")

# --------------------
# PUBLICO GENERAL
# --------------------
if modo == "🌎 General":
    st.subheader("👷‍♂️ Vista de colaboradores")

    preventivos = supabase.table("preventivos") \
        .select("*") \
        .eq("tecnico_id", tecnico_sel["id"]) \
        .eq("estatus", "PENDIENTE") \
        .execute().data

    df_prev = pd.DataFrame(preventivos)

    st.dataframe(df_prev)

    if not df_prev.empty:
        ot_sel = st.selectbox(
            "Selecciona OT",
            df_prev["numero_ot"]
        )
        if "ot_actual" not in st.session_state:
            st.session_state.ot_actual = ot_sel

        if st.session_state.ot_actual != ot_sel:
            st.session_state.evidencia_url = None
            st.session_state.ot_actual = ot_sel

        if "evidencia_url" not in st.session_state:
            st.session_state.evidencia_url = None

        # -----------------
        # CARGA DE EVIDENCIAS
        # -----------------
        if "uploader_key" not in st.session_state:
            st.session_state.uploader_key = str(uuid.uuid4())

        archivo_img = st.file_uploader(
            "Subir evidencia",
            type=["jpg", "jpeg", "png"],
            key=st.session_state.uploader_key
        )

        if archivo_img:

            if archivo_img.type not in ["image/jpeg", "image/png", "image/jpg"]:
                st.error("Solo se permiten fotos JPG, PNG o JPEG")
                st.stop()

            nombre_archivo = f"{ot_sel}_{uuid.uuid4().hex}.jpg"

            supabase.storage.from_("evidencias").upload(
                nombre_archivo,
                archivo_img.getvalue()
            )

            evidencia_url = supabase.storage.from_(
                "evidencias").get_public_url(nombre_archivo)
            st.session_state.evidencia_url = evidencia_url

            supabase.table("preventivos").update({
                "evidencia_url": evidencia_url
            }).eq("numero_ot", ot_sel).execute()

            st.success("📸 Evidencia subida")

            # Automatic reset
            st.session_state.uploader_key = str(uuid.uuid4())
        # ------------------
        # BOTON COMPLETAR
        # ------------------
        if st.button("✅ Marcar como realizado"):
            if not st.session_state.get("evidencia_url"):
                st.error("⚠️ Debes subir una evidencia antes de cerrar.")
            else:
                supabase.table("preventivos").update({
                    "estatus": "REALIZADO",
                    "fecha_cierre": datetime.now().date().isoformat(),
                    "evidencia_url": st.session_state.evidencia_url
                }).eq("numero_ot", ot_sel).execute()

                # LIMPIAR ESTADO
                st.session_state.evidencia_url = None

                st.success("OT cerrada")
                st.rerun()

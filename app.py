import streamlit as st
import pandas as pd
from supabase import create_client
import re
from dotenv import load_dotenv
from datetime import datetime, timezone, date, timedelta
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


def mostrar_detalle_ejecucion(fecha_inicio, fecha_cierre):
    if not fecha_inicio or pd.isna(fecha_inicio):
        st.warning("Sin fecha de inicio")
        return

    tz = "America/Mexico_City"

    try:
        inicio = pd.to_datetime(fecha_inicio, utc=True).tz_convert(tz)
    except Exception as e:
        st.error(f"Error fecha inicio: {e}")
        return

    inicio_fmt = inicio.strftime("%d/%m/%Y %I:%M %p")
    fin_fmt = "En proceso"
    duracion_fmt = "Calculando..."

    if fecha_cierre and pd.notna(fecha_cierre):
        try:
            cierre = pd.to_datetime(fecha_cierre, utc=True).tz_convert(tz)
            fin_fmt = cierre.strftime("%d/%m/%Y %I:%M %p")
            duracion = cierre - inicio

            if duracion.total_seconds() >= 0:
                total_segundos = int(duracion.total_seconds())
                dias = total_segundos // 86400
                horas = (total_segundos % 86400) // 3600
                minutos = (total_segundos % 3600) // 60

                duracion_fmt = f"{dias} días, {horas}horas, {minutos}min"
            else:
                duracion_fmt = "Error: Cierre antes de inicio"
        except Exception as e:
            fin_fmt = "Error leyendo fecha"
            duracion_fmt = str(e)

    html = f"""
    <div style="
        background:white;
        padding:25px;
        border-radius:18px;
        box-shadow:0 6px 20px rgba(0,0,0,0.08);
        margin:20px 0;
    ">
        <h2>Detalle de ejecución</h2>
        <p><b>Inicio:</b> {inicio_fmt}</p>
        <p><b>Fin:</b> {fin_fmt}</p>
        <p><b>Duración:</b> {duracion_fmt}</p>
    </div>
    """
    components.html(html, height=220)


def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def guardar_anotaciones_si_hay_cambios(ot_sel, texto_db):
    key = f"anotaciones_{ot_sel}"

    texto_actual = st.session_state.get(key, "")
    texto_actual = str(texto_actual or "").strip()
    texto_db = str(texto_db or "").strip()

    if texto_actual != texto_db:
        supabase.table("preventivos").update({
            "anotaciones": texto_actual
        }).eq("numero_ot", ot_sel).execute()


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

    .line1 {{
        display: block;
    }}

    .line2 {{
        display: block;
        margin-top: 5px;
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
                    tecnico_db = (
                        supabase.table("tecnicos")
                        .select("*")
                        .eq("email", usuario_input)
                        .execute()
                        .data
                    )

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
    return (
        supabase.table("tecnicos")
        .select("*")
        .eq("activo", True)
        .execute()
        .data
    )


tecnicos = get_tecnicos()

if tipo == "admin":
    st.success("Modo administrador")
    modo = "Admin"
else:
    st.info("Modo tecnico")
    modo = "General"

with st.sidebar:
    st.markdown("---")
    st.write("Sesion activa")

    if tipo == "admin":
        st.caption(f"Admin: {usuario.email}")
    else:
        st.caption(f"Técnico: {st.session_state.tecnico['nombre']}")

    if st.button("🔒 Cerrar sesion", use_container_width=True):
        if modo == "General":
            tecnico_actual = st.session_state.tecnico

            preventivos_abiertos = supabase.table("preventivos") \
                .select("numero_ot, anotaciones") \
                .eq("tecnico_id", tecnico_actual["id"]) \
                .eq("estatus", "EN PROCESO") \
                .execute().data

            for prev in preventivos_abiertos:
                guardar_anotaciones_si_hay_cambios(
                    prev["numero_ot"],
                    prev.get("anotaciones")
                )

        supabase.auth.sign_out()
        st.session_state.clear()
        st.session_state.pantalla = "landing"
        st.rerun()

if modo != "Admin":
    tecnico_sel = st.session_state.tecnico

if modo == "Admin":

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Carga a sistema",
        "Vista técnico",
        "Evidencias",
        "Job Plans",
        "Tecnicos",
        "Roles"
    ])

    # ---------------
    # PRIMERA PESTAÑA
    # ---------------
    with tab1:
        st.subheader("📩 Cargar preventivos desde Máximo")
        st.markdown("---")
        st.subheader("Descargar preventivos cerrados")
        preventivos_realizados = supabase.table("preventivos") \
            .select("*") \
            .eq("estatus", "REALIZADO") \
            .execute().data
        if preventivos_realizados:
            df_realizados = pd.DataFrame(preventivos_realizados)

            csv = df_realizados.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="Descargar CSV OT realizadas",
                data=csv,
                file_name=f"preventivos_realizados_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No hay preventivos cerrados")

        archivo = st.file_uploader(
            "Sube archivos de Máximo", type=["csv", "xlsx"])
        if archivo:
            if archivo.name.endswith(".csv"):
                df = pd.read_csv(archivo)
            else:
                df = pd.read_excel(archivo)

            df.columns = df.columns.str.lower().str.strip()
            st.write("Vista previo:", df.head())

            datos_carga = []
            no_asignados = []

            tecnico_cba = next(
                (t for t in tecnicos
                 if t["nombre"] == "Isaac Zamudio"),
                None
            )
            if not tecnico_cba:
                st.error("No se encontro tecnico CBA")
                st.stop()

            fontaneros = [
                t for t in tecnicos
                if t["area"] == "FONTANERIA"
                and t["id"] != tecnico_cba["id"]
            ]

            cuota_fontaneria = {
                t["id"]: 2 for t in fontaneros
            }

            carga_temporal = {
                t["id"]: 0
                for t in tecnicos
                if t["id"] != tecnico_cba["id"]
            }

            tecnico_marin = next(
                (t for t in tecnicos if t["nombre"] == "Alejandro Marin"),
                None
            )

            PM_MARIN = "IFMSI006"
            PM_SEGUNDO_TURNO = ["IFMSI214"]
            PM_PRIMER_TURNO = ["IFMSI210"]

            def limpiar_turno(turno):
                return str(turno).strip().replace(".0", "")

            for _, row in df.iterrows():

                location = str(row["location"]).upper()
                descripcion = str(row["description"]).upper()
                pmnum = str(row.get("pmnum")).strip().upper()
                fecha_raw = str(row.get("schedfinish", "")).strip()
                match = re.search(
                    r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})',
                    fecha_raw
                )
                if match:
                    fecha_raw = match.group(1)
                schedfinish = pd.to_datetime(
                    fecha_raw,
                    format="%b %d, %Y",
                    errors="coerce"
                )

                if "NODO" in descripcion:
                    no_asignados.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "motivo": "JCI"
                    })
                    continue

                partes_location = location.split()
                codigo_sede = location.split()[-1].strip()

                mapa_sedes = {
                    "ANG": "El Angel",
                    "BA": "Bellas Artes",
                    "CLC": "CLC",
                    "P.P": "Popopiramides",
                    "PIN": "Pintura",
                    "CBA": "CBA"
                }

                sede = mapa_sedes.get(codigo_sede, codigo_sede)

                if ("CBA" in descripcion or codigo_sede == "CBA") and "IFSI" not in location:
                    datos_carga.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "jpnum": str(row["jpnum"]).strip() if pd.notna(row.get("jpnum")) else None,
                        "pmnum": pmnum,
                        "estatus": "PENDIENTE",
                        "tecnico_id": tecnico_cba["id"],
                        "sede": sede,
                        "schedfinish": (
                            schedfinish.date().isoformat()
                            if pd.notna(schedfinish)
                            else None
                        )
                    })
                    continue

                # ---------------
                # SCI
                # ---------------
                if "IFSI" in location:

                    # CCTV MARIN
                    if pmnum == PM_MARIN:

                        if tecnico_marin:
                            datos_carga.append({
                                "numero_ot": row["wonum"],
                                "descripcion": row["description"],
                                "jpnum": str(row["jpnum"]).strip() if pd.notna(row.get("jpnum")) else None,
                                "pmnum": pmnum,
                                "estatus": "PENDIENTE",
                                "tecnico_id": tecnico_marin["id"],
                                "sede": sede,
                                "schedfinish": (
                                    schedfinish.date().isoformat()
                                    if pd.notna(schedfinish)
                                    else None
                                )
                            })
                        continue

                    # SOLO SEGUNDO TURNO
                    elif (
                        pmnum in PM_SEGUNDO_TURNO
                        or "C-IFSI-CBA" in location
                        or "C-IFSI-CLC" in location
                    ):
                        candidatos = [
                            t for t in tecnicos
                            if t["area"] == "SCI"
                            and limpiar_turno(t.get("turno_actual")) == "2"
                            and t["id"] != tecnico_cba["id"]
                        ]

                    # SOLO PRIMER TURNO
                    elif pmnum in PM_PRIMER_TURNO:
                        candidatos = [
                            t for t in tecnicos
                            if t["area"] == "SCI"
                            and limpiar_turno(t.get("turno_actual")).strip() == "1"
                            and t["id"] != tecnico_cba["id"]
                        ]

                    # ----------
                    # RESTO SCI
                    # ----------
                    else:
                        candidatos = [
                            t for t in tecnicos
                            if t["area"] == "SCI"
                            and t["id"] != tecnico_cba["id"]
                        ]

                # ----------------
                # IFCO
                # ----------------
                elif "IFCO" in location:
                    candidatos = [
                        t for t in tecnicos
                        if t["area"] in ["COCINAS", "CONSERVACION"]
                        and t["id"] != tecnico_cba["id"]
                    ]

                # ----------------
                # IFFA
                # ----------------
                elif "IFFA" in location:

                    fontaneros_pendientes = [
                        t for t in fontaneros
                        if cuota_fontaneria[t["id"]] > 0
                    ]

                    if fontaneros_pendientes:
                        candidatos = fontaneros_pendientes
                    else:
                        candidatos = [
                            t for t in tecnicos
                            if t["area"] in ["COCINAS", "CONSERVACION"]
                            and t["id"] != tecnico_cba["id"]
                        ]

                # ---------------
                # NO ASIGNAR
                # ---------------
                elif "IFVI" in location or "IFDE" in location:
                    no_asignados.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "motivo": "PROVEEDOR"
                    })
                    continue

                else:
                    no_asignados.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "motivo": "Sin regla de asignacion"
                    })
                    continue

                if not candidatos:
                    no_asignados.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "motivo": "No hay tecnico disponible"
                    })
                    continue

                min_carga = min(carga_temporal[t["id"]] for t in candidatos)

                tecnicos_disponibles = [
                    t for t in candidatos
                    if carga_temporal[t["id"]] == min_carga
                ]

                tecnico_asignado = random.choice(tecnicos_disponibles)

                # Actualizar contador
                carga_temporal[tecnico_asignado["id"]] += 1

                if tecnico_asignado["area"] == "FONTANERIA":
                    cuota_fontaneria[tecnico_asignado["id"]] -= 1

                jpnum_val = row.get("jpnum")

                if pd.notna(jpnum_val):
                    jpnum_val = str(jpnum_val).strip()
                else:
                    jpnum_val = None

                datos_carga.append({
                    "numero_ot": row["wonum"],
                    "descripcion": row["description"],
                    "jpnum": jpnum_val,
                    "pmnum": pmnum,
                    "estatus": "PENDIENTE",
                    "tecnico_id": tecnico_asignado["id"],
                    "sede": sede,
                    "schedfinish": (
                        schedfinish.date().isoformat()
                        if pd.notna(schedfinish)
                        else None
                    )
                })

            df_carga = pd.DataFrame(datos_carga)

            if st.button("Actualizar sedes de preventivos existentes"):

                actualizados = 0

                mapa_sedes = {
                    "ANG": "El Angel",
                    "BA": "Bellas Artes",
                    "CLC": "CLC",
                    "P.P": "Popopiramides",
                    "PIN": "Pintura",
                    "CBA": "CBA"
                }

                for _, row in df.iterrows():

                    location = str(row["location"]).upper()
                    partes = location.split()
                    codigo_sede = partes[-1] if partes else None

                    sede = mapa_sedes.get(codigo_sede, codigo_sede)

                    supabase.table("preventivos").update({
                        "sede": sede
                    }).eq("numero_ot", row["wonum"]).execute()

                actualizados += 1

                st.success(f"{actualizados} preventivos actualizados")

            if st.button("Actualizar fechas programadas"):
                actualizados = 0

                for _, row in df.iterrows():
                    fecha_raw = str(row.get("schedfinish", "")).strip()
                    match = re.search(
                        r'([A-Za-z]{3}\s+\d{1,2},\s+\d{4})',
                        fecha_raw
                    )
                    if match:
                        fecha_raw = match.group(1)
                    schedfinish = pd.to_datetime(
                        fecha_raw,
                        format="%b %d, %Y",
                        errors="coerce"
                    )

                    supabase.table("preventivos").update({
                        "schedfinish": (
                            schedfinish.date().isoformat()
                            if pd.notna(schedfinish)
                            else None
                        )
                    }).eq(
                        "numero_ot",
                        row["wonum"]
                    ).execute()

                    actualizados += 1
                    st.success(
                        f"{actualizados} OTS actualizadas"
                    )

            if st.button("Cargar preventivos al sistema"):

                existentes = supabase.table("preventivos") \
                    .select("numero_ot") \
                    .execute().data
                ots_existentes = {x["numero_ot"] for x in existentes}

                nuevos = [
                    row for row in df_carga.to_dict(orient="records")
                    if row["numero_ot"] not in ots_existentes
                ]

                if nuevos:
                    supabase.table("preventivos").insert(nuevos).execute()

                supabase.table("preventivos_no_asignados") \
                    .delete() \
                    .neq("numero_ot", "") \
                    .execute()

                if no_asignados:
                    for item in no_asignados:
                        item["fecha_carga"] = datetime.now(
                            timezone.utc).isoformat()

                    supabase.table("preventivos_no_asignados") \
                        .insert(no_asignados) \
                        .execute()

                st.success(
                    f"{len(nuevos)} preventivos cargados | "
                    f"{len(no_asignados)} no asignados"
                )

    # ----------------
    # SEGUNDA PESTAÑA
    # ----------------
    with tab2:
        st.subheader("Visualizacion modo técnico.")

        col1, col2 = st.columns([1, 2])

        with col1:
            tec_sel_admin = st.selectbox(
                "Visualizar:",
                tecnicos,
                format_func=lambda x: x["nombre"]
            )

        with col2:
            rango = st.date_input(
                "Periodo",
                value=(
                    date.today() - timedelta(days=7),
                    date.today()
                )
            )
        # Traer preventivos
        prev_admin = supabase.table("preventivos") \
            .select("*") \
            .eq("tecnico_id", tec_sel_admin["id"]) \
            .execute().data

        df_admin_prev = pd.DataFrame(prev_admin)

        try:
            if (
                not df_admin_prev.empty
                and len(rango) == 2
                and "schedfinish" in df_admin_prev.columns
            ):

                inicio = pd.to_datetime(rango[0]).date()
                fin = pd.to_datetime(rango[1]).date()

                df_admin_prev["schedfinish"] = pd.to_datetime(
                    df_admin_prev["schedfinish"],
                    errors="coerce"
                )

                df_admin_prev = df_admin_prev.dropna(
                    subset=["schedfinish"]
                )
                if not df_admin_prev.empty:
                    df_admin_prev["schedfinish_date"] = (
                        df_admin_prev["schedfinish"].dt.date
                    )

                    st.write("COLUMNAS:")
                    st.write(df_admin_prev.columns.tolist())

                    st.write("TIPO schedfinish:")
                    st.write(df_admin_prev["schedfinish"].dtype)

                    st.write("PRIMEROS VALORES:")
                    st.write(df_admin_prev["schedfinish"].head())
                    df_admin_prev = df_admin_prev[
                        (
                            df_admin_prev["schedfinish_date"] >= inicio
                        )
                        &
                        (
                            df_admin_prev["schedfinish_date"] <= fin
                        )
                    ]
        except Exception as e:
            st.warning(
                f"No fue posible aplicar filtro de fechas: {e}"
            )

        st.write(f"Preventivos de {tec_sel_admin['nombre']}")
        st.dataframe(
            df_admin_prev[
                [
                    "numero_ot",
                    "descripcion",
                    "sede",
                    "estatus",
                    "schedfinish"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

        if not df_admin_prev.empty:
            ot_sel_admin = st.selectbox(
                "Selecciona OT",
                df_admin_prev["numero_ot"],
                key="admin_ot"
            )

            fila = df_admin_prev[df_admin_prev["numero_ot"] == ot_sel_admin]

            if not fila.empty:
                estado_actual = fila.iloc[0]["estatus"]
                evidencia_inicio = fila.iloc[0].get("evidencia_inicio_url")
                evidencia_fin = fila.iloc[0].get("evidencia_fin_url")

                anotaciones = fila.iloc[0].get("anotaciones")
                fecha_inicio = fila.iloc[0].get("fecha_inicio")
                fecha_cierre = fila.iloc[0].get("fecha_cierre")

                st.write(f"Estado actual: **{estado_actual}**")

                if estado_actual == "REALIZADO":
                    st.warning("Esta OT ya está cerrada")
                elif estado_actual == "PENDIENTE":
                    st.info("Esta OT esta abierta")
                elif estado_actual == "EN PROCESO":
                    st.info("Esta OT está en proceso")

            # Mostrar evidencia si existe
                st.markdown("---")
                mostrar_detalle_ejecucion(fecha_inicio, fecha_cierre)

                if anotaciones:
                    st.text_area(
                        "Anotaciones del tecnico",
                        value=anotaciones,
                        height=150,
                        disabled=True
                    )

                col_ev1, col_ev2 = st.columns(2)

                with col_ev1:
                    if evidencia_inicio and isinstance(evidencia_inicio, str) and evidencia_inicio.startswith("http"):
                        try:
                            st.image(
                                evidencia_inicio,
                                caption="Antes de iniciar",
                                use_container_width=True
                            )
                        except Exception:
                            st.info("Evidencia inicial invalida")
                    else:
                        st.info("Sin evidencia inicial")

                with col_ev2:
                    if evidencia_fin and isinstance(evidencia_fin, str) and evidencia_fin.startswith("http"):
                        try:
                            st.image(
                                evidencia_fin,
                                caption="Despues de finalizar",
                                use_container_width=True
                            )
                        except Exception:
                            st.info("Evidencia final invalida")
                    else:
                        st.info("Sin evidencia final")

                col1, col2 = st.columns(2)

        # -------------
        # CERRAR OT
        # -------------
                with col1:
                    if st.button("✅ Forzar cierre"):
                        supabase.table("preventivos").update({
                            "estatus": "REALIZADO",
                            "fecha_cierre": datetime.now(timezone.utc).isoformat()
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
                            "fecha_inicio": None,
                            "fecha_cierre": None,
                            "evidencia_inicio_url": None,
                            "evidencia_fin_url": None,
                            "anotaciones": None
                        }).eq("numero_ot", ot_sel_admin).execute()

                        st.success("OT reabierta")
                        st.rerun()
        else:
            st.warning("No hay preventivos para este tecnico")

    # ---------------
    # TERCERA PESTAÑA
    # ---------------
    with tab3:
        st.subheader("Auditoría")

        termino = st.text_input(
            "Buscar por número OT, descripción o sede",
            placeholder="Ej: A86354164, baños, comedor, CLC..."
        )

        if termino:
            termino = termino.strip()

            resultados = supabase.table("preventivos") \
                .select("*") \
                .or_(
                    f"numero_ot.ilike.%{termino}%,"
                    f"descripcion.ilike.%{termino}%,"
                    f"sede.ilike.%{termino}%"
            ) \
                .execute().data

            df_resultados = pd.DataFrame(resultados)

            if df_resultados.empty:
                st.warning("No se encontraron preventivos.")
            else:
                st.dataframe(
                    df_resultados[[
                        "numero_ot",
                        "descripcion",
                        "sede",
                        "estatus"
                    ]],
                    use_container_width=True,
                    hide_index=True
                )

                ot_sel_audit = st.selectbox(
                    "Selecciona OT para auditoría",
                    df_resultados["numero_ot"],
                    key="auditoria_ot"
                )

                fila = df_resultados[
                    df_resultados["numero_ot"] == ot_sel_audit
                ]

                if not fila.empty:
                    estado_actual = fila.iloc[0]["estatus"]
                    evidencia_inicio = fila.iloc[0].get("evidencia_inicio_url")
                    evidencia_fin = fila.iloc[0].get("evidencia_fin_url")
                    anotaciones = fila.iloc[0].get("anotaciones")
                    fecha_inicio = fila.iloc[0].get("fecha_inicio")
                    fecha_cierre = fila.iloc[0].get("fecha_cierre")
                    tecnico_id = fila.iloc[0].get("tecnico_id")

                    tecnico_nombre = "Sin asignar"

                    if tecnico_id:
                        tecnico = supabase.table("tecnicos") \
                            .select("nombre") \
                            .eq("id", tecnico_id) \
                            .execute().data

                        if tecnico:
                            tecnico_nombre = tecnico[0]["nombre"]

                    st.markdown("---")

                    st.write(f"**OT:** {ot_sel_audit}")
                    st.write(f"**Estado:** {estado_actual}")
                    st.write(f"**Técnico asignado:** {tecnico_nombre}")

                    mostrar_detalle_ejecucion(
                        fecha_inicio,
                        fecha_cierre
                    )

                    if anotaciones:
                        st.text_area(
                            "Anotaciones del técnico",
                            value=anotaciones,
                            height=180,
                            disabled=True
                        )
                    else:
                        st.info("Sin anotaciones")

                    col1, col2 = st.columns(2)

                    with col1:
                        if evidencia_inicio and isinstance(evidencia_inicio, str) and evidencia_inicio.startswith("http"):
                            try:
                                st.image(
                                    evidencia_inicio,
                                    caption="Evidencia inicial",
                                    use_container_width=True
                                )
                            except Exception:
                                st.info("Evidencia incial invalida")
                        else:
                            st.info("Sin evidencia inicial")

                    with col2:
                        if evidencia_fin and isinstance(evidencia_fin, str) and evidencia_fin.startswith("http"):
                            try:
                                st.image(
                                    evidencia_fin,
                                    caption="Evidencia final",
                                    use_container_width=True
                                )
                            except Exception:
                                st.info("Evidencia final invalida")
                        else:
                            st.info("Sin evidencia final")

        st.markdown("---")
        st.subheader("Preventivos no asignados")

        no_asignados_db = supabase.table("preventivos_no_asignados") \
            .select("*") \
            .order("fecha_carga", desc=True) \
            .execute().data

        if no_asignados_db:
            df_no = pd.DataFrame(no_asignados_db)

            st.dataframe(
                df_no[["numero_ot", "descripcion", "motivo", "fecha_carga"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No hay preventivos sin asignar")

    with tab4:

        st.subheader("📑 Cargar Job Plan Tasks")

        archivo_jp = st.file_uploader(
            "Sube Excel de Job Plan",
            type=["xlsx"]
        )

        if archivo_jp:
            excel_file = pd.ExcelFile(archivo_jp)
            hojas = excel_file.sheet_names

            todas_tareas = []
            for hoja in hojas:
                df_excel = pd.read_excel(
                    archivo_jp,
                    sheet_name=hoja,
                    header=None
                )

                # -----------------
                # OBTENER JPNUM
                # -----------------
                import re

                jpnum = None

                for _, row in df_excel.iterrows():
                    for valor in row:
                        texto = str(valor)

                        match = re.search(r'JPNUM[:\s]*([0-9]+)', texto)

                        if match:
                            jpnum = match.group(1)
                            break

                    if jpnum:
                        break

                if not jpnum:
                    st.error("No se pudo detectar el JPNUM")
                    st.stop()

                st.success(f"JP Detectado: {jpnum}")

                # -------------------------
                # ENCONTRAR INICIO DE TASKS
                # -------------------------
                inicio_tasks = None

                for i, row in df_excel.iterrows():

                    if "TASK ID" in str(row[0]).upper():
                        inicio_tasks = i + 1
                        break

                tareas = []

                if inicio_tasks:

                    i = inicio_tasks

                    while i < len(df_excel):
                        secuencia = df_excel.iloc[i, 0]
                        descripcion = df_excel.iloc[i, 1]

                        if pd.isna(secuencia) and pd.isna(descripcion):
                            i += 1
                            continue

                        if pd.notna(secuencia):

                            try:
                                secuencia = int(secuencia)
                                texto_completo = str(descripcion).strip()

                                # Leer filas inferiores
                                j = i + 1

                                while j < len(df_excel):
                                    siguiente_sec = df_excel.iloc[j, 0]
                                    texto_extra = df_excel.iloc[j, 1]

                                    # Si encuentra nueva secuencia -> termina
                                    if pd.notna(siguiente_sec):
                                        break

                                    # Agregar texto adicional
                                    if pd.notna(texto_extra):
                                        texto_completo += "\n" + \
                                            str(texto_extra).strip()

                                    j += 1

                                todas_tareas.append({
                                    "jpnum": str(jpnum),
                                    "secuencia": secuencia,
                                    "tarea": texto_completo
                                })

                                i = j

                            except Exception as e:
                                st.warning(f"Fila ignorada: {e}")
                                i += 1
                        else:
                            i += 1

            # -----------------
            # FINAL DATAFRAME
            # -----------------
            df_tareas = pd.DataFrame(todas_tareas)
            st.dataframe(df_tareas)

            # ------------
            # GUARDAR
            # ------------

            if st.button("Guardar Job Plan"):

                insertados = 0

                for jp in df_tareas["jpnum"].unique():
                    existente = supabase.table("jobplan_tareas") \
                        .select("jpnum") \
                        .eq("jpnum", jp) \
                        .execute().data

                    if existente:
                        continue

                    datos_jp = df_tareas[
                        df_tareas["jpnum"] == jp
                    ]

                    supabase.table("jobplan_tareas").insert(
                        datos_jp.to_dict(orient="records")
                    ).execute()

                    insertados += 1

                st.success(f"{len(df_tareas)} tareas guardadas.")

    with tab5:
        st.subheader("Gestion de personal")

        tecnicos_todos = (
            supabase.table("tecnicos")
            .select("*")
            .execute()
            .data
        )

        for tecnico in tecnicos_todos:

            col1, col2 = st.columns([3, 1])

            with col1:
                estado = "Activo" if tecnico["activo"] else "Inactivo"
                st.write(f"{tecnico['nombre']} - {tecnico['area']} - {estado}")

            with col2:
                nuevo_estado = st.toggle(
                    "Activo",
                    value=tecnico["activo"],
                    key=f"tec_{tecnico['id']}"
                )

                if nuevo_estado != tecnico["activo"]:
                    supabase.table("tecnicos").update({
                        "activo": nuevo_estado
                    }).eq("id", tecnico["id"]).execute()

                    st.cache_data.clear()
                    st.rerun()

    with tab6:
        st.subheader("Actualizar rol de turno")

        archivo_roles = st.file_uploader(
            "Carga archivo de roles",
            type=["xlsx"],
            key="roles_excel"
        )

        if archivo_roles:
            from openpyxl import load_workbook

            wb = load_workbook(archivo_roles, data_only=True)
            ws = wb.active

            fila_header = None

            for fila in ws.iter_rows(min_row=1, max_row=30):
                valores = [
                    str(cell.value).strip().upper()
                    for cell in fila
                    if cell.value is not None
                ]

                if "NOMBRE" in valores and "TURNO" in valores:
                    fila_header = fila[0].row
                    break

            st.write("Fila detectada:", fila_header)

            if fila_header is None:
                st.error("No se encontró encabezado")
                st.stop()

            datos = list(ws.values)

            encabezados = [
                str(x).strip().upper() if x is not None else ""
                for x in datos[fila_header - 1]
            ]

            df_roles = pd.DataFrame(
                datos[fila_header:],
                columns=encabezados
            )

            df_roles = df_roles[
                (df_roles["NOMBRE"].notna()) &
                (df_roles["TURNO"].notna())
            ]

            st.dataframe(df_roles[["NOMBRE", "TURNO"]], hide_index=True)

            def limpiar_texto(txt):
                txt = str(txt)
                txt = txt.replace("\xa0", " ")
                txt = str(txt).upper().strip()
                txt = re.sub(r"\s+", " ", txt)
                return txt

            if st.button("Actualizar turnos:"):
                actualizados = 0
                no_encontrados = []

                tecnicos_db = supabase.table("tecnicos").select(
                    "id,nombre_nomina"
                ).execute().data

                mapa_tecnicos = {}

                for t in tecnicos_db:
                    nombre_limpio = limpiar_texto(t["nombre_nomina"])
                    mapa_tecnicos[nombre_limpio] = t["id"]

                for _, row in df_roles.iterrows():
                    nombre_excel = limpiar_texto(row["NOMBRE"])
                    turno = str(row["TURNO"]).strip()

                    if nombre_excel in ["", "NAN", "NONE"]:
                        continue

                    tecnico_id = mapa_tecnicos.get(nombre_excel)

                    if tecnico_id:
                        supabase.table("tecnicos").update({
                            "turno_actual": turno
                        }).eq("id", tecnico_id).execute()

                        actualizados += 1
                    else:
                        no_encontrados.append(nombre_excel)

                st.success(f"{actualizados} técnicos actualizados")

                if no_encontrados:
                    st.warning("No encontrados:")
                    st.write(no_encontrados)
                st.cache_data.clear()

# --------------------
# PUBLICO GENERAL
# --------------------
if "confirmar_cierre_ot" not in st.session_state:
    st.session_state.confirmar_cierre_ot = None

if modo == "General":
    st.subheader("👷‍♂️ Vista de colaboradores")

    preventivos = supabase.table("preventivos") \
        .select("*") \
        .eq("tecnico_id", tecnico_sel["id"]) \
        .in_("estatus", ["PENDIENTE", "EN PROCESO"]) \
        .execute().data

    df_prev = pd.DataFrame(preventivos)

    if not df_prev.empty:
        st.dataframe(
            df_prev[[
                "numero_ot",
                "descripcion",
                "sede",
                "estatus"
            ]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No tienes OTs pendientes. Gracias por tu trabajo. 🙂")

    if not df_prev.empty:
        ot_sel = st.selectbox(
            "Selecciona OT",
            df_prev["numero_ot"]
        )
        fila_ot = df_prev[df_prev["numero_ot"] == ot_sel]

        jpnum_ot = fila_ot.iloc[0]["jpnum"]
        jpnum_ot = str(jpnum_ot).strip()

        tareas_jp = supabase.table("jobplan_tareas") \
            .select("*") \
            .eq("jpnum", str(jpnum_ot)) \
            .order("secuencia") \
            .execute().data

        with st.expander("Detalles de tarea"):
            if tareas_jp:
                for tarea in tareas_jp:
                    st.markdown(
                        f"**{tarea['secuencia']}** - {tarea['tarea']}"
                    )
            else:
                st.warning(
                    "No hay Job Plan cargado. Comuniquese con su planner.")

        estado_ot = fila_ot.iloc[0]["estatus"]

        # --------------
        # OT PENDIENTE
        # --------------
        if estado_ot == "PENDIENTE":
            st.warning("Tarea aun no iniciada")

            foto_inicio = st.file_uploader(
                "Sube foto iniciando actividad",
                type=["jpg", "jpeg", "png"],
                key=f"inicio_{ot_sel}"
            )

            if st.button("Iniciar tarea"):

                if not foto_inicio:
                    st.error("Debes subir una foto inicial de la actividad.")
                else:
                    nombre_inicio = f"INICIO_{ot_sel}_{uuid.uuid4().hex}.jpg"

                    supabase.storage.from_("evidencias").upload(
                        nombre_inicio,
                        foto_inicio.getvalue()
                    )

                    url_inicio = supabase.storage.from_(
                        "evidencias"
                    ).get_public_url(nombre_inicio)

                    supabase.table("preventivos").update({
                        "estatus": "EN PROCESO",
                        "evidencia_inicio_url": url_inicio,
                        "fecha_inicio": datetime.now(timezone.utc).isoformat()
                    }).eq("numero_ot", ot_sel).execute()

                    st.success("Tarea iniciada ✅")
                    st.rerun()

        # ---------------
        # OT EN PROCESO
        # ---------------
        elif estado_ot == "EN PROCESO":
            st.info("Tarea en proceso")

            evidencia_inicio = fila_ot.iloc[0].get("evidencia_inicio_url")
            evidencia_fin = fila_ot.iloc[0].get("evidencia_fin_url")
            anotacion_actual = str(fila_ot.iloc[0].get("anotaciones") or "")

            key_anot = f"anotaciones_{ot_sel}"
            if key_anot not in st.session_state:
                st.session_state[key_anot] = str(anotacion_actual or "")

            # --------------
            # FOTO INICIAL
            # --------------
            if evidencia_inicio and isinstance(evidencia_inicio, str) and evidencia_inicio.startswith("http"):
                try:
                    st.image(
                        evidencia_inicio,
                        caption="Foto inicial",
                        width=200
                    )

                    if st.button("Reemplazar foto inicial"):
                        guardar_anotaciones_si_hay_cambios(
                            ot_sel,
                            anotacion_actual
                        )

                        supabase.table("preventivos").update({
                            "evidencia_inicio_url": None
                        }).eq("numero_ot", ot_sel).execute()

                        st.session_state[key_anot] = str(
                            st.session_state.get(key_anot, ""))
                        st.success("Ahora sube la nueva foto incial")
                        st.rerun()

                except Exception:
                    st.warning(
                        "La evidencia inicial esta corrupta o es invalida")
                    evidencia_inicio = None

            else:
                st.warning("La evidencia inicial es inválida o inexistente")

                nueva_inicio = st.file_uploader(
                    "Sube foto inicial",
                    type=["jpg", "png", "jpeg"],
                    key=f"reemplazo_inicio_{ot_sel}"
                )

                if st.button("Guardar nueva foto incial"):
                    if not nueva_inicio:
                        st.error("Debes subir una evidencia")
                    else:
                        nombre_inicio = f"INICIO_{ot_sel}_{uuid.uuid4().hex}.jpg"

                        supabase.storage.from_("evidencias").upload(
                            nombre_inicio,
                            nueva_inicio.getvalue()
                        )

                        url_inicio = supabase.storage.from_(
                            "evidencias"
                        ).get_public_url(nombre_inicio)

                        supabase.table("preventivos").update({
                            "evidencia_inicio_url": url_inicio
                        }).eq("numero_ot", ot_sel).execute()

                        st.session_state[key_anot] = str(
                            st.session_state.get(key_anot, ""))
                        st.success("Foto inicial reemplazada")
                        st.rerun()

            # --------------
            # ANOTACIONES
            # --------------
            key_anot = f"anotaciones_{ot_sel}"

            anotaciones = st.text_area(
                "Anotaciones de la actividad",
                key=key_anot,
                height=150,
                placeholder="Ejemplo: Se detecto fuga en baño X, se reemplazó empaque"
            )

            if st.button("Guardar anotaciones"):
                guardar_anotaciones_si_hay_cambios(
                    ot_sel,
                    anotacion_actual
                )
                st.success("Anotaciones guardadas correctamente")
                st.rerun()

            # ----------------
            # EVIDENCIA FINAL
            # ----------------
            if evidencia_fin and isinstance(evidencia_fin, str) and evidencia_fin.startswith("http"):
                try:
                    st.image(
                        evidencia_fin,
                        caption="Foto final actual",
                        width=200
                    )
                except Exception:
                    st.warning(
                        "La evidencia final esta corrupta o es invalida")
                    evidencia_fin = None

                if evidencia_fin and st.button("Reemplazar foto final"):
                    guardar_anotaciones_si_hay_cambios(
                        ot_sel,
                        anotacion_actual
                    )

                    supabase.table("preventivos").update({
                        "evidencia_fin_url": None
                    }).eq("numero_ot", ot_sel).execute()

                    st.session_state[key_anot] = str(
                        st.session_state.get(key_anot, ""))
                    st.success("Ahora sube la evidencia final")
                    st.rerun()
            else:
                st.warning("Sin evidencia final valida")

            foto_fin = st.file_uploader(
                "Sube evidencia de fin de tarea",
                type=["jpg", "jpeg", "png"],
                key=f"fin{ot_sel}"
            )

            # --------------------
            # CIERRE DE EVIDENCIAS
            # --------------------

            if st.button("Finalizar tarea"):
                st.session_state.confirmar_cierre_ot = ot_sel
                st.rerun()

            if st.session_state.confirmar_cierre_ot == ot_sel:
                st.warning(
                    f"Estás a punto de cerrar el preventivo:\n\n"
                    f"**{fila_ot.iloc[0]['descripcion']}**\n\n"
                    f"¿Estás seguro?"
                )

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Sí, finalizar"):
                        guardar_anotaciones_si_hay_cambios(
                            ot_sel,
                            anotacion_actual
                        )

                        evidencia_inicio_actual = supabase.table("preventivos") \
                            .select("evidencia_inicio_url,evidencia_fin_url") \
                            .eq("numero_ot", ot_sel) \
                            .execute().data[0]

                        if not evidencia_inicio_actual["evidencia_inicio_url"]:
                            st.error("Debes contar con foto inicial")
                            st.stop()

                        url_fin = evidencia_inicio_actual["evidencia_fin_url"]

                        if foto_fin:
                            nombre_fin = f"FIN_{ot_sel}_{uuid.uuid4().hex}.jpg"

                            supabase.storage.from_("evidencias").upload(
                                nombre_fin,
                                foto_fin.getvalue()
                            )

                            url_fin = supabase.storage.from_(
                                "evidencias"
                            ).get_public_url(nombre_fin)

                        if not url_fin:
                            st.error("Debes subir evidencia final")
                            st.stop()

                        supabase.table("preventivos").update({
                            "estatus": "REALIZADO",
                            "fecha_cierre": datetime.now(timezone.utc).isoformat(),
                            "evidencia_fin_url": url_fin,
                            "anotaciones": anotaciones
                        }).eq("numero_ot", ot_sel).execute()

                        st.session_state.pop(f"anotaciones_{ot_sel}", None)
                        st.session_state.confirmar_cierre_ot = None
                        st.success("OT Cerrada ✅")
                        st.rerun()

                with col2:
                    if st.button("Regresar"):
                        st.session_state.confirmar_cierre_ot = None
                        st.rerun()

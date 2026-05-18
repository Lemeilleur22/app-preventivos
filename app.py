import streamlit as st
import pandas as pd
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime, timezone
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
        supabase.auth.sign_out()
        st.session_state.clear()
        st.session_state.pantalla = "landing"
        st.rerun()

if modo != "Admin":
    tecnico_sel = st.session_state.tecnico

if modo == "Admin":

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📩 Carga a sistema",
        "👷‍♂️ Vista técnico",
        "📸 Evidencias",
        "📑 Job Plans",
        "Tecnicos"
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

            datos_carga = []

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

            for _, row in df.iterrows():

                location = str(row["location"]).upper()
                descripcion = str(row["description"]).upper()

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

                if "CBA" in descripcion and "IFSI" not in location:
                    datos_carga.append({
                        "numero_ot": row["wonum"],
                        "descripcion": row["description"],
                        "jpnum": str(row["jpnum"]).strip() if pd.notna(row.get("jpnum")) else None,
                        "estatus": "PENDIENTE",
                        "tecnico_id": tecnico_cba["id"],
                        "sede": sede
                    })
                    continue

                # ---------------
                # SCI
                # ---------------
                if "IFSI" in location:
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
                    continue
                else:
                    continue

                if not candidatos:
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
                    "estatus": "PENDIENTE",
                    "tecnico_id": tecnico_asignado["id"],
                    "sede": sede
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
                    st.success(f"{len(nuevos)} preventivos cargados")
                else:
                    st.info("No habia OTs nuevas")

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
                    if evidencia_inicio and str(evidencia_inicio).startswith("http"):
                        st.image(
                            evidencia_inicio,
                            caption="Antes de iniciar",
                            use_container_width=True
                        )
                    else:
                        st.info("Sin evidencia inicial")

                with col_ev2:
                    if evidencia_fin and str(evidencia_fin).startswith("https"):
                        st.image(
                            evidencia_fin,
                            caption="Despues de finalizar",
                            use_container_width=True
                        )
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

        else:  # Mostrar todas
            st.dataframe(
                df_ev[[
                    "numero_ot",
                    "descripcion",
                    "estatus",
                    "fecha_inicio",
                    "fecha_cierre"
                ]],
                use_container_width=True
            )

        # SOLO OTs cerradas
            df_cerradas = df_ev[df_ev["estatus"] == "REALIZADO"]

            if df_cerradas.empty:
                st.info("No hay OTs cerradas con evidencia")

            else:
                ot_ev = st.selectbox(
                    "Selecciona OT para ver evidencia",
                    df_cerradas["numero_ot"]
                )

                fila = df_cerradas[df_cerradas["numero_ot"] == ot_ev]

                evidencia_inicio = fila.iloc[0].get("evidencia_inicio_url")
                evidencia_fin = fila.iloc[0].get("evidencia_fin_url")
                anotaciones = fila.iloc[0].get("anotaciones")

                if st.button("Ver evidencia"):
                    col1, col2 = st.columns(2)

                    with col1:
                        if evidencia_inicio and str(evidencia_inicio).startswith("http"):
                            st.image(
                                evidencia_inicio,
                                caption="Antes de iniciar",
                                use_container_width=True
                            )

                    with col2:
                        if evidencia_fin and str(evidencia_fin).startswith("http"):
                            st.image(
                                evidencia_fin,
                                caption="Despues de finalizar la tarea",
                                use_container_width=True
                            )

                    if anotaciones:
                        st.text_area(
                            "Anotaciones del técnico",
                            value=anotaciones,
                            height=150,
                            disabled=True
                        )

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

# --------------------
# PUBLICO GENERAL
# --------------------
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
            use_container_width=True
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

            if evidencia_inicio:
                st.image(
                    evidencia_inicio,
                    caption="Foto inicial",
                    width=300
                )

            anotacion_actual = fila_ot.iloc[0].get("anotaciones")

            anotaciones = st.text_area(
                "Anotaciones de la actividad",
                value=anotacion_actual if anotacion_actual else "",
                height=150,
                placeholder="Ejemplo: Se detecto fuga en baño X, se reemplazó empaque"
            )
            if st.button("Guardar anotaciones"):
                supabase.table("preventivos").update({
                    "anotaciones": anotaciones
                }).eq("numero_ot", ot_sel).execute()

                st.success("Anotaciones guardadas correctamente")
                st.rerun()

            foto_fin = st.file_uploader(
                "Sube una foto de fin de tarea",
                type=["jpg", "jpeg", "png"],
                key=f"fin{ot_sel}"
            )

            if st.button("Finalizar tarea"):

                if not foto_fin:
                    st.error("Debes subir una foto de termino de tu actividad.")
                else:
                    nombre_fin = f"FIN_{ot_sel}_{uuid.uuid4().hex}.jpg"

                    supabase.storage.from_("evidencias").upload(
                        nombre_fin,
                        foto_fin.getvalue()
                    )

                    url_fin = supabase.storage.from_(
                        "evidencias"
                    ).get_public_url(nombre_fin)

                    supabase.table("preventivos").update({
                        "estatus": "REALIZADO",
                        "fecha_cierre": datetime.now(timezone.utc).isoformat(),
                        "evidencia_fin_url": url_fin,
                        "anotaciones": anotaciones
                    }).eq("numero_ot", ot_sel).execute()

                    st.success("OT Cerrada ✅")
                    st.rerun()

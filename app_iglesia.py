import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Configuración de la página
st.set_page_config(page_title="Registro IASD Turno II", layout="wide")

def conectar_db():
    conn = sqlite3.connect("evangelismo_web.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT, telefono TEXT, direccion TEXT, 
            curso TEXT, estado TEXT, fecha TEXT
        )
    ''')
    conn.commit()
    return conn

conn = conectar_db()

st.title("⛪ Control de Visitas - Alajuela Central")
st.subheader("Campañas Evangelísticas - Turno II")

# --- BARRA LATERAL (MENÚ) ---
menu = ["Registrar Visita", "Ver Base de Datos", "Buscar y Editar", "Reportes"]
choice = st.sidebar.selectbox("Menú de Navegación", menu)

if choice == "Registrar Visita":
    st.header("📝 Nueva Inscripción")
    with st.form("form_registro", clear_on_submit=True):
        nombre = st.text_input("Nombre Completo")
        col1, col2 = st.columns(2)
        with col1:
            tel = st.text_input("Teléfono")
        with col2:
            curso = st.selectbox("¿Desea Curso Bíblico?", ["No", "Sí"])
        
        dir = st.text_area("Dirección de Residencia")
        
        enviar = st.form_submit_button("Guardar Registro")
        
        if enviar:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO visitas (nombre, telefono, direccion, curso, estado, fecha) VALUES (?,?,?,?,?,?)",
                           (nombre, tel, dir, curso, "Pendiente", fecha))
            conn.commit()
            st.success(f"¡{nombre} ha sido registrado(a) exitosamente!")

elif choice == "Ver Base de Datos":
    st.header("📋 Listado General de Visitas")
    df = pd.read_sql_query("SELECT * FROM visitas", conn)
    st.dataframe(df, use_container_width=True)

elif choice == "Buscar y Editar":
    st.header("🔍 Seguimiento de Personas")
    nombre_buscar = st.text_input("Buscar por nombre:")
    if nombre_buscar:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM visitas WHERE nombre LIKE ?", (f'%{nombre_buscar}%',))
        datos = cursor.fetchall()
        
        if datos:
            for d in datos:
                with st.expander(f"👤 {d[1]} (ID: {d[0]})"):
                    nuevo_estado = st.selectbox("Cambiar Estado", ["Pendiente", "Visitado", "En Curso", "Bautizado"], key=f"sel{d[0]}")
                    if st.button("Actualizar", key=f"btn{d[0]}"):
                        cursor.execute("UPDATE visitas SET estado = ? WHERE id = ?", (nuevo_estado, d[0]))
                        conn.commit()
                        st.rerun()
        else:
            st.warning("No se encontraron coincidencias.")

elif choice == "Reportes":
    st.header("📊 Exportar Información")
    df = pd.read_sql_query("SELECT * FROM visitas", conn)
    
    # Botón para descargar en Excel (CSV)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Descargar Lista para Excel",
        data=csv,
        file_name='visitas_iglesia.csv',
        mime='text/csv',
    )
    st.info("Este archivo puedes abrirlo en Excel para imprimirlo fácilmente.")

import streamlit as st
import os
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="Peru Delivery - Sistema de Facturación",
    page_icon="🚚",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Crear directorio cache si no existe
if not os.path.exists("cache"):
    os.makedirs("cache")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 10px;
        color: white;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.75rem;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1>🚚 PERU DELIVERY</h1>
    <p>Sistema de Facturación Electrónica</p>
</div>
""", unsafe_allow_html=True)

# Sidebar para navegación
st.sidebar.title("📋 Menú Principal")
st.sidebar.markdown("---")

# Opciones del menú
opcion = st.sidebar.selectbox(
    "Selecciona una opción:",
    ["🏠 Inicio", "📝 Generar Factura", "🖊️ Editar Factura", "📋 Listar Facturas", "🗑️ Eliminar Factura"]
)


# Función para contar facturas
def contar_facturas():
    try:
        if not os.path.exists("cache"):
            return 0
        archivos = [f for f in os.listdir("cache") if f.startswith("factura_") and f.endswith(".txt")]
        return len(archivos)
    except:
        return 0


# Función para obtener total de facturas (suma de montos)
def obtener_total_general():
    try:
        total = 0.0
        if not os.path.exists("cache"):
            return total

        archivos = [f for f in os.listdir("cache") if f.startswith("factura_") and f.endswith(".txt")]
        for archivo in archivos:
            try:
                with open(os.path.join("cache", archivo), "r", encoding="utf-8") as f:
                    contenido = f.read()
                    # Buscar línea con TOTAL
                    for linea in contenido.split('\n'):
                        if 'TOTAL' in linea and 'S/.' in linea:
                            # Extraer el monto
                            monto_str = linea.split('S/.')[1].strip()
                            total += float(monto_str)
                            break
            except:
                continue
        return total
    except:
        return 0.0


# PÁGINA PRINCIPAL
if opcion == "🏠 Inicio":
    st.header("Dashboard del Sistema")

    # Métricas del sistema
    col1, col2, col3 = st.columns(3)

    num_facturas = contar_facturas()
    total_general = obtener_total_general()

    with col1:
        st.metric("📄 Total Facturas", num_facturas)

    with col2:
        st.metric("💰 Monto Total", f"S/. {total_general:.2f}")

    with col3:
        promedio = total_general / num_facturas if num_facturas > 0 else 0
        st.metric("📊 Promedio", f"S/. {promedio:.2f}")

    st.markdown("---")
    st.subheader("🚀 Accesos Rápidos")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📝 Nueva Factura", type="primary", use_container_width=True):
            st.switch_page("pages/generar_factura.py")

        if st.button("📋 Ver Facturas", use_container_width=True):
            st.switch_page("pages/listar_facturas.py")

    with col2:
        if st.button("🖊️ Editar Factura", use_container_width=True):
            st.switch_page("pages/editar_factura.py")

        if st.button("🗑️ Eliminar Factura", use_container_width=True):
            st.switch_page("pages/eliminar_factura.py")

    st.markdown("---")
    st.info("💡 **Tip:** Usa el menú lateral para navegar entre las diferentes funciones del sistema.")

    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: #666; padding: 2rem;'>
            <p>© 2025 Peru Delivery | Sistema de Facturación v2.0</p>
            <p>Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Redirigir a páginas según selección
elif opcion == "📝 Generar Factura":
    st.switch_page("pages/generar_factura.py")
elif opcion == "🖊️ Editar Factura":
    st.switch_page("pages/editar_factura.py")
elif opcion == "📋 Listar Facturas":
    st.switch_page("pages/listar_facturas.py")
elif opcion == "🗑️ Eliminar Factura":
    st.switch_page("pages/eliminar_factura.py")
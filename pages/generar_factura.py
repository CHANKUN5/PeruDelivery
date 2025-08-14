import streamlit as st
import sys
import os

# Añadir el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.archivo import guardar_factura
from utils.validaciones import dato_valido

IGV = 0.18

st.set_page_config(page_title="Generar Factura", page_icon="📝")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .totales-container {
        background: linear-gradient(135deg, #6b46c1 0%, #8b5cf6 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        text-align: center;
    }
    .producto-row {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #27ae60;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📝 GENERAR FACTURA</h1>
    <p>Ingrese hasta 10 productos con sus precios y cantidades</p>
</div>
""", unsafe_allow_html=True)

# Botón de regreso
if st.button("🏠 Volver al inicio", type="secondary"):
    st.switch_page("app.py")

st.markdown("---")

# Inicializar estado si no existe
if 'productos' not in st.session_state:
    st.session_state.productos = []
    for i in range(10):
        st.session_state.productos.append({
            'nombre': '',
            'precio': 0.0,
            'cantidad': 0
        })


# Función para calcular totales
def calcular_totales():
    subtotal = 0.0
    for producto in st.session_state.productos:
        if producto['nombre'].strip() and producto['precio'] > 0 and producto['cantidad'] > 0:
            subtotal += producto['precio'] * producto['cantidad']

    igv = subtotal * IGV
    total = subtotal + igv
    return subtotal, igv, total


# Formulario de productos
st.subheader("🛍️ Productos de la Factura")

# Crear formulario dinámico
with st.form("formulario_factura", clear_on_submit=False):
    productos_validos = []

    for i in range(10):
        st.markdown(f"**Producto {i + 1}:**")

        col1, col2, col3 = st.columns([3, 2, 1])

        with col1:
            nombre = st.text_input(
                f"Nombre del producto {i + 1}",
                key=f"nombre_{i}",
                placeholder="Ej: Pizza Margarita",
                label_visibility="collapsed"
            )

        with col2:
            precio = st.number_input(
                f"Precio S/. {i + 1}",
                min_value=0.0,
                step=0.01,
                key=f"precio_{i}",
                format="%.2f",
                label_visibility="collapsed"
            )

        with col3:
            cantidad = st.number_input(
                f"Cantidad {i + 1}",
                min_value=0,
                step=1,
                key=f"cantidad_{i}",
                label_visibility="collapsed"
            )

        # Actualizar estado
        st.session_state.productos[i] = {
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad
        }

        # Validar y añadir a productos válidos
        if nombre.strip() and precio > 0 and cantidad > 0:
            if dato_valido(precio, cantidad):
                total_item = precio * cantidad
                productos_validos.append((nombre.strip(), precio, cantidad, total_item))

    st.markdown("---")

    # Mostrar totales en tiempo real
    subtotal, igv, total = calcular_totales()

    st.markdown(f"""
    <div class="totales-container">
        <h3>💰 Resumen de la Factura</h3>
        <div style="display: flex; justify-content: space-around; margin: 1rem 0;">
            <div>
                <h4>Subtotal</h4>
                <p style="font-size: 1.2em;">S/. {subtotal:.2f}</p>
            </div>
            <div>
                <h4>IGV (18%)</h4>
                <p style="font-size: 1.2em;">S/. {igv:.2f}</p>
            </div>
            <div>
                <h4>TOTAL</h4>
                <p style="font-size: 1.5em; font-weight: bold; color: #ffe680;">S/. {total:.2f}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botones de acción
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        limpiar = st.form_submit_button("🧹 Limpiar", use_container_width=True)

    with col2:
        guardar = st.form_submit_button("💾 Guardar Factura", type="primary", use_container_width=True)

    with col3:
        cancelar = st.form_submit_button("❌ Cancelar", use_container_width=True)

# Procesar acciones
if limpiar:
    # Limpiar todos los campos
    for key in st.session_state.keys():
        if key.startswith('nombre_') or key.startswith('precio_') or key.startswith('cantidad_'):
            st.session_state[key] = 0.0 if 'precio' in key else (0 if 'cantidad' in key else '')
    st.success("🧹 Campos limpiados correctamente")
    st.rerun()

if cancelar:
    st.switch_page("app.py")

if guardar:
    if not productos_validos:
        st.error("❌ **Error:** Debes ingresar al menos un producto con precio y cantidad válidos.")
    else:
        try:
            # Validar todos los productos
            for nombre, precio, cantidad, total_item in productos_validos:
                if not dato_valido(precio, cantidad):
                    st.error(f"❌ **Error:** El producto '{nombre}' tiene valores inválidos.")
                    break
            else:
                # Guardar la factura
                guardar_factura(productos_validos, subtotal, igv, total)

                # Mostrar resumen de éxito
                st.success("✅ **¡Factura generada exitosamente!**")

                st.balloons()

                # Mostrar resumen
                with st.expander("📋 Ver resumen de la factura", expanded=True):
                    st.markdown("**Productos incluidos:**")
                    for nombre, precio, cantidad, total_item in productos_validos:
                        st.markdown(f"- **{nombre}**: {cantidad} x S/. {precio:.2f} = S/. {total_item:.2f}")

                    st.markdown("---")
                    st.markdown(f"**💰 Total final: S/. {total:.2f}**")

                # Opciones después del guardado
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📝 Generar otra factura", use_container_width=True):
                        # Limpiar campos y recargar
                        for key in st.session_state.keys():
                            if key.startswith('nombre_') or key.startswith('precio_') or key.startswith('cantidad_'):
                                st.session_state[key] = 0.0 if 'precio' in key else (0 if 'cantidad' in key else '')
                        st.rerun()

                with col2:
                    if st.button("📋 Ver todas las facturas", use_container_width=True):
                        st.switch_page("pages/listar_facturas.py")

        except Exception as e:
            st.error(f"❌ **Error al guardar la factura:** {str(e)}")

# Vista previa de productos ingresados
if productos_validos:
    st.markdown("---")
    st.subheader("👀 Vista previa de productos")

    for i, (nombre, precio, cantidad, total_item) in enumerate(productos_validos, 1):
        st.markdown(f"""
        <div class="producto-row">
            <strong>{i}. {nombre}</strong><br>
            <small>Precio: S/. {precio:.2f} | Cantidad: {cantidad} | Total: S/. {total_item:.2f}</small>
        </div>
        """, unsafe_allow_html=True)

# Información adicional
st.markdown("---")
st.info("""
💡 **Tips para generar facturas:**
- Asegúrate de ingresar precios mayores a 0
- Las cantidades deben ser números enteros positivos
- Los nombres de productos no pueden estar vacíos
- El IGV se calcula automáticamente (18%)
""")
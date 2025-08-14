import streamlit as st
import os

st.set_page_config(page_title="Eliminar Factura", page_icon="🗑️")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .warning-container {
        background-color: #fff3cd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        text-align: center;
    }
    .danger-container {
        background-color: #f8d7da;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    .factura-info {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
    }
    .success-container {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🗑️ ELIMINAR FACTURA</h1>
    <p>⚠️ Esta acción no se puede deshacer</p>
</div>
""", unsafe_allow_html=True)

# Botón de regreso
if st.button("🏠 Volver al inicio", type="secondary"):
    st.switch_page("app.py")

st.markdown("---")

# Advertencia principal
st.markdown("""
<div class="warning-container">
    <h3>⚠️ ADVERTENCIA IMPORTANTE</h3>
    <p>La eliminación de una factura es <strong>permanente e irreversible</strong>.</p>
    <p>Asegúrate de seleccionar la factura correcta antes de proceder.</p>
</div>
""", unsafe_allow_html=True)


# Función para obtener facturas disponibles
@st.cache_data
def obtener_facturas_disponibles():
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
            return []

        archivos = sorted(
            [f for f in os.listdir("cache") if f.startswith("factura_") and f.endswith(".txt")]
        )

        facturas = []
        for archivo in archivos:
            try:
                numero = int(archivo.split("_")[1].split(".")[0])
                ruta = os.path.join("cache", archivo)
                tamaño_kb = os.path.getsize(ruta) / 1024

                # Leer total y fecha de la factura
                total = "0.00"
                fecha_mod = os.path.getmtime(ruta)

                try:
                    with open(ruta, "r", encoding="utf-8") as f:
                        contenido = f.read()
                        for linea in contenido.split('\n'):
                            if 'TOTAL' in linea and 'S/.' in linea:
                                total = linea.split('S/.')[1].strip()
                                break
                except:
                    pass

                facturas.append({
                    'numero': numero,
                    'archivo': archivo,
                    'ruta': ruta,
                    'tamaño_kb': tamaño_kb,
                    'total': total,
                    'fecha_mod': fecha_mod
                })
            except:
                continue

        return sorted(facturas, key=lambda x: x['numero'])

    except Exception as e:
        st.error(f"Error al obtener las facturas: {e}")
        return []


# Obtener facturas
facturas_disponibles = obtener_facturas_disponibles()

if not facturas_disponibles:
    st.markdown("""
    <div class="factura-info">
        <h3>📭 No hay facturas para eliminar</h3>
        <p>No existen facturas registradas en el sistema.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📝 Generar primera factura", type="primary", use_container_width=True):
        st.switch_page("pages/generar_factura.py")

else:
    # MÉTODO 1: Selección por lista
    st.subheader("📋 Método 1: Seleccionar de la lista")

    # Verificar si viene de otra página con número específico
    numero_preseleccionado = st.session_state.get('numero_a_eliminar', None)

    opciones = ["Selecciona una factura..."]
    indice_preseleccionado = 0

    for i, factura in enumerate(facturas_disponibles):
        opcion = f"Factura N° {factura['numero']:03d} - S/. {factura['total']} ({factura['tamaño_kb']:.1f} KB)"
        opciones.append(opcion)
        if numero_preseleccionado and factura['numero'] == numero_preseleccionado:
            indice_preseleccionado = i + 1

    seleccion_lista = st.selectbox(
        "Selecciona la factura a eliminar:",
        opciones,
        index=indice_preseleccionado,
        key="selector_eliminar"
    )

    factura_seleccionada = None

    if seleccion_lista != "Selecciona una factura...":
        numero_seleccionado = int(seleccion_lista.split("N° ")[1].split(" ")[0])
        factura_seleccionada = next(f for f in facturas_disponibles if f['numero'] == numero_seleccionado)

    st.markdown("**- O -**")

    # MÉTODO 2: Ingreso directo de número
    st.subheader("🔢 Método 2: Ingresar número directamente")

    numero_directo = st.number_input(
        "Número de factura a eliminar:",
        min_value=1,
        max_value=999,
        step=1,
        value=numero_preseleccionado if numero_preseleccionado else 1,
        key="numero_directo"
    )

    if st.button("🔍 Buscar factura", use_container_width=True):
        factura_encontrada = next((f for f in facturas_disponibles if f['numero'] == numero_directo), None)
        if factura_encontrada:
            factura_seleccionada = factura_encontrada
            st.success(f"✅ Factura N° {numero_directo:03d} encontrada")
        else:
            st.error(f"❌ No existe la factura N° {numero_directo:03d}")
            factura_seleccionada = None

    # Si hay una factura seleccionada, mostrar información y opción de eliminar
    if factura_seleccionada:
        st.markdown("---")

        # Mostrar información de la factura
        import datetime

        fecha_modificacion = datetime.datetime.fromtimestamp(factura_seleccionada['fecha_mod'])

        st.markdown(f"""
        <div class="factura-info">
            <h3>📄 Información de la Factura</h3>
            <p><strong>Número:</strong> {factura_seleccionada['numero']:03d}</p>
            <p><strong>Total:</strong> S/. {factura_seleccionada['total']}</p>
            <p><strong>Tamaño:</strong> {factura_seleccionada['tamaño_kb']:.2f} KB</p>
            <p><strong>Última modificación:</strong> {fecha_modificacion.strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>Archivo:</strong> {factura_seleccionada['archivo']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Mostrar contenido de la factura
        with st.expander("👁️ Ver contenido de la factura", expanded=False):
            try:
                with open(factura_seleccionada['ruta'], "r", encoding="utf-8") as f:
                    contenido = f.read()
                st.code(contenido, language="text")
            except Exception as e:
                st.error(f"Error al leer el contenido: {e}")

        # Zona de peligro
        st.markdown(f"""
        <div class="danger-container">
            <h3>⚠️ ZONA DE PELIGRO</h3>
            <p><strong>¿Estás completamente seguro de eliminar la Factura N° {factura_seleccionada['numero']:03d}?</strong></p>
            <p>Esta acción:</p>
            <ul>
                <li>Eliminará <strong>permanentemente</strong> el archivo de factura</li>
                <li><strong>No se puede deshacer</strong></li>
                <li>Perderás todos los datos de esta factura</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        # Confirmación con checkbox
        confirmar_eliminacion = st.checkbox(
            f"✅ Sí, estoy seguro de eliminar la Factura N° {factura_seleccionada['numero']:03d}",
            key="confirmar_checkbox"
        )

        if confirmar_eliminacion:
            st.markdown("### 🔐 Confirmación Final")

            # Input de confirmación
            confirmacion_texto = st.text_input(
                f"Escribe exactamente 'ELIMINAR {factura_seleccionada['numero']:03d}' para confirmar:",
                key="confirmacion_texto"
            )

            texto_esperado = f"ELIMINAR {factura_seleccionada['numero']:03d}"

            if confirmacion_texto == texto_esperado:
                # Botón final de eliminación
                col1, col2, col3 = st.columns([1, 2, 1])

                with col2:
                    if st.button(
                            f"🗑️ ELIMINAR FACTURA {factura_seleccionada['numero']:03d}",
                            type="primary",
                            use_container_width=True,
                            key="boton_eliminar_final"
                    ):
                        try:
                            # Realizar la eliminación
                            os.remove(factura_seleccionada['ruta'])

                            # Mensaje de éxito
                            st.markdown(f"""
                            <div class="success-container">
                                <h3>✅ FACTURA ELIMINADA EXITOSAMENTE</h3>
                                <p><strong>Factura N° {factura_seleccionada['numero']:03d}</strong> ha sido eliminada permanentemente.</p>
                                <p>El archivo <code>{factura_seleccionada['archivo']}</code> ya no existe.</p>
                            </div>
                            """, unsafe_allow_html=True)

                            st.balloons()

                            # Limpiar cache
                            st.cache_data.clear()

                            # Limpiar session state
                            if 'numero_a_eliminar' in st.session_state:
                                del st.session_state.numero_a_eliminar

                            # Opciones post-eliminación
                            st.markdown("---")
                            st.subheader("📋 ¿Qué hacer ahora?")

                            col1, col2, col3 = st.columns(3)

                            with col1:
                                if st.button("🗑️ Eliminar otra factura", use_container_width=True):
                                    st.rerun()

                            with col2:
                                if st.button("📋 Ver facturas restantes", use_container_width=True):
                                    st.switch_page("pages/listar_facturas.py")

                            with col3:
                                if st.button("🏠 Ir al inicio", use_container_width=True):
                                    st.switch_page("app.py")

                        except Exception as e:
                            st.error(f"❌ **Error al eliminar la factura:** {str(e)}")

            elif confirmacion_texto and confirmacion_texto != texto_esperado:
                st.error(f"❌ El texto no coincide. Debe escribir exactamente: **{texto_esperado}**")

        # Botones de cancelar/salir
        st.markdown("---")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("❌ Cancelar operación", use_container_width=True):
                # Limpiar session state
                if 'numero_a_eliminar' in st.session_state:
                    del st.session_state.numero_a_eliminar
                st.switch_page("app.py")

        with col2:
            if st.button("📋 Ver todas las facturas", use_container_width=True):
                st.switch_page("pages/listar_facturas.py")

# Información de ayuda
st.markdown("---")
st.info("""
💡 **Información importante:**
- Solo se pueden eliminar facturas que existan en el sistema
- La eliminación es irreversible - no hay papelera de reciclaje
- Se recomienda hacer una copia de respaldo antes de eliminar facturas importantes
- Puedes ver el contenido de la factura antes de eliminarla para confirmar
""")

# Estadísticas del sistema
if facturas_disponibles:
    st.markdown("---")
    st.subheader("📊 Estadísticas del Sistema")

    total_facturas = len(facturas_disponibles)
    total_monto = sum(float(f['total']) for f in facturas_disponibles)
    tamaño_total = sum(f['tamaño_kb'] for f in facturas_disponibles)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Facturas totales", total_facturas)

    with col2:
        st.metric("💰 Monto total", f"S/. {total_monto:.2f}")

    with col3:
        st.metric("💾 Espacio usado", f"{tamaño_total:.2f} KB")
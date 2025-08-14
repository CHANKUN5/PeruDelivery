import streamlit as st
import sys
import os

# Añadir el directorio raíz al path para importar utils
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utils.validaciones import dato_valido

IGV = 0.18

st.set_page_config(page_title="Editar Factura", page_icon="🖊️")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
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
    .factura-info {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #27ae60;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🖊️ EDITAR FACTURA</h1>
    <p>Selecciona una factura de la lista para modificar sus datos</p>
</div>
""", unsafe_allow_html=True)

# Botón de regreso
if st.button("🏠 Volver al inicio", type="secondary"):
    st.switch_page("app.py")

st.markdown("---")


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

                # Leer total de la factura
                total = "0.00"
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
                    'total': total
                })
            except:
                continue

        return sorted(facturas, key=lambda x: x['numero'])

    except Exception as e:
        st.error(f"Error al obtener las facturas: {e}")
        return []


# Función para parsear factura
def parsear_factura(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            lineas = [l.rstrip("\n") for l in f.readlines()]

        # Buscar sección de items entre las líneas de guiones
        idx_inicio = None
        idx_fin = None

        for i, linea in enumerate(lineas):
            if i > 0 and set(linea) == {"-"}:
                idx_inicio = i + 1
                break

        if idx_inicio is not None:
            for j in range(idx_inicio, len(lineas)):
                if set(lineas[j]) == {"-"}:
                    idx_fin = j
                    break

        items = []
        if idx_inicio is None or idx_fin is None:
            return items

        for linea in lineas[idx_inicio:idx_fin]:
            if not linea.strip():
                continue

            nombre = linea[:20].strip()
            resto = linea[20:].strip().split()

            if len(resto) >= 3:
                try:
                    precio = float(resto[0])
                    cantidad = int(resto[1])
                    if nombre:
                        items.append((nombre, precio, cantidad))
                except:
                    continue
        return items
    except Exception as e:
        st.error(f"Error al parsear la factura: {e}")
        return []


# Función para escribir factura
def escribir_factura(ruta, productos, subtotal, igv, total):
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("🧾 FACTURA ELECTRÓNICA - PERU DELIVERY\n")
            f.write("=" * 50 + "\n")
            f.write(f"{'Producto':<20}{'Precio':>10}{'Cant.':>8}{'Total':>10}\n")
            f.write("-" * 50 + "\n")
            for nombre, precio, cantidad, total_item in productos:
                f.write(f"{nombre:<20}{precio:>10.2f}{cantidad:>8}{total_item:>10.2f}\n")
            f.write("-" * 50 + "\n")
            f.write(f"{'Subtotal':<30} S/. {subtotal:.2f}\n")
            f.write(f"{'IGV (18%)':<30} S/. {igv:.2f}\n")
            f.write(f"{'TOTAL':<30} S/. {total:.2f}\n")
            f.write("=" * 50 + "\n")
        return True
    except Exception as e:
        st.error(f"Error al escribir la factura: {e}")
        return False


# Obtener facturas
facturas_disponibles = obtener_facturas_disponibles()

if not facturas_disponibles:
    st.warning("📭 No hay facturas disponibles para editar")
    if st.button("📝 Generar primera factura", type="primary", use_container_width=True):
        st.switch_page("pages/generar_factura.py")
else:
    # PASO 1: Seleccionar factura
    st.subheader("📂 Paso 1: Seleccionar Factura")

    # Verificar si viene de otra página con número específico
    numero_preseleccionado = st.session_state.get('numero_a_editar', None)

    opciones = []
    indice_preseleccionado = 0

    for i, factura in enumerate(facturas_disponibles):
        opcion = f"Factura N° {factura['numero']:03d} - S/. {factura['total']} ({factura['tamaño_kb']:.1f} KB)"
        opciones.append(opcion)
        if numero_preseleccionado and factura['numero'] == numero_preseleccionado:
            indice_preseleccionado = i

    seleccion = st.selectbox(
        "Selecciona la factura a editar:",
        opciones,
        index=indice_preseleccionado,
        key="selector_factura"
    )

    if seleccion:
        # Obtener datos de la factura seleccionada
        numero_seleccionado = int(seleccion.split("N° ")[1].split(" ")[0])
        factura_actual = next(f for f in facturas_disponibles if f['numero'] == numero_seleccionado)

        # Mostrar información de la factura
        st.markdown(f"""
        <div class="factura-info">
            <h4>📄 Factura seleccionada: N° {factura_actual['numero']:03d}</h4>
            <p><strong>Total actual:</strong> S/. {factura_actual['total']}</p>
            <p><strong>Archivo:</strong> {factura_actual['archivo']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Botón para cargar
        if st.button("📂 Cargar datos de la factura", type="primary", use_container_width=True):
            # Parsear y cargar datos en session_state
            productos_parseados = parsear_factura(factura_actual['ruta'])

            # Inicializar productos en session_state
            st.session_state.productos_editando = []
            for i in range(10):
                if i < len(productos_parseados):
                    nombre, precio, cantidad = productos_parseados[i]
                    st.session_state.productos_editando.append({
                        'nombre': nombre,
                        'precio': precio,
                        'cantidad': cantidad
                    })
                else:
                    st.session_state.productos_editando.append({
                        'nombre': '',
                        'precio': 0.0,
                        'cantidad': 0
                    })

            st.session_state.factura_cargada = factura_actual
            st.success(f"✅ Datos cargados de la Factura N° {factura_actual['numero']:03d}")
            st.rerun()

    # PASO 2: Editar productos (solo si hay factura cargada)
    if 'factura_cargada' in st.session_state and 'productos_editando' in st.session_state:
        st.markdown("---")
        st.subheader("🖊️ Paso 2: Editar Productos")

        factura_cargada = st.session_state.factura_cargada

        st.markdown(f"""
        <div class="warning-box">
            <strong>⚠️ Editando:</strong> Factura N° {factura_cargada['numero']:03d}<br>
            <small>Los cambios sobrescribirán la factura original</small>
        </div>
        """, unsafe_allow_html=True)


        # Función para calcular totales
        def calcular_totales_edicion():
            subtotal = 0.0
            for producto in st.session_state.productos_editando:
                if producto['nombre'].strip() and producto['precio'] > 0 and producto['cantidad'] > 0:
                    subtotal += producto['precio'] * producto['cantidad']

            igv = subtotal * IGV
            total = subtotal + igv
            return subtotal, igv, total


        # Formulario de edición
        with st.form("formulario_edicion", clear_on_submit=False):
            productos_validos = []

            for i in range(10):
                st.markdown(f"**Producto {i + 1}:**")

                col1, col2, col3 = st.columns([3, 2, 1])

                with col1:
                    nombre = st.text_input(
                        f"Nombre del producto {i + 1}",
                        value=st.session_state.productos_editando[i]['nombre'],
                        key=f"edit_nombre_{i}",
                        placeholder="Ej: Pizza Margarita",
                        label_visibility="collapsed"
                    )

                with col2:
                    precio = st.number_input(
                        f"Precio S/. {i + 1}",
                        value=st.session_state.productos_editando[i]['precio'],
                        min_value=0.0,
                        step=0.01,
                        key=f"edit_precio_{i}",
                        format="%.2f",
                        label_visibility="collapsed"
                    )

                with col3:
                    cantidad = st.number_input(
                        f"Cantidad {i + 1}",
                        value=st.session_state.productos_editando[i]['cantidad'],
                        min_value=0,
                        step=1,
                        key=f"edit_cantidad_{i}",
                        label_visibility="collapsed"
                    )

                # Actualizar estado
                st.session_state.productos_editando[i] = {
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

            # Mostrar totales
            subtotal, igv, total = calcular_totales_edicion()

            st.markdown(f"""
            <div class="totales-container">
                <h3>💰 Totales Actualizados</h3>
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
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                guardar = st.form_submit_button("💾 Guardar Cambios", type="primary")

            with col2:
                limpiar = st.form_submit_button("🧹 Limpiar")

            with col3:
                recargar = st.form_submit_button("🔄 Recargar Original")

            with col4:
                cancelar = st.form_submit_button("❌ Cancelar")

        # Procesar acciones
        if guardar:
            if not productos_validos:
                st.error("❌ **Error:** Debe haber al menos un producto válido.")
            else:
                try:
                    # Validar todos los productos
                    for nombre, precio, cantidad, total_item in productos_validos:
                        if not dato_valido(precio, cantidad):
                            st.error(f"❌ **Error:** El producto '{nombre}' tiene valores inválidos.")
                            break
                    else:
                        # Confirmar guardado
                        with st.container():
                            st.warning(
                                f"⚠️ ¿Confirmar guardado de cambios en la Factura N° {factura_cargada['numero']:03d}?")

                            col1, col2 = st.columns(2)

                            with col1:
                                if st.button("✅ Sí, Guardar", type="primary", use_container_width=True):
                                    if escribir_factura(factura_cargada['ruta'], productos_validos, subtotal, igv,
                                                        total):
                                        st.success(f"✅ **¡Cambios guardados exitosamente!**")
                                        st.balloons()

                                        # Limpiar session_state
                                        if 'productos_editando' in st.session_state:
                                            del st.session_state.productos_editando
                                        if 'factura_cargada' in st.session_state:
                                            del st.session_state.factura_cargada
                                        if 'numero_a_editar' in st.session_state:
                                            del st.session_state.numero_a_editar

                                        # Limpiar cache
                                        st.cache_data.clear()

                                        st.info("🔄 La página se actualizará en unos segundos...")

                                        if st.button("📋 Ver facturas actualizadas"):
                                            st.switch_page("pages/listar_facturas.py")

                            with col2:
                                if st.button("❌ Cancelar", use_container_width=True):
                                    st.info("Operación cancelada")

                except Exception as e:
                    st.error(f"❌ **Error al guardar:** {str(e)}")

        if limpiar:
            # Limpiar todos los campos
            for i in range(10):
                st.session_state.productos_editando[i] = {
                    'nombre': '',
                    'precio': 0.0,
                    'cantidad': 0
                }
            st.success("🧹 Campos limpiados")
            st.rerun()

        if recargar:
            # Recargar datos originales
            productos_parseados = parsear_factura(factura_cargada['ruta'])
            for i in range(10):
                if i < len(productos_parseados):
                    nombre, precio, cantidad = productos_parseados[i]
                    st.session_state.productos_editando[i] = {
                        'nombre': nombre,
                        'precio': precio,
                        'cantidad': cantidad
                    }
                else:
                    st.session_state.productos_editando[i] = {
                        'nombre': '',
                        'precio': 0.0,
                        'cantidad': 0
                    }
            st.success("🔄 Datos originales recargados")
            st.rerun()

        if cancelar:
            # Limpiar session_state y volver
            if 'productos_editando' in st.session_state:
                del st.session_state.productos_editando
            if 'factura_cargada' in st.session_state:
                del st.session_state.factura_cargada
            if 'numero_a_editar' in st.session_state:
                del st.session_state.numero_a_editar
            st.switch_page("app.py")

# Información adicional
st.markdown("---")
st.info("""
💡 **Tips para editar facturas:**
- Selecciona una factura de la lista y carga sus datos
- Modifica los productos según necesites
- Los cambios sobrescribirán la factura original
- Puedes limpiar campos o recargar los datos originales
""")
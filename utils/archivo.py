import os


def obtener_siguiente_numero_factura():
    """
    Obtiene el siguiente número de factura disponible.
    Busca en la carpeta cache y devuelve el número más alto + 1.
    """
    carpeta = "cache"

    # Crear carpeta si no existe
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    try:
        archivos = os.listdir(carpeta)
        numeros = []

        for archivo in archivos:
            if archivo.startswith("factura_") and archivo.endswith(".txt"):
                try:
                    # Extraer número del archivo factura_XXX.txt
                    num = int(archivo.split("_")[1].split(".")[0])
                    numeros.append(num)
                except (ValueError, IndexError):
                    # Ignorar archivos con formato incorrecto
                    continue

        if numeros:
            return max(numeros) + 1
        else:
            return 1
    except OSError:
        # Si hay error al acceder a la carpeta, empezar desde 1
        return 1


def guardar_factura(productos, subtotal, igv, total):
    """
    Guarda una factura en formato texto en la carpeta cache.

    Args:
        productos: Lista de tuplas (nombre, precio, cantidad, total_item)
        subtotal: Subtotal sin IGV
        igv: Monto del IGV
        total: Total final con IGV

    Returns:
        str: Nombre del archivo creado o None si hubo error
    """
    try:
        # Obtener número de factura
        numero = obtener_siguiente_numero_factura()
        nombre_archivo = f"cache/factura_{str(numero).zfill(3)}.txt"

        # Crear contenido de la factura
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            # Encabezado
            f.write("🧾 FACTURA ELECTRÓNICA - PERU DELIVERY\n")
            f.write("=" * 50 + "\n")

            # Cabecera de la tabla
            f.write(f"{'Producto':<20}{'Precio':>10}{'Cant.':>8}{'Total':>10}\n")
            f.write("-" * 50 + "\n")

            # Productos
            for prod, precio, cantidad, total_item in productos:
                # Truncar nombre del producto si es muy largo
                nombre_truncado = prod[:19] if len(prod) > 19 else prod
                f.write(f"{nombre_truncado:<20}{precio:>10.2f}{cantidad:>8}{total_item:>10.2f}\n")

            # Separador
            f.write("-" * 50 + "\n")

            # Totales
            f.write(f"{'Subtotal':<30} S/. {subtotal:.2f}\n")
            f.write(f"{'IGV (18%)':<30} S/. {igv:.2f}\n")
            f.write(f"{'TOTAL':<30} S/. {total:.2f}\n")
            f.write("=" * 50 + "\n")

        print(f"✅ Factura guardada como: {nombre_archivo}")
        return nombre_archivo

    except Exception as e:
        print(f"❌ Error al guardar la factura: {str(e)}")
        return None


def verificar_factura_existe(numero_factura):
    """
    Verifica si existe una factura con el número dado.

    Args:
        numero_factura: Número de la factura a verificar

    Returns:
        bool: True si existe, False si no existe
    """
    nombre_archivo = f"cache/factura_{str(numero_factura).zfill(3)}.txt"
    return os.path.exists(nombre_archivo)


def obtener_info_factura(numero_factura):
    """
    Obtiene información básica de una factura.

    Args:
        numero_factura: Número de la factura

    Returns:
        dict: Información de la factura o None si no existe
    """
    nombre_archivo = f"cache/factura_{str(numero_factura).zfill(3)}.txt"

    if not os.path.exists(nombre_archivo):
        return None

    try:
        stat = os.stat(nombre_archivo)

        # Leer total de la factura
        total = "0.00"
        try:
            with open(nombre_archivo, "r", encoding="utf-8") as f:
                contenido = f.read()
                for linea in contenido.split('\n'):
                    if 'TOTAL' in linea and 'S/.' in linea:
                        total = linea.split('S/.')[1].strip()
                        break
        except:
            pass

        return {
            'numero': numero_factura,
            'archivo': f"factura_{str(numero_factura).zfill(3)}.txt",
            'ruta': nombre_archivo,
            'tamaño_bytes': stat.st_size,
            'tamaño_kb': round(stat.st_size / 1024, 2),
            'total': total,
            'fecha_modificacion': stat.st_mtime
        }

    except Exception as e:
        print(f"Error al obtener info de factura {numero_factura}: {e}")
        return None


def listar_todas_las_facturas():
    """
    Lista todas las facturas disponibles en el sistema.

    Returns:
        list: Lista de diccionarios con información de cada factura
    """
    try:
        if not os.path.exists("cache"):
            os.makedirs("cache")
            return []

        archivos = os.listdir("cache")
        facturas = []

        for archivo in archivos:
            if archivo.startswith("factura_") and archivo.endswith(".txt"):
                try:
                    numero = int(archivo.split("_")[1].split(".")[0])
                    info = obtener_info_factura(numero)
                    if info:
                        facturas.append(info)
                except:
                    continue

        # Ordenar por número de factura
        facturas.sort(key=lambda x: x['numero'])
        return facturas

    except Exception as e:
        print(f"Error al listar facturas: {e}")
        return []


def eliminar_factura(numero_factura):
    """
    Elimina una factura del sistema.

    Args:
        numero_factura: Número de la factura a eliminar

    Returns:
        bool: True si se eliminó correctamente, False si hubo error
    """
    nombre_archivo = f"cache/factura_{str(numero_factura).zfill(3)}.txt"

    try:
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
            print(f"✅ Factura {numero_factura:03d} eliminada correctamente")
            return True
        else:
            print(f"❌ No existe la factura {numero_factura:03d}")
            return False

    except Exception as e:
        print(f"❌ Error al eliminar factura {numero_factura:03d}: {e}")
        return False


def crear_backup_factura(numero_factura, carpeta_backup="backups"):
    """
    Crea una copia de respaldo de una factura.

    Args:
        numero_factura: Número de la factura a respaldar
        carpeta_backup: Carpeta donde guardar el respaldo

    Returns:
        str: Ruta del archivo de respaldo o None si hubo error
    """
    import shutil
    from datetime import datetime

    nombre_archivo = f"cache/factura_{str(numero_factura).zfill(3)}.txt"

    if not os.path.exists(nombre_archivo):
        return None

    try:
        # Crear carpeta de respaldo si no existe
        if not os.path.exists(carpeta_backup):
            os.makedirs(carpeta_backup)

        # Nombre del archivo de respaldo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_backup = f"{carpeta_backup}/factura_{numero_factura:03d}_backup_{timestamp}.txt"

        # Copiar archivo
        shutil.copy2(nombre_archivo, nombre_backup)

        print(f"✅ Backup creado: {nombre_backup}")
        return nombre_backup

    except Exception as e:
        print(f"❌ Error al crear backup de factura {numero_factura:03d}: {e}")
        return None
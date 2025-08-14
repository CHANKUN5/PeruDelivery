def dato_valido(precio, cantidad):
    """
    Verifica si el precio y cantidad ingresados son válidos.

    Args:
        precio (float): Precio del producto
        cantidad (int): Cantidad del producto

    Returns:
        bool: True si ambos valores son válidos, False en caso contrario

    Criterios de validación:
    - El precio debe ser un número (int o float) mayor que 0
    - La cantidad debe ser un número entero positivo
    - No se permiten valores None, negativos o cero
    """
    try:
        # Verificar que el precio sea un número válido
        if not isinstance(precio, (int, float)):
            return False

        # Verificar que la cantidad sea un número entero válido
        if not isinstance(cantidad, int):
            return False

        # Verificar que el precio sea mayor que 0
        if precio <= 0:
            return False

        # Verificar que la cantidad sea mayor que 0
        if cantidad <= 0:
            return False

        # Verificar rangos razonables
        # Precio máximo: S/. 10,000 (productos muy costosos)
        if precio > 10000:
            return False

        # Cantidad máxima: 999 unidades
        if cantidad > 999:
            return False

        return True

    except (TypeError, ValueError):
        return False


def validar_nombre_producto(nombre):
    """
    Valida el nombre de un producto.

    Args:
        nombre (str): Nombre del producto

    Returns:
        bool: True si el nombre es válido, False en caso contrario
    """
    if not isinstance(nombre, str):
        return False

    # Eliminar espacios al inicio y final
    nombre = nombre.strip()

    # Verificar que no esté vacío
    if not nombre:
        return False

    # Verificar longitud mínima y máxima
    if len(nombre) < 2:
        return False

    if len(nombre) > 50:
        return False

    # Verificar que contenga al menos una letra
    if not any(c.isalpha() for c in nombre):
        return False

    return True


def validar_numero_factura(numero):
    """
    Valida un número de factura.

    Args:
        numero: Número de factura a validar

    Returns:
        bool: True si el número es válido, False en caso contrario
    """
    try:
        # Convertir a entero si es string
        if isinstance(numero, str):
            numero = int(numero)

        # Verificar que sea un entero
        if not isinstance(numero, int):
            return False

        # Verificar rango (1 a 999)
        if numero < 1 or numero > 999:
            return False

        return True

    except (TypeError, ValueError):
        return False


def validar_monto(monto):
    """
    Valida un monto monetario.

    Args:
        monto: Monto a validar

    Returns:
        bool: True si el monto es válido, False en caso contrario
    """
    try:
        # Convertir a float si es string
        if isinstance(monto, str):
            monto = float(monto)

        # Verificar que sea un número
        if not isinstance(monto, (int, float)):
            return False

        # Verificar que sea positivo
        if monto < 0:
            return False

        # Verificar rango máximo razonable (S/. 100,000)
        if monto > 100000:
            return False

        return True

    except (TypeError, ValueError):
        return False


def validar_producto_completo(nombre, precio, cantidad):
    """
    Valida un producto completo (nombre, precio y cantidad).

    Args:
        nombre (str): Nombre del producto
        precio (float): Precio del producto
        cantidad (int): Cantidad del producto

    Returns:
        dict: Diccionario con resultado de validación y mensajes de error
    """
    resultado = {
        'valido': True,
        'errores': []
    }

    # Validar nombre
    if not validar_nombre_producto(nombre):
        resultado['valido'] = False
        if not nombre or not nombre.strip():
            resultado['errores'].append("El nombre del producto no puede estar vacío")
        elif len(nombre.strip()) < 2:
            resultado['errores'].append("El nombre del producto debe tener al menos 2 caracteres")
        elif len(nombre.strip()) > 50:
            resultado['errores'].append("El nombre del producto no puede tener más de 50 caracteres")
        else:
            resultado['errores'].append("El nombre del producto no es válido")

    # Validar precio
    if not dato_valido(precio, 1):  # Usamos cantidad 1 para validar solo el precio
        resultado['valido'] = False
        if precio <= 0:
            resultado['errores'].append("El precio debe ser mayor que 0")
        elif precio > 10000:
            resultado['errores'].append("El precio no puede ser mayor que S/. 10,000")
        else:
            resultado['errores'].append("El precio no es válido")

    # Validar cantidad
    if not dato_valido(1, cantidad):  # Usamos precio 1 para validar solo la cantidad
        resultado['valido'] = False
        if cantidad <= 0:
            resultado['errores'].append("La cantidad debe ser mayor que 0")
        elif cantidad > 999:
            resultado['errores'].append("La cantidad no puede ser mayor que 999")
        else:
            resultado['errores'].append("La cantidad no es válida")

    return resultado


def limpiar_y_validar_entrada(entrada):
    """
    Limpia y valida una entrada de texto.

    Args:
        entrada (str): Texto a limpiar y validar

    Returns:
        str: Texto limpio y validado
    """
    if not isinstance(entrada, str):
        return ""

    # Eliminar espacios al inicio y final
    entrada = entrada.strip()

    # Eliminar caracteres especiales problemáticos
    caracteres_prohibidos = ['\n', '\r', '\t', '|', '"', "'"]
    for char in caracteres_prohibidos:
        entrada = entrada.replace(char, ' ')

    # Eliminar espacios múltiples
    while '  ' in entrada:
        entrada = entrada.replace('  ', ' ')

    return entrada


def formatear_precio(precio):
    """
    Formatea un precio para mostrar correctamente.

    Args:
        precio (float): Precio a formatear

    Returns:
        str: Precio formateado como "S/. XX.XX"
    """
    try:
        return f"S/. {float(precio):.2f}"
    except (TypeError, ValueError):
        return "S/. 0.00"


def calcular_igv(subtotal, porcentaje_igv=0.18):
    """
    Calcula el IGV de un subtotal.

    Args:
        subtotal (float): Subtotal sin IGV
        porcentaje_igv (float): Porcentaje de IGV (por defecto 18% = 0.18)

    Returns:
        float: Monto del IGV
    """
    try:
        return float(subtotal) * float(porcentaje_igv)
    except (TypeError, ValueError):
        return 0.0


def calcular_total_con_igv(subtotal, porcentaje_igv=0.18):
    """
    Calcula el total incluyendo IGV.

    Args:
        subtotal (float): Subtotal sin IGV
        porcentaje_igv (float): Porcentaje de IGV (por defecto 18% = 0.18)

    Returns:
        tuple: (igv, total) - Monto del IGV y total con IGV
    """
    try:
        subtotal = float(subtotal)
        igv = calcular_igv(subtotal, porcentaje_igv)
        total = subtotal + igv
        return igv, total
    except (TypeError, ValueError):
        return 0.0, 0.0
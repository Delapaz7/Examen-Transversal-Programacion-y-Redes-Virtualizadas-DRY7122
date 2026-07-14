import requests


URL_GEOCODIFICACION = "https://graphhopper.com/api/1/geocode"
URL_RUTA = "https://graphhopper.com/api/1/route"


def obtener_coordenadas(ciudad, pais, api_key):
    """
    Convierte el nombre de una ciudad en coordenadas geográficas.
    """

    parametros = {
        "q": f"{ciudad}, {pais}",
        "locale": "es",
        "limit": 1,
        "key": api_key
    }

    respuesta = requests.get(
        URL_GEOCODIFICACION,
        params=parametros,
        timeout=20
    )

    respuesta.raise_for_status()
    datos = respuesta.json()

    resultados = datos.get("hits", [])

    if not resultados:
        return None

    lugar = resultados[0]
    coordenadas = lugar["point"]

    return {
        "latitud": coordenadas["lat"],
        "longitud": coordenadas["lng"],
        "nombre": lugar.get("name", ciudad),
        "pais": lugar.get("country", pais)
    }


def calcular_ruta(origen, destino, transporte, api_key):
    """
    Calcula la ruta entre las coordenadas de origen y destino.
    """

    parametros = [
        (
            "point",
            f"{origen['latitud']},{origen['longitud']}"
        ),
        (
            "point",
            f"{destino['latitud']},{destino['longitud']}"
        ),
        ("profile", transporte),
        ("locale", "es"),
        ("instructions", "true"),
        ("calc_points", "false"),
        ("key", api_key)
    ]

    respuesta = requests.get(
        URL_RUTA,
        params=parametros,
        timeout=30
    )

    respuesta.raise_for_status()
    datos = respuesta.json()

    rutas = datos.get("paths", [])

    if not rutas:
        return None

    return rutas[0]


def convertir_duracion(milisegundos):
    """
    Convierte milisegundos en días, horas y minutos.
    """

    minutos_totales = int(milisegundos / 60000)

    dias = minutos_totales // 1440
    horas = (minutos_totales % 1440) // 60
    minutos = minutos_totales % 60

    partes = []

    if dias > 0:
        partes.append(f"{dias} día(s)")

    if horas > 0:
        partes.append(f"{horas} hora(s)")

    partes.append(f"{minutos} minuto(s)")

    return ", ".join(partes)


def seleccionar_transporte():
    """
    Permite seleccionar el medio de transporte.
    """

    print("\nSeleccione el medio de transporte:")
    print("1. Automóvil")
    print("2. Bicicleta")
    print("3. Caminando")
    print("s. Salir")

    opcion = input("Ingrese una opción: ").strip().lower()

    transportes = {
        "1": ("car", "Automóvil"),
        "2": ("bike", "Bicicleta"),
        "3": ("foot", "Caminando")
    }

    if opcion == "s":
        return "s"

    return transportes.get(opcion)


def mostrar_narrativa(instrucciones):
    """
    Muestra las indicaciones paso a paso del viaje.
    """

    print("\n============= NARRATIVA DEL VIAJE =============")

    if not instrucciones:
        print("No se encontraron instrucciones para esta ruta.")
        return

    for numero, instruccion in enumerate(instrucciones, start=1):
        texto = instruccion.get("text", "Continúe por la ruta")
        distancia_metros = instruccion.get("distance", 0)
        distancia_km = distancia_metros / 1000

        print(f"{numero}. {texto} — {distancia_km:.2f} km")


def main():
    print("===================================================")
    print("   VIAJE ENTRE UNA CIUDAD DE CHILE Y ARGENTINA")
    print("===================================================")

    api_key = input(
        "Ingrese su API Key de GraphHopper: "
    ).strip()

    if not api_key:
        print("Error: debe ingresar una API Key.")
        return

    while True:
        print("\nPuede ingresar la letra 's' para salir.")

        ciudad_origen = input(
            "Ciudad de Origen en Chile: "
        ).strip()

        if ciudad_origen.lower() == "s":
            print("Programa finalizado.")
            break

        ciudad_destino = input(
            "Ciudad de Destino en Argentina: "
        ).strip()

        if ciudad_destino.lower() == "s":
            print("Programa finalizado.")
            break

        seleccion = seleccionar_transporte()

        if seleccion == "s":
            print("Programa finalizado.")
            break

        if seleccion is None:
            print("Opción de transporte inválida.")
            continue

        perfil, nombre_transporte = seleccion

        try:
            print("\nBuscando las ciudades...")

            origen = obtener_coordenadas(
                ciudad_origen,
                "Chile",
                api_key
            )

            destino = obtener_coordenadas(
                ciudad_destino,
                "Argentina",
                api_key
            )

            if origen is None:
                print(
                    f"No se encontró la ciudad de origen: "
                    f"{ciudad_origen}."
                )
                continue

            if destino is None:
                print(
                    f"No se encontró la ciudad de destino: "
                    f"{ciudad_destino}."
                )
                continue

            print(
                f"Origen encontrado: "
                f"{origen['nombre']}, {origen['pais']}"
            )

            print(
                f"Destino encontrado: "
                f"{destino['nombre']}, {destino['pais']}"
            )

            print("\nCalculando la ruta...")

            ruta = calcular_ruta(
                origen,
                destino,
                perfil,
                api_key
            )

            if ruta is None:
                print(
                    "No fue posible calcular una ruta "
                    "entre las ciudades indicadas."
                )
                continue

            distancia_metros = ruta.get("distance", 0)
            duracion_milisegundos = ruta.get("time", 0)

            distancia_km = distancia_metros / 1000
            distancia_millas = distancia_km * 0.621371
            duracion = convertir_duracion(
                duracion_milisegundos
            )

            print("\n================ RESUMEN DEL VIAJE ================")
            print(
                f"Ciudad de Origen: "
                f"{origen['nombre']}, Chile"
            )
            print(
                f"Ciudad de Destino: "
                f"{destino['nombre']}, Argentina"
            )
            print(f"Medio de transporte: {nombre_transporte}")
            print(f"Distancia en kilómetros: {distancia_km:.2f} km")
            print(f"Distancia en millas: {distancia_millas:.2f} mi")
            print(f"Duración estimada: {duracion}")

            instrucciones = ruta.get("instructions", [])
            mostrar_narrativa(instrucciones)

            print("\n===================================================")

        except requests.exceptions.Timeout:
            print(
                "Error: la solicitud tardó demasiado tiempo."
            )

        except requests.exceptions.HTTPError as error:
            codigo = error.response.status_code

            if codigo == 401:
                print(
                    "Error 401: la API Key no es válida."
                )
            elif codigo == 429:
                print(
                    "Error 429: se alcanzó el límite "
                    "de solicitudes de la API."
                )
            else:
                print(
                    f"Error HTTP al consultar GraphHopper: "
                    f"{codigo}"
                )

        except requests.exceptions.RequestException as error:
            print(
                f"Error de conexión con GraphHopper: {error}"
            )

        continuar = input(
            "\n¿Desea calcular otro viaje? "
            "Presione Enter para continuar o 's' para salir: "
        ).strip().lower()

        if continuar == "s":
            print("Programa finalizado.")
            break


if __name__ == "__main__":
    main()
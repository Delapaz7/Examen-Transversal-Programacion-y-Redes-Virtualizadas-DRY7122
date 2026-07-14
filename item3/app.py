import getpass
import sqlite3
import sys
from pathlib import Path

from flask import Flask, render_template_string, request
from werkzeug.security import check_password_hash, generate_password_hash


# ---------------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------------

app = Flask(__name__)

# La base de datos se creará en la misma carpeta de app.py
RUTA_BASE_DATOS = Path(__file__).with_name("usuarios.db")

# Integrantes autorizados para ingresar al sitio
INTEGRANTES = [
    "Cristobal De la Paz",
    "Aldo Borotto",
    "Ambar Gonzalez"
]


# ---------------------------------------------------------
# PÁGINAS HTML
# ---------------------------------------------------------

PAGINA_LOGIN = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Inicio de sesión DRY7122</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #eef2f7;
        }

        .contenedor {
            width: 380px;
            margin: 80px auto;
            padding: 30px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
        }

        h1 {
            text-align: center;
            color: #243447;
            font-size: 25px;
        }

        p {
            text-align: center;
            color: #5d6d7e;
        }

        label {
            display: block;
            margin-top: 18px;
            margin-bottom: 6px;
            font-weight: bold;
            color: #34495e;
        }

        select,
        input {
            width: 100%;
            box-sizing: border-box;
            padding: 11px;
            border: 1px solid #aeb6bf;
            border-radius: 6px;
        }

        button {
            width: 100%;
            margin-top: 22px;
            padding: 12px;
            border: none;
            border-radius: 6px;
            background: #2471a3;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        button:hover {
            background: #1a5276;
        }

        .mensaje {
            margin-top: 18px;
            padding: 10px;
            background: #f8d7da;
            color: #842029;
            border-radius: 6px;
            text-align: center;
        }

        .pie {
            margin-top: 25px;
            font-size: 13px;
            color: #7f8c8d;
        }
    </style>
</head>

<body>

    <div class="contenedor">

        <h1>Validación de usuarios</h1>

        <p>Examen Transversal DRY7122</p>

        <form method="POST">

            <label for="usuario">Usuario</label>

            <select id="usuario" name="usuario" required>
                <option value="">Seleccione un integrante</option>

                {% for integrante in integrantes %}
                    <option value="{{ integrante }}">
                        {{ integrante }}
                    </option>
                {% endfor %}
            </select>

            <label for="clave">Contraseña</label>

            <input
                type="password"
                id="clave"
                name="clave"
                placeholder="Ingrese su contraseña"
                required
            >

            <button type="submit">
                Iniciar sesión
            </button>

        </form>

        {% if mensaje %}
            <div class="mensaje">
                {{ mensaje }}
            </div>
        {% endif %}

        <p class="pie">
            Las contraseñas se almacenan como hash en SQLite.
        </p>

    </div>

</body>
</html>
"""


PAGINA_EXITO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">

    <title>Acceso autorizado</title>

    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #eafaf1;
        }

        .contenedor {
            width: 450px;
            margin: 100px auto;
            padding: 35px;
            background: white;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.18);
        }

        h1 {
            color: #196f3d;
        }

        .usuario {
            font-size: 20px;
            font-weight: bold;
            color: #1f618d;
        }

        a {
            display: inline-block;
            margin-top: 25px;
            padding: 11px 20px;
            background: #2471a3;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        }
    </style>
</head>

<body>

    <div class="contenedor">

        <h1>Acceso autorizado</h1>

        <p>La contraseña ingresada es correcta.</p>

        <p class="usuario">
            Bienvenido, {{ usuario }}
        </p>

        <a href="/">
            Cerrar sesión
        </a>

    </div>

</body>
</html>
"""


# ---------------------------------------------------------
# FUNCIONES DE BASE DE DATOS
# ---------------------------------------------------------

def conectar_base_datos():
    """
    Crea una conexión con la base de datos SQLite.
    """

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.row_factory = sqlite3.Row

    return conexion


def crear_tabla_usuarios():
    """
    Crea la tabla usuarios si todavía no existe.
    """

    with conectar_base_datos() as conexion:

        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
            """
        )

        conexion.commit()


def guardar_usuario(usuario, password_hash):
    """
    Guarda un usuario nuevo o actualiza su hash.
    """

    with conectar_base_datos() as conexion:

        usuario_existente = conexion.execute(
            """
            SELECT id
            FROM usuarios
            WHERE usuario = ?
            """,
            (usuario,)
        ).fetchone()

        if usuario_existente:

            conexion.execute(
                """
                UPDATE usuarios
                SET password_hash = ?
                WHERE usuario = ?
                """,
                (password_hash, usuario)
            )

        else:

            conexion.execute(
                """
                INSERT INTO usuarios (
                    usuario,
                    password_hash
                )
                VALUES (?, ?)
                """,
                (usuario, password_hash)
            )

        conexion.commit()


def crear_usuarios():
    """
    Solicita una contraseña para cada integrante
    y almacena solamente su hash.
    """

    crear_tabla_usuarios()

    print("==============================================")
    print(" CREACIÓN DE USUARIOS DEL EXAMEN DRY7122")
    print("==============================================")

    print(
        "\nLa contraseña no aparecerá en pantalla "
        "mientras la escribes."
    )

    for usuario in INTEGRANTES:

        while True:

            print(f"\nUsuario: {usuario}")

            clave = getpass.getpass(
                "Ingrese una contraseña: "
            )

            confirmacion = getpass.getpass(
                "Confirme la contraseña: "
            )

            if len(clave) < 8:

                print(
                    "La contraseña debe tener "
                    "al menos 8 caracteres."
                )

                continue

            if clave != confirmacion:

                print(
                    "Las contraseñas no coinciden. "
                    "Inténtalo nuevamente."
                )

                continue

            password_hash = generate_password_hash(clave)

            guardar_usuario(
                usuario,
                password_hash
            )

            print(
                f"Usuario {usuario} almacenado correctamente."
            )

            break

    print("\nBase de datos creada correctamente.")
    print(f"Ubicación: {RUTA_BASE_DATOS}")


def buscar_usuario(usuario):
    """
    Busca un usuario dentro de SQLite.
    """

    with conectar_base_datos() as conexion:

        resultado = conexion.execute(
            """
            SELECT usuario, password_hash
            FROM usuarios
            WHERE usuario = ? COLLATE NOCASE
            """,
            (usuario,)
        ).fetchone()

    return resultado


# ---------------------------------------------------------
# SITIO WEB
# ---------------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def inicio():

    mensaje = None

    if request.method == "POST":

        usuario = request.form.get(
            "usuario",
            ""
        ).strip()

        clave = request.form.get(
            "clave",
            ""
        )

        usuario_encontrado = buscar_usuario(usuario)

        if usuario_encontrado is None:

            mensaje = "El usuario no se encuentra registrado."

        elif check_password_hash(
            usuario_encontrado["password_hash"],
            clave
        ):

            return render_template_string(
                PAGINA_EXITO,
                usuario=usuario_encontrado["usuario"]
            )

        else:

            mensaje = "La contraseña ingresada es incorrecta."

    return render_template_string(
        PAGINA_LOGIN,
        integrantes=INTEGRANTES,
        mensaje=mensaje
    )


# ---------------------------------------------------------
# EJECUCIÓN DEL PROGRAMA
# ---------------------------------------------------------

def mostrar_ayuda():

    print("Comandos disponibles:")

    print(
        "  python3 app.py crear-db"
        "    Crea la base de datos y los usuarios."
    )

    print(
        "  python3 app.py"
        "             Inicia el sitio web."
    )


if __name__ == "__main__":

    if len(sys.argv) > 1:

        comando = sys.argv[1].lower()

        if comando == "crear-db":

            crear_usuarios()

        else:

            print(f"Comando desconocido: {comando}")
            mostrar_ayuda()

    else:

        crear_tabla_usuarios()

        print("==============================================")
        print(" SITIO WEB DEL EXAMEN DRY7122")
        print("==============================================")
        print("Puerto utilizado: 5800")
        print("Dirección local: http://127.0.0.1:5800")
        print("Presione Ctrl + C para detener el servidor.")

        app.run(
            host="0.0.0.0",
            port=5800,
            debug=False
        )
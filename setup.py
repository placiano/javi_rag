import os
import sys
import subprocess
import venv
from pathlib import Path
import shutil

# Directorio del proyecto
PROJECT_DIR = Path(__file__).parent
VENV_DIR = PROJECT_DIR / ".venv"
ENV_FILE = PROJECT_DIR / ".env"

# Verificar si el entorno virtual existe
def is_venv_active():
    return sys.prefix != sys.base_prefix

# Encontrar el ejecutable de Python 3.11
def find_python_311():
    possible_executables = [
        "python3.11",  # Unix/Mac
        "python311",   # Windows (a veces)
        "/usr/bin/python3.11",  # Ruta común en Unix
        "/usr/local/bin/python3.11",  # Otra ruta común en Unix
        shutil.which("python3.11"),  # Busca en PATH
    ]
    for exe in possible_executables:
        if exe and os.path.exists(exe):
            try:
                result = subprocess.run([exe, "--version"], capture_output=True, text=True)
                if "Python 3.11" in result.stdout or "Python 3.11" in result.stderr:
                    return exe
            except Exception:
                continue
    return None

# Crear entorno virtual con Python 3.11
def create_venv():
    if not VENV_DIR.exists():
        python_311 = find_python_311()
        if not python_311:
            print("Error: No se encontró Python 3.11 en el sistema. Instálalo desde python.org.")
            sys.exit(1)
        
        print(f"Creando entorno virtual con {python_311}...")
        builder = venv.EnvBuilder(with_pip=True)
        # Crear el entorno usando el ejecutable específico
        subprocess.check_call([python_311, "-m", "venv", str(VENV_DIR)])
        print("Entorno virtual creado.")
    else:
        print("Entorno virtual ya existe.")

# Activar entorno virtual
def activate_venv():
    if sys.platform == "win32":
        activate_script = VENV_DIR / "Scripts" / "activate.bat"
    else:
        activate_script = VENV_DIR / "bin" / "activate"
    return str(activate_script)

# Crear archivo .env con secretos
def create_env_file():
    if not ENV_FILE.exists():
        api_key = input("Introduce tu clave de API de OpenAI: ")
        with open(ENV_FILE, "w") as f:
            f.write(f"OPENAI_API_KEY={api_key}\n")
        print(".env creado con éxito.")
    else:
        print(".env ya existe.")

# Instalar dependencias
def install_dependencies():
    pip_executable = VENV_DIR / "bin" / "pip" if sys.platform != "win32" else VENV_DIR / "Scripts" / "pip.exe"
    subprocess.check_call([str(pip_executable), "install", "-r", "requirements.txt"])
    print("Dependencias instaladas.")

def main():
    # Verificar si estamos en un venv
    if not is_venv_active():
        create_venv()
        print("Por favor, activa el entorno virtual manualmente:")
        print(f"  Windows: {activate_venv()}")
        print(f"  Unix/Mac: source {activate_venv()}")
        print("Luego ejecuta 'python setup.py' de nuevo.")
        sys.exit(1)
    
    # Crear .env si no existe
    create_env_file()
    
    # Instalar dependencias
    install_dependencies()
    
    print("Configuración completada. Puedes ejecutar 'streamlit run app.py' ahora.")

if __name__ == "__main__":
    # Verificar versión de Python actual
    if sys.version_info < (3, 11):
        print("Este script debe ejecutarse con Python 3.11 o superior para verificar correctamente.")
        print("Si tienes Python 3.11 instalado, usa 'python3.11 setup.py' en lugar de 'python setup.py'.")
        sys.exit(1)
    main()
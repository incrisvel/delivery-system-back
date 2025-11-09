from pathlib import Path
import subprocess
import sys
import os
import shutil

ROOT = Path(__file__).resolve().parent.parent
SERVICES = ["order_service", "delivery_service", "notification_service"]
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PIP = VENV / ("Scripts/pip.exe" if os.name == "nt" else "bin/pip")


def run(cmd):
    print(f"{cmd}")
    subprocess.run(cmd, shell=True, check=True, cwd=ROOT)


def venv():
    if not VENV.exists():
        run(f"python -m venv {VENV}")
        print("Ambiente virtual criado.")


def install_shared():
    venv()
    run(f"{PIP} install -r {ROOT / 'requirements.txt'}")


def install_service(service):
    venv()
    req = ROOT / "services" / service / "requirements.txt"
    if not req.exists():
        print(f"{service} não tem o arquivo requirements.txt")
        return
    run(f"{PIP} install -r {req}")


def install_all():
    install_shared()
    for s in SERVICES:
        install_service(s)


def clean():
    print("Limpando ambiente virtual e caches")
    shutil.rmtree(VENV, ignore_errors=True)
    for s in SERVICES:
        shutil.rmtree(ROOT / s / "__pycache__", ignore_errors=True)
    shutil.rmtree(ROOT / "__pycache__", ignore_errors=True)
    shutil.rmtree(ROOT / ".pytest_cache", ignore_errors=True)


if __name__ == "__main__":
    tasks = {
        "venv": venv,
        "install-shared": install_shared,
        "install-service": lambda: install_service(sys.argv[2]) if len(sys.argv) > 2 else print("Use: python scripts/tasks.py install-service <service>"),
        "install-all": install_all,
        "clean": clean,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in tasks:
        print("Comandos disponíveis:")
        for k in tasks:
            print(f"  python scripts/tasks.py {k}")
        sys.exit(0)

    tasks[sys.argv[1]]()

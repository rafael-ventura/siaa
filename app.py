import os, sys

# garante que modules/ fique no PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from config import configurar_pagina
from modules.web.pages.app_controller import AppController

def main():
    configurar_pagina()
    controller = AppController()
    controller.run()

if __name__ == "__main__":
    main()

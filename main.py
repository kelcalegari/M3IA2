import sys
import os
import tkinter as tk

from src.interface.gui import FaceAppGUI

# Adiciona o diretório src ao caminho de pesquisa do Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.interface.cli import menu

if __name__ == "__main__":
    #menu()
    root = tk.Tk()
    app = FaceAppGUI(root)
    root.mainloop()

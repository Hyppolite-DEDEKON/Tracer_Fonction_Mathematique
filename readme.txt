import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def plot_function(expression):
    x = np.linspace(-10, 10, 400)
    y = eval(expression, globals(), {'x': x})
    
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title('Courbe de la fonction')
    ax.set_xlabel('x')
    ax.set_ylabel('y')

    return fig

def on_submit():
    expression = entry.get()
    # Ajouter une évaluation de sécurité pour éviter des expressions potentiellement dangereuses
    try:
        fig = plot_function(expression)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=2, column=0)
    except Exception as e:
        print(f"Erreur lors de l'évaluation de l'expression : {e}")

# Interface utilisateur
window = tk.Tk()
window.title("Traceur de fonctions")

# Augmentation de la taille de la fenêtre
window.geometry("800x600")

label = tk.Label(window, text="Entrez une expression mathématique:")
label.grid(row=0, column=0)

entry = tk.Entry(window)
entry.grid(row=1, column=0)

submit_button = tk.Button(window, text="Tracer la fonction", command=on_submit)
submit_button.grid(row=1, column=1)

window.mainloop()

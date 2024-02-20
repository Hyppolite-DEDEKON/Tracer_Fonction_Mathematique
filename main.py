import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_pdf import PdfPages

fig = None  

def plot_function(expression, x):
    y = eval(expression, globals(), {'x': x})
    
    global fig 
    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_title('Graphique de la fonction')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    return fig

def on_submit():
    global fig 
    expression = entry.get()
    start_value = float(start_entry.get())
    end_value = float(end_entry.get())

    x = np.linspace(start_value, end_value, 400)
    
    try:
        fig = plot_function(expression, x)
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.grid(row=2, column=0)
    except Exception as e:
        print(f"Erreur lors de l'évaluation de l'expression : {e}")

def export_graph():
    try:
        global fig  
        if fig is not None:  
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")])
            if file_path:
                if file_path.endswith(".pdf"):
                    with PdfPages(file_path) as pdf:
                        pdf.savefig(fig)
                else:
                    fig.savefig(file_path)
    except Exception as e:
        print(f"Erreur lors de l'exportation du graphique : {e}")



def show_help():
    message = "Bienvenue dans l'application Traceur de fonctions !\n\n"\
              "Entrez une expression mathématique dans la zone de texte.\n"\
              "Vous pouvez également spécifier l'intervalle de valeurs pour x.\n"\
              "Cliquez sur 'Tracer la fonction' pour afficher le graphique.\n"\
              "Explorez les options de style graphique et exportez le graphique si nécessaire."
    messagebox.showinfo("Aide", message)

# Interface utilisateur
window = tk.Tk()
window.title("Traceur de fonctions")
window.geometry("800x650")

label = tk.Label(window, text="Entrez une expression mathématique:")
label.grid(row=0, column=0)

entry = tk.Entry(window)
entry.grid(row=1, column=0)

start_label = tk.Label(window, text="Début de l'intervalle:")
start_label.grid(row=0, column=1)
start_entry = tk.Entry(window)
start_entry.grid(row=1, column=1)

end_label = tk.Label(window, text="Fin de l'intervalle:")
end_label.grid(row=2, column=1)
end_entry = tk.Entry(window)
end_entry.grid(row=3, column=1)

submit_button = tk.Button(window, text="Tracer la fonction", command=on_submit)
submit_button.grid(row=3, column=0)

export_button = tk.Button(window, text="Exporter le graphique", command=export_graph)
export_button.grid(row=5, column=0)

help_button = tk.Button(window, text="Aide", command=show_help)
help_button.grid(row=0, column=7)

window.mainloop()
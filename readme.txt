Traceur de fonctions mathématiques
==================================

Application de bureau (Python + Tkinter + Matplotlib) pour tracer une ou plusieurs
fonctions f(x) sur un intervalle, avec export et thème clair / sombre.

Structure
---------

  main.py
  requirements.txt
  tests/
  tracer/
    app.py
    core/          calcul, tracé, segments aux discontinuités
    services/      export PNG / PDF / SVG
    ui/            thème, fenêtre, aide

Installation
------------

  sudo apt install python3-numpy python3-matplotlib python3-tk

Environnement virtuel :

  python3 -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt

Lancement
---------

  python3 main.py

Fonctionnalités
---------------

  • Jusqu'à 3 courbes superposées
  • Intervalle x personnalisé, nombre de points réglable
  • Style : couleur, épaisseur, grille, axes, coupure aux asymptotes
  • Mode sombre
  • Export PNG, PDF, SVG
  • Raccourcis : Ctrl+Entrée (tracer), Ctrl+E (export), Ctrl+L (effacer)

Tests
-----

  pip install pytest
  pytest

Fonctions mathématiques
-----------------------

  sin, cos, tan, asin, acos, atan, sinh, cosh, tanh,
  exp, log, log10, sqrt, abs, floor, ceil
  Constantes : pi, e

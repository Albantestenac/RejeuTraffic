# -*- coding: utf-8 -*-
author = 'Audrey', 'Alban'

import pyrejeu.models as mod
from sqlalchemy.orm import sessionmaker
from math import *

Session = sessionmaker(bind=mod.engine)
session = Session()

def set_heading(f_id, heading, time): # time en sec

    # On prend dans le bdd le plot au niveau duquel la cmde de changement de cap a été envoyée.
    starting_cone = session.query(mod.Cone).filter \
        (mod.Cone.flight_id == f_id, mod.Cone.hour >= time, mod.Cone.version == mod.Cone.last_version).order_by(mod.Cone.hour).first()
    list_cones = [starting_cone] # liste_cones contient strating_cone et sera complété des plots calculés pour le changement de cap demandé.

    # !!! On ne doit changer la vitesse que du deuxième plot !!! --> A corriger !!!
    # Calculer la nouvelle position et les nouvelles vitesses (en x et y) de starting cone et la rajouter à la bdd.

    incrementation_time = 8 # On crée des plots successifs espacés dans le temps de 8sec (comme sur exemple_donnees.txt).
    for (i, t) in enumerate(range(starting_cone.hour, time+3600, incrementation_time)): # Création de la liste des nouveaux plots pendant 1h.

        n_pos_x = incrementation_time * list_cones[i].vit_x # Position en x du plot i+1.
        n_pos_y = incrementation_time * list_cones[i].vit_y # Position en y du plot i+1.

        speed_vector_norm = math.sqrt(list_cones[i].vit_x ** 2 + list_cones[i].vit_y ** 2) # Calcul de la norme du vecteur vitesse au plot i.
        n_vit_x = speed_vector_norm*sin(heading) # Calcul de la vitesse en x du plot i+1 en considérant que les vecteurs vitesse du plot i et i+1 aient la même norme.
        n_vit_y = speed_vector_norm*cos(heading) # Calcul de la vitesse en y du plot i+1 en considérant que les vecteurs vitesse du plot i et i+1 aient la même norme.

        # On considère que l'avion reste à la même altitude pendant tout la suite du vol.
        n_cone = mod.Cone(version=2,
                 pos_x=n_pos_x, pos_y=n_pos_y,
                 vit_x=n_vit_x, vit_y=n_vit_y,
                 flight_level=starting_cone.flight_level, rate=0, tendency=0,
                 hour=t, flight_id=f_id)

        session.add(n_cone) # On ajoute n_cone à la bdd.
        list_cones.append(n_cone)


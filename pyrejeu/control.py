# -*- coding: utf-8 -*-
author = 'Audrey', 'Alban'

import pyrejeu.models as mod
from sqlalchemy.orm import sessionmaker
from math import *

Session = sessionmaker(bind=mod.engine)
session = Session()



# Calcul des nouveaux plots à partir de la cmde de changement de cap.
def set_heading(f_id, heading, time): # time en sec

    incrementation_time = 8 # On crée des plots successifs espacés dans le temps de 8sec (comme sur exemple_donnees.txt).

    # On prend dans la bdd tout les plots à partir desquels la cmde de changement de cap a été envoyée
    # + le plot juste avant l'ordre de cmde (si la cmde n'a pas été envoyée sur une heure multiple de 8).
    list_cones_sup_time = session.query(mod.Cone).filter \
        (mod.Cone.flight_id == f_id, mod.Cone.hour >= (time-incrementation_time+1), mod.Cone.version == mod.Cone.flight.last_version)
    starting_cone = list_cones_sup_time[0] # Plot de départ.
    last_cone = list_cones_sup_time[-1] # Dernier plot de la dernière trajectoire de l'avion.
    list_cones = [starting_cone] # liste_cones contient strating_cone en 1er élément et sera complété des plots calculés à partir du nouveau cap.

    # On incrémente last_version du vol associé à l'avion.
    mod.Cone.flight.last_version += 1

    # On considère que la vitesse de l'avion sera constante.
    speed_vector_norm = math.sqrt(starting_cone.vit_x**2 + starting_cone.vit_y**2)  # Calcul de la norme du vecteur vitesse au plot de départ.
    n_vit_x = speed_vector_norm * math.sin(math.radians(heading))  # Calcul de la vitesse en x des nouveaux plots.
    n_vit_y = speed_vector_norm * math.cos(math.radians(heading))  # Calcul de la vitesse en y des nouveaux plots.

    end_time = last_cone.hour
    for (i, t) in enumerate(range(starting_cone.hour, end_time, incrementation_time)): # Création de la liste des nouveaux plots.

        n_pos_x = incrementation_time * list_cones[i].vit_x # Position en x du plot i+1.
        n_pos_y = incrementation_time * list_cones[i].vit_y # Position en y du plot i+1.

        # Définition du nouveau plot.
        # On considère que l'avion restera à la même altitude.
        n_cone = mod.Cone(version=starting_cone.last_version+1,
                 pos_x=n_pos_x, pos_y=n_pos_y,
                 vit_x=n_vit_x, vit_y=n_vit_y,
                 flight_level=starting_cone.flight_level, rate=0, tendency=0,
                 hour=t, flight_id=f_id)

        session.add(n_cone) # On ajoute n_cone à la bdd.
        list_cones.append(n_cone)



def delete_version(truc, machin):

    mod.Cone.flight.last_version -= 1



    pass

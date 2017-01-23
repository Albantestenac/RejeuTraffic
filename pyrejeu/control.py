# -*- coding: utf-8 -*-
author = 'Audrey', 'Alban'

import models as mod
from sqlalchemy.orm import sessionmaker
from math import *

Session = sessionmaker(bind=mod.engine)
session = Session()



# Calcul des nouveaux plots pour un changement de cap.
def set_heading(f_id, heading, time): # time en sec

    incrementation_time = 8 # Deux plots successifs sont séparés de 8sec.

    # Recherche du plot de début du changement de cap.
    list_cones_sup_time = session.query(mod.Cone).filter \
        (mod.Cone.flight_id == f_id, mod.Cone.hour >= (time-incrementation_time+1), mod.Cone.version == mod.Cone.flight.last_version)
    starting_cone = list_cones_sup_time[0] # Plot de départ.
    list_cones = [starting_cone]

    mod.Cone.flight.last_version += 1

    # On considère que la vitesse de l'avion sera constante.
    speed_vector_norm = math.sqrt(starting_cone.vit_x**2 + starting_cone.vit_y**2)  # Calcul de la norme du vecteur vitesse au plot de départ.
    n_vit_x = speed_vector_norm * math.sin(math.radians(heading))  # Calcul de la vitesse en x des nouveaux plots.
    n_vit_y = speed_vector_norm * math.cos(math.radians(heading))  # Calcul de la vitesse en y des nouveaux plots.

    end_time = list_cones_sup_time[-1].hour
    for (i, t) in enumerate(range(starting_cone.hour, end_time, incrementation_time)): # Définition des paramètres des nouveaux plots.

        n_pos_x = incrementation_time * list_cones[i].vit_x # Position en x du plot i+1.
        n_pos_y = incrementation_time * list_cones[i].vit_y # Position en y du plot i+1.

        # On considère que l'avion restera à la même altitude.
        n_cone = mod.Cone(version=starting_cone.last_version+1,
                 pos_x=n_pos_x, pos_y=n_pos_y,
                 vit_x=n_vit_x, vit_y=n_vit_y,
                 flight_level=starting_cone.flight_level, rate=0, tendency=0,
                 hour=t, flight_id=f_id)

        session.add(n_cone)
        list_cones.append(n_cone)


# Suppression la dernière version.
def delete_last_version(f_id):

    list_cones_last_version = session.query(mod.Cone).filter \
        (mod.Cone.flight_id == f_id, mod.Cone.version == mod.Cone.flight.last_version)

    for i, elt in enumerate(list_cones_last_version):
        session.delete(list_cones_last_version[i])

    mod.Cone.flight.last_version -= 1



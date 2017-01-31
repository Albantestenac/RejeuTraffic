# -*- coding: utf-8 -*-
author = 'Audrey', 'Alban'

import models as mod
import math
import utils
import logging


def set_heading(session, f_id, target_heading, time, side, rate):
    """
    Calcul des nouveaux plots pour un changement de cap.

    :param session:

    :param f_id: Identifiant du vol (Int)

    :param target_heading: Valeur du nouveau cap (Int)

    :param time: Heure de début en sec (Int)

    :param side: Côté de virage demandé (Str: "Right" ou "Left")

    :param rate: Taux de virage en °/sec (Int)

    :return: NONE
    """

    incrementation_time = 8 # Deux plots successifs sont séparés de 8sec.

    flight = session.query(mod.Flight).filter(mod.Flight.id == f_id).first()

    # Recherche du plot de début du changement de cap.
    list_cones_sup_time = session.query(mod.Cone) \
        .join(mod.Cone.flight) \
        .filter(mod.Cone.flight_id == f_id,
                mod.Cone.hour >= (time-incrementation_time+1),
                mod.Cone.version == mod.Flight.last_version)
    starting_cone = list_cones_sup_time[0]
    end_time = list_cones_sup_time[-1].hour                         #Heure du dernier plot

    # Copie et incrémentation de la version des plots situés avant et au changement de cap.
    list_cones_inf_time = session.query(mod.Cone) \
        .join(mod.Cone.flight) \
        .filter(mod.Cone.flight_id == f_id,
                mod.Cone.hour < (time - incrementation_time + 1),
                mod.Cone.version == mod.Flight.last_version).all()
    list_cones = []
    for cone in list_cones_inf_time:
        cone.version += 1
        list_cones.append(cone)

    #Liste des plots modifiés
    modified_cones = [starting_cone]

    # Norme du vecteur vitesse (constante pour tous les plots suivants la modification)
    speed_vector_norm = math.sqrt(starting_cone.vit_x**2 + starting_cone.vit_y**2)

    #Construction des caps successifs en fonction du taux et du coté demandé
    current_heading = utils.get_heading(starting_cone.vit_x, starting_cone.vit_y)
    headings = capture_heading(current_heading, target_heading, side, rate, incrementation_time)
    j=0
    # Définition des paramètres des nouveaux plots.
    for (i, t) in enumerate(range(starting_cone.hour, end_time, incrementation_time)):
        if j<len(headings):
            n_vit_x = speed_vector_norm * math.sin(math.radians(headings[j]))  # Vitesse en x des nouveaux plots dans le virage (kts)
            n_vit_y = speed_vector_norm * math.cos(math.radians(headings[j]))  # Vitesse en y des nouveaux plots dans le virage (kts)
            j+=1
        else:
            n_vit_x = speed_vector_norm * math.sin(math.radians(target_heading))  # Vitesse en x des nouveaux plots. (kts)
            n_vit_y = speed_vector_norm * math.cos(math.radians(target_heading))  # Vitesse en y des nouveaux plots. (kts)
        if i==0:
            n_pos_x = modified_cones[i].pos_x
            n_pos_y = modified_cones[i].pos_y
        else:
            n_pos_x = modified_cones[i].pos_x + incrementation_time * modified_cones[i].vit_x / 3600 * 64  # Position en x (1/64 NM) du plot i+1.
            n_pos_y = modified_cones[i].pos_y + incrementation_time * modified_cones[i].vit_y / 3600 * 64  # Position en y (1/64 NM) du plot i+1.
        if i<10:
            logging.debug("Plot h=%s: pos_x=%f pos_y=%f vit_x=%f vit_y=%f" % (utils.sec_to_str(modified_cones[i].hour), modified_cones[i].pos_x, modified_cones[i].pos_y,
                                                                              modified_cones[i].vit_x, modified_cones[i].vit_y))

        # On considère que l'avion restera à la même altitude.
        n_cone = mod.Cone(version=starting_cone.flight.last_version+1,
                 pos_x=n_pos_x, pos_y=n_pos_y,
                 vit_x=n_vit_x, vit_y=n_vit_y,
                 flight_level=starting_cone.flight_level, rate=0, tendency=0,
                 hour=t+incrementation_time, flight_id=f_id, flight=flight)
        modified_cones.append(n_cone)

    list_cones += modified_cones
    session.add_all(list_cones)
    flight.last_version += 1
    session.commit()


def delete_last_version(session, f_id):
    """
    Suppression la dernière version de la trajectoire.

    :param session:

    :param f_id: Num de vol (Int).

    :return: NONE
    """
    flight = session.query(mod.Flight).filter(mod.Flight.id == f_id).first()

    list_cones_last_version = session.query(mod.Cone) \
        .join(mod.Cone.flight) \
        .filter(mod.Cone.flight_id == f_id,
                mod.Cone.version == mod.Flight.last_version)

    for cone in list_cones_last_version:
        session.delete(cone)
    flight.last_version -= 1
    session.commit()

def capture_heading(current_hdg, target_hdg, side, rate, incrementation_time=8):
    """
    Calcule le cap que prend l'avion pour chaque plot du virage.

    :param current_hdg: Cap actuel (Int)

    :param target_hdg: Cap demandé (Int)

    :param side: Côté du virage (Str: "Right" ou "Left")

    :param rate: Taux de virage en °/sec (Int)

    :param incrementation_time: 8sec

    :return: headings: Liste des caps (1cap/8sec) à suivre dans le virage (List)
    """
    headings = []
    if side=="":
        if target_hdg > current_hdg:
            side="Right"
        else:
            side="Left"
    if (target_hdg > current_hdg) and side=="Right":
        headings += range(current_hdg, target_hdg, rate*incrementation_time)    #Caps entre cap actuel et cible
    elif (target_hdg > current_hdg) and side=="Left":
        headings += range(current_hdg, 0, -rate*incrementation_time)            # Caps entre cap actuel et cap le plus proche de 0
        headings.append((headings[-1]-rate*incrementation_time)%360)            # Passage du cap 0
        if headings[-1]==0: headings[-1]=360                                    # Mise au cap 360
        headings += range(headings[-1]-rate*incrementation_time, target_hdg, -rate*incrementation_time)  # Caps entre celui le plus proche de 360 et cible
    elif (target_hdg < current_hdg) and side=="Right":
        headings += range(current_hdg, 360, rate*incrementation_time)
        headings.append((headings[-1]+rate*incrementation_time)%360)                 # Passage du cap 0
        headings += range(headings[-1]+rate*incrementation_time, target_hdg, rate*incrementation_time)
    elif (target_hdg < current_hdg) and side=="Left":
        headings += range(current_hdg, target_hdg, -rate*incrementation_time)
    headings.append(target_hdg)
    return headings

if __name__ == '__main__':
    print("Cap 120 à 248, droite, 3°/s")
    print(capture_heading(120, 248, "Right", 3))

    print("Cap 120 à 248, gauche, 3°/s")
    print(capture_heading(120, 248, "Left", 3))

    print("Cap 248 à 120, droite, 3°/s")
    print(capture_heading(248, 120, "Right", 3))

    print("Cap 248 à 120, gauche, 3°/s")
    print(capture_heading(248, 120, "Left", 3))

    print("Cap 120 à 15, droite, 3°/s")
    print(capture_heading(120, 15, "Right", 3))

    print("Cap 120 à 15, gauche, 3°/s")
    print(capture_heading(120, 15, "Left", 3))




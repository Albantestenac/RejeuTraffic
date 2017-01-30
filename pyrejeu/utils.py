# -*- coding: utf-8 -*-
__author__ = "Alban", "Audrey"

import math
import traceback
import logging


def log_traceback(level="info"):
    log_func = level == "info" and logging.info or logging.error
    log_func("------------------Traceback lines--------------------")
    log_func(traceback.format_exc())
    log_func("-----------------------------------------------------")


def str_to_sec(string):
    """
    Convertit une chaine de caractere au format HH:MM:SS en un nombre de secondes (depuis 00:00:00)
    :param string: Heure au format HH:MM:SS (Str)
    :return: Nombre de secondes ecoulees depuis 00:00:00 (Int)
    """
    (h,m,s)= string.split(':')
    return int(h)*3600 + int(m)*60 + int(s)


def sec_to_str(nb_sec):
    """
    Convertit un nombre de seconde donne en une chaine au format HH:MM:SS
    :param nb_sec: nombre de seconde du temps a convertir (Int)
    :return: Heure au format HH:MM:SS (Str)
    """
    h = nb_sec//3600
    nb_sec -= h*3600
    m = nb_sec // 60
    s = nb_sec - m*60
    return "%02d:%02d:%02d" % (h, m, s)


def sec_to_str_without_sec(nb_sec):
    """
    Convertit un nombre de seconde donnÉ en une chaine au format HH:MM
    :param nb_sec: Nombre de secondes du temps à convertir (Int)
    :return: Heure au format HH:MM (Str)
    """
    h = nb_sec//3600
    nb_sec -= h*3600
    m = nb_sec // 60
    return "%02d:%02d" % (h, m)

def extract_sim_bounds(flight_list):
    """
    Revoie l'heure de début et l'heure de fin de la simulation à partir d'une liste de vols
    :param flight_list: liste de vols (List)
    :return: start_h: heure de début (Int) et stop_h: heure de fin de simulation (Int)
    """
    (start_h, stop_h) = (flight_list[0].h_dep, flight_list[0].h_arr)
    for flight in flight_list:
        if flight.h_dep < start_h:
            start_h = flight.h_dep
        if flight.h_arr > stop_h:
            stop_h = flight.h_arr

    #Si les heures sortent des limites
    if start_h < 0: start_h = 0
    if stop_h > str_to_sec("23:59:59"): stop_h = str_to_sec("23:59:59")

    return (start_h, stop_h)


def layer_s_name_from_FL(layers_list, fl):
    """
    Trouve le nom de la couche à partir du niveau de vol.
    :param layers_list: liste des couches (List)
    :param fl: niveau de vol (Int)
    :return: found_name: le nom de la couche (Str)
    """
    for layer in layers_list:
        if fl >= layer.floor and fl < layer.ceiling:
            found_name = layer.name
    return found_name


def extract_route(flight_plan, start_beacon=None, start_time=None):
    """
    Fonction renvoyant le plan de vol au format "NOM (V ou A) HEURE FL "
    :param flight_plan: Objet de type FlightPlan
    :param start_beacon: 1er plot (Str)
    :param start_time: Dernier plot (Str)
    :return: res : plan de vol au format "NOM (V ou A) HEURE FL " (Str)
    """
    res=""
    start = 0
    if start_beacon == None:
        if start_time == None:
            start = 0;
        else:
            for (i, beacon) in enumerate(flight_plan.beacons):
                if beacon.hour >= start_time:
                    start = i
                    break
    else:
        for (i,beacon) in enumerate(flight_plan.beacons):
            if beacon.beacon_name == start_beacon:
                start = i
                break
    for b in flight_plan.beacons[start:]:
        res += b.beacon_name + " "
        res += b.V_or_A + " "
        res += sec_to_str_without_sec(b.hour) + " "
        res += str(b.FL) + " "
    return res

def get_heading(x_speed, y_speed):
    """
    Obtient la cap à partir des vitesses sur le plan horizontal.
    :param x_speed: Vitesse en x (Int)
    :param y_speed: Vitesse en y (Int)
    :return: Cap en ° (Int)
    """
    if x_speed == 0:
        if y_speed >= 0: return 0
        else: return 180
    angle = math.atan(y_speed/x_speed)

    if x_speed > 0: return int(math.degrees(math.pi/2 - angle))
    else: return int(math.degrees(3*math.pi/2 - angle))


if __name__ == "__main__":
    print str_to_sec("13:20:50")
    print sec_to_str(str_to_sec("13:20:50"))
    print get_heading(0,-1)


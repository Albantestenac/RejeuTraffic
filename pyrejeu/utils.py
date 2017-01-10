# -*- coding: utf-8 -*-
__author__ = "Alban", "Audrey"


def str_to_sec(string):
    """
    Convertit une chaine de caractere au format HH:MM:SS en un nombre de secondes (depuis 00:00:00)
    :param string: chaine de caractere au format HH:MM:SS
    :return: Entier correspondant au nombre de secondes ecoulees depuis 00:00:00
    """
    (h,m,s)= string.split(':')
    return int(h)*3600 + int(m)*60 + int(s)


def sec_to_str(nb_sec):
    """
    Convertit un nombre de seconde donne en une chaine au format HH:MM:SS
    :param nb_sec: nombre de seconde du temps a convertir
    :return: Chaine de caractere au format HH:MM:SS
    """
    h = nb_sec//3600
    nb_sec -= h*3600
    m = nb_sec // 60
    s = nb_sec - m*60
    return "%02d:%02d:%02d" % (h, m, s)


def sec_to_str_without_sec(nb_sec):
    """
    Convertit un nombre de seconde donne en une chaine au format HH:MM
    :param nb_sec: nombre de seconde du temps a convertir
    :return: Chaine de caractere au format HH:MM
    """
    h = nb_sec//3600
    nb_sec -= h*3600
    m = nb_sec // 60
    return "%02d:%02d" % (h, m)

def extract_sim_bounds(flight_list):
    """
    Revoie l'heure de début et l'heure de fin de la simulation à partir d'une liste de vols
    :param flight_list:
    :return:
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
    for layer in layers_list:
        if fl >= layer.floor and fl < layer.ceiling:
            found_name = layer.name
    return found_name


if __name__ == "__main__":
    print str_to_sec("13:20:50")
    print sec_to_str(str_to_sec("13:20:50"))


author = 'Alban'

import Models as mod
import Clock
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=mod.engine)

def line_search(filename, beginning_pattern, ending_pattern):
    """
    Extrait une liste de lignes comprises entre deux motifs (non inclus) a partir d'un fichier texte passe en parametre
    :param filename: fichier texte contenant les lignes a extraire
    :param beginning_pattern: motif indiquant le debut des lignes utiles
    :param ending_pattern: motif indiquant la fin des lignes utiles
    :return: list_lines: liste de chaine de caracteres correspondant aux lignes utiles (un element = une ligne)
    """
    with open(filename, 'r') as f:
        (start, end) = (0, 0)
        lines = f.readlines()
        for (i, line) in enumerate(lines):
            if beginning_pattern in line:
                start = i+1
            if ending_pattern in line:
                end = i
        list_lines = lines[start:end]
    return list_lines

def f_import_beacons(filename):
    """
    Importe les donnees relative aux balise a partir d un fichier texte passe en entree et les stocke dans la BDD
    :param filename: fichier texte contenant les balises a importer
    :return: 0 si correctement importe, 1 sinon
    """
    l_beacons = line_search(filename, "NBeacons:", "########## Layers")

    if l_beacons == []:
        print("Aucune balise dans le fichier %s") % (filename)
        return 1

    for beacon in l_beacons:
        (b_name, b_x_pos, b_y_pos) = beacon.split()[0:3]                  #Attention: la position est une str ici, pas un entier
        tmp_beacon = mod.Beacon(name=b_name, pos_x=int(b_x_pos), pos_y=int(b_y_pos))
        #Remplissage des tables avec les balises
        tmp_session = Session()
        if (tmp_session.query(mod.Beacon).filter(mod.Beacon.name==b_name).first()) == None :
            #Ajout de la balise a la bdd si elle n'y est pas deja
            tmp_session.add(tmp_beacon)
        else:
            #Cas ou une balise portant le meme nom est dans la bdd
            conflicting_beacon = tmp_session.query(mod.Beacon).filter(mod.Beacon.name == b_name).first()
            if conflicting_beacon is not tmp_beacon:
            #Modification des champs si differents
                if conflicting_beacon.pos_x != b_x_pos:
                    conflicting_beacon.pos_x = b_x_pos
                elif conflicting_beacon.pos_y != b_y_pos:
                    conflicting_beacon.pos_y = b_y_pos
        tmp_session.commit()
    return 0

def f_import_flights(filename):
    """
    Importe les donnees relative aux vols a partir d un fichier texte passe en entree et les stocke dans la BDD
    :param filename: fichier texte contenant les vols a importer
    :return:
    """
    with open(filename, 'r') as f:
        (start, count, nb_vols) = (0, 0, 0)
        l_flights= []
        lines = f.readlines()
        for (i, line) in enumerate(lines):
            if "NbVols:" in line:
                nb_vols = int(line.split()[1])
                start = i
            if start > i and "$" in line and count<=nb_vols:
                l_flights.add(line)
                count += 1

    #Remplissage des tables
    for beacon in l_flights:
        (f_id, f_h_dep, f_h_arr, f_fl, f_speed, f_callsign, f_type, f_dep, f_arr) = beacon.split()[1:10]
        #Conversions
        f_h_dep = Clock.str_to_sec(f_h_dep)
        f_h_arr = Clock.str_to_sec(f_h_arr)

        #Ecriture dans un objet Flight
        tmp_flight = mod.Flight(id=f_id, h_dep=f_h_dep, h_arr=f_h_arr, fl=int(f_fl), v=int(f_speed), callsign=f_callsign,
                                type=f_type, dep=f_dep, arr=f_arr)

        #Remplissage des tables avec les vols
        tmp_session = Session()
        if (tmp_session.query(mod.Flight).filter(mod.Flight.id==f_id).first()) == None :
            #Ajout du vol a la bdd si il n'y est pas deja
            tmp_session.add(tmp_flight)
        else:
            #Cas ou un vol ayant le meme id est dans la bdd
            conflicting_flight = tmp_session.query(mod.Flight).filter(mod.Flight.id == f_id).first()
            if conflicting_flight is not tmp_flight:
            #Modification des champs si differents
                pass
        tmp_session.commit()
    return 0




print("Importation des balises ...")
f_import_beacons("../exemple_donnees.txt")
print("Fait")
print("Importation des vols ...")
f_import_flights("../exemple_donnees.txt")
print("Fait")

#Test rapide sur la BDD importee
session_test = Session()
test_beacon = session_test.query(mod.Beacon).first()
print test_beacon
test_flight = session_test.query(mod.Flight).first()
print test_flight
session_test.commit()

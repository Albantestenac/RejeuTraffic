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
        (start, nb_vols) = (0, 0)
        l_flights= []
        lines = f.readlines()
        for (i, line) in enumerate(lines):
            if "NbVols:" in line:
                start = i
            if start > 0 and i>start and "$" in line:
                l_flights.append(line)

    l_id = []
    #Remplissage des tables
    for flight in l_flights:
        (f_id, f_h_dep, f_h_arr, f_fl, f_speed, f_callsign, f_type, f_dep, f_arr) = flight.split()[1:10]
        #Conversions
        f_h_dep = Clock.str_to_sec(f_h_dep)
        f_h_arr = Clock.str_to_sec(f_h_arr)

        #Ecriture dans un objet Flight
        tmp_flight = mod.Flight(id=int(f_id), h_dep=f_h_dep, h_arr=f_h_arr, fl=int(f_fl), v=int(f_speed), callsign=f_callsign,
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
        l_id.append(int(f_id))
    return l_id


def f_import_plots(filename, flight_id):
    """
    Importe les donnees des plots correspondant a un vol a partir du fichier apsse en parametre et les stock dans la bdd
    :param filename: Nom du fichier contenant les donnes
    :param flight_id: identifiant du vol dont on veut recuperer les plots
    :return:
    """
    #Extraction des lignes concernant les plots du vol
    with open(filename, 'r') as f:
        (block_start, block_end, marker) = (0, 0, 0)
        lines = f.readlines()
        for (i, line) in enumerate(lines):
            if "NbVols:" in line:
                marker = i
            if marker > 0 and i>marker and ("$" and str(flight_id) in line):
                marker = i
            if marker > 0 and i>marker and "NbPlots:" in line:
                block_start = i+1                                     #debut du bloc = ligne premier plot
                block_end = block_start + int(line.split()[1])        #fin du bloc = ligne du dernier plot + 1 (ATTENTION)
                break                                                 #On quitte une fois fini
        l_cones = lines[block_start:block_end]

    #Remplissage des tables
    for cone in l_cones:
        (c_hour, c_pos_x, c_pos_y, c_vit_x, c_vit_y, c_fl, c_rate, c_tendency) = cone.split()

        #Conversion
        c_hour = Clock.str_to_sec(c_hour)

        # Ecriture dans un objet Cone
        tmp_cone = mod.Cone(pos_x=int(c_pos_x), pos_y=int(c_pos_y), vit_x=int(c_vit_x), vit_y=int(c_vit_y), flight_level=int(c_fl),
                            rate=int(c_rate), hour=c_hour, flight=flight_id)

        # Remplissage des tables avec les cones
        tmp_session = Session()
        tmp_session.add(tmp_cone)
        tmp_session.commit()


    return 0



# print("Importation des balises ...")
# f_import_beacons("../exemple_donnees.txt")
# print("Fait")
print("Importation des vols ...")
liste_vols = f_import_flights("../exemple_donnees.txt")
print("Fait")
print ("Importation des plots ...")
for id_vol in liste_vols:
    f_import_plots("../exemple_donnees.txt", id_vol)
print "Fait"

# #Test rapide sur la BDD importee
# session_test = Session()
# test_beacon = session_test.query(mod.Beacon).first()
# print test_beacon
# test_flight = session_test.query(mod.Flight).first()
# print test_flight
# session_test.commit()
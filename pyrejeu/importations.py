# -*- coding: utf-8 -*-
author = 'Alban', 'Alexandre'

import sys
import os.path
import logging
from sqlalchemy.orm import sessionmaker
import pyrejeu.models as mod
from pyrejeu import utils
from pyrejeu import PyRejeuException

Session = sessionmaker(bind=mod.engine)


class RejeuImportation(object): 

    def __init__(self):
        self.session = Session()

    def import_file(self, filename):
        if not os.path.isfile(filename):
            raise PyRejeuException("Le fichier %s n'existe pas" % filename)
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.__import_beacons(lines)

            self.__import_flights(lines)
            for flight in self.session.query(mod.Flight).all():
                self.__import_plots(lines, flight)
                self.__import_flightplan(lines, flight)
        self.session.commit()

    def __line_search(self, lines, beginning_pattern, ending_pattern):
        """
        Extrait une liste de lignes comprises entre deux motifs (non inclus)
        a partir d'un fichier texte passe en parametre
        :param filename: fichier texte contenant les lignes a extraire
        :param beginning_pattern: motif indiquant le debut des lignes utiles
        :param ending_pattern: motif indiquant la fin des lignes utiles
        :return: list_lines: liste de chaine de caracteres correspondant
             aux lignes utiles (un element = une ligne)
        """
        for (i, line) in enumerate(lines):
            if beginning_pattern in line:
                start = i+1
            if ending_pattern in line:
                end = i
        return lines[start:end]

    def __import_beacons(self, lines):
        """
        Importe les donnees relative aux balise a partir d un fichier texte
        passe en entree et les stocke dans la BDD
        :param lines: fichier texte contenant les balises a importer
        :return: None
        """
        logging.debug("Importation des balises")
        l_beacons = self.__line_search(lines, "NBeacons:", "########## Layers")

        if l_beacons == []:
            print("Aucune balise dans le fichier")

        for beacon in l_beacons:
            # Attention: la position est une str ici, pas un entier
            (b_name, b_x_pos, b_y_pos) = beacon.split()[0:3]
            ### chercher du becon
            r_beacon = self.session.query(mod.Beacon)\
                                   .filter(mod.Beacon.name==b_name)\
                                   .first()
            if r_beacon is None:
                # Ajout de la balise a la bdd si elle n'y est pas deja
                r_beacon = mod.Beacon(name = b_name, 
                                      pos_x = int(b_x_pos), 
                                      pos_y = int(b_y_pos))
            else:
                # Cas ou une balise portant le meme nom est dans la bdd
                r_beacon.pos_x = b_x_pos
                r_beacon.pos_y = b_y_pos
            self.session.add(r_beacon)
        logging.debug("%d balises ont été importées" % len(l_beacons))

    def __import_flights(self, lines):
        """
        Importe les donnees relative aux vols a partir d un fichier texte passe
        en entree et les stocke dans la BDD
        :param lines: lignes du fichier contenant les vols a importer
        :return: None
        """
        logging.debug("Importation des vols")
        start = 0
        l_flights= []

        for (i, line) in enumerate(lines):
            if "NbVols:" in line:
                start = i
            if start > 0 and i>start and line[0]=='$':
                l_flights.append(line)

        # Remplissage des tables
        for flight in l_flights:
            (f_id, f_h_dep, f_h_arr, f_fl, f_speed, f_callsign, f_type, f_dep, f_arr) = flight.split()[1:10]
            # Conversions
            f_h_dep = utils.str_to_sec(f_h_dep)
            f_h_arr = utils.str_to_sec(f_h_arr)

            # Remplissage des tables avec les vols
            r_flight = self.session.query(mod.Flight)\
                                   .filter(mod.Flight.id==f_id).first()
            if r_flight is None:
                # Ajout du vol a la bdd si il n'y est pas deja
                r_flight = mod.Flight(id=int(f_id), h_dep=f_h_dep,
                                      h_arr=f_h_arr, fl=int(f_fl),
                                      v=int(f_speed), callsign=f_callsign,
                                      type=f_type, dep=f_dep, arr=f_arr, pln_event=0)
            else:
                # Cas ou un vol ayant le meme id est dans la bdd
                r_flight.h_dep = f_h_dep
                r_flight.h_arr = f_h_arr
                r_flight.v = int(f_speed)
                r_flight.fl = int(f_fl)
                r_flight.callsign = f_callsign
                r_flight.type = f_type
                r_flight.dep = f_dep
                r_flight.arr = f_arr
                r_flight.pln_event = 0
            self.session.add(r_flight)

        logging.debug("%d vols ont été importés" % len(l_flights))

    def __import_plots(self, lines, flight):
        """
        Importe les donnees des plots correspondant a un vol a partir du fichier apsse en parametre et les stock dans la bdd
        :param lines: lignes du fichier contenant les donnes
        :param flight: vol dont on veut recuperer les plots
        :return:
        """
        logging.debug("Importation des plots pour le vol %s" % flight.callsign)
        # Extraction des lignes concernant les plots du vol
        block_start, block_end, marker = 0, 0, 0
        for (i, line) in enumerate(lines):
            if line[0]=="$" and (str(flight.id) in line):
                marker = i
            if marker > 0 and i>marker and "NbPlots:" in line:
                block_start = i+1                                     #debut du bloc = ligne premier plot
                block_end = block_start + int(line.split()[1])        #fin du bloc = ligne du dernier plot + 1 (ATTENTION)
                break                                                 #On quitte une fois fini
        l_cones = lines[block_start:block_end]

        # Remplissage des tables
        for cone in l_cones:
            (c_hour, c_pos_x, c_pos_y, c_vit_x, c_vit_y, c_fl, c_rate, c_tendency) = cone.split()

            # Conversion
            c_hour = utils.str_to_sec(c_hour)

            # Ecriture dans un objet Cone
            tmp_cone = mod.Cone(pos_x=int(c_pos_x), pos_y=int(c_pos_y),
                                vit_x=int(c_vit_x), vit_y=int(c_vit_y),
                                flight_level=int(c_fl), rate=int(c_rate),
                                tendency= c_tendency, hour=c_hour, flight_id=flight.id)
            self.session.add(tmp_cone)

    def __import_flightplan(self, lines, flight):
        # Extraction de la ligne crrespondant au plan de vol
        logging.debug("Importation plan de vol pour le vol %s" % flight.callsign)
        marker = 0
        flightplan_str = ""
        for (i, line) in enumerate(lines):
            if line[0]=="$" and (str(flight.id) in line):
                marker = i
            if marker > 0 and i > marker and line[0] == '!':
                flightplan_str = line
                break        # On quitte une fois fini

        # Remplissable des tables
        if flightplan_str != "":
            tmp_tab = flightplan_str.split()
            datas = []
            index = 1
            if (len(tmp_tab)-1)%5 == 0:
                while index<len(tmp_tab):
                    (fp_beacon, V_or_A, fp_hour, dummy2, fp_fl) = tmp_tab[index:index+5]
                    datas.append((fp_beacon, V_or_A, fp_hour, dummy2, fp_fl))
                    index += 5

            flight_plan = mod.FlightPlan(flight_id=flight.id)
            for (i, data) in enumerate(datas):
                beacon = mod.FlightPlanBeacon(order=i+1,
                                              beacon_name=data[0],
                                              V_or_A=data[1],
                                              hour=utils.str_to_sec(data[2]),
                                              FL = data[4])
                flight_plan.beacons.append(beacon)
            self.session.add(flight_plan)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)-15s - %(levelname)s - %(message)s', level=logging.DEBUG)
    if len(sys.argv) != 2:
        sys.exit("Usage : importation.py <file>")

    import_obj = RejeuImportation()
    import_obj.import_file(sys.argv[1])

    # Test rapide sur la BDD importee
    print("------------ Test sur la base de données --------------")
    session_test = Session()
    print("Affichage d'une balise")
    print(session_test.query(mod.Beacon).first())
    print("Affichage des informations sur les vols")
    for flight in session_test.query(mod.Flight):
        print(flight)
        print(flight.display_cones_extract())
    print("Affichage des plans de vol")
    for fpl in session_test.query(mod.FlightPlan):
        print(fpl)

# -*- coding: utf-8 -*-
author = 'Alban', 'Alexandre', 'Audrey'

import sys
import os.path
import logging
from sqlalchemy.orm import sessionmaker
import models as mod
import utils
from __init__ import PyRejeuException
import connection

class RejeuImportation(object):

    def __init__(self, db_connection):
        self.session = db_connection.get_session()

    def import_file(self, filename):
        """
        Importe les balises, couches, vols, plots et plans de vols contenus dans le fichier texte passé en paramètre
        :param filename: nom du fichier contenant les informations de simulation
        :return: None
        """
        if not os.path.isfile(filename):
            raise PyRejeuException("Le fichier %s n'existe pas" % filename)
        with open(filename, 'r') as f:
            lines = f.readlines()
            self.__import_beacons(lines)
            self.__import_layer(lines)

            self.__import_flights(lines)
            for flight in self.session.query(mod.Flight).all():
                self.__import_plots(lines, flight)
                self.__import_flightplan(lines, flight)
        self.session.commit()
        self.session.close()

    def __line_search(self, lines, beginning_pattern, ending_pattern):
        """
        Extrait une sous-liste de lignes comprises entre deux motifs (non inclus) à partir d'une liste de lignes
        :param lines: liste des lignes à parser
        :param beginning_pattern: motif indiquant le debut des lignes utiles
        :param ending_pattern: motif indiquant la fin des lignes utiles
        :return: liste des lignes utiles
        """
        for (i, line) in enumerate(lines):
            if beginning_pattern in line:
                start = i+1
            if ending_pattern in line:
                end = i
        return lines[start:end]

    def __import_beacons(self, lines):
        """
        Importe les données relatives aux balises a partir d'une liste de lignes en entrée et les stocke dans la BDD
        :param lines: liste des lignes contenant les balises a importer
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
                                      pos_x = int(b_x_pos)/8.0,
                                      pos_y = int(b_y_pos)/8.0)
            else:
                # Cas ou une balise portant le meme nom est dans la bdd
                r_beacon.pos_x = int(b_x_pos)/8.0
                r_beacon.pos_y = int(b_y_pos)/8.0
            self.session.add(r_beacon)
        logging.debug("%d balises ont été importées" % len(l_beacons))

    def __import_flights(self, lines):
        """
        Importe les données relatives aux vols à partir d'une liste de lignes en entrée et les stocke dans la BDD
        :param lines: liste des lignes contenant les vols à importer
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
            tmp_list = flight.split()
            (f_id, f_h_dep, f_h_arr, f_fl, f_speed, f_callsign, f_type, f_dep, f_arr, f_ssr, f_rvsm, f_tcas, f_adsb) = tmp_list[1:14]
            if len(tmp_list)==15: f_dlink = tmp_list[-1]
            else: f_dlink = ""

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
                                      type=f_type, dep=f_dep, arr=f_arr,
									  ssr = int(f_ssr), rvsm=f_rvsm, tcas=f_tcas, adsb=f_adsb, dlink=f_dlink,
									  last_version=1)
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
                r_flight.ssr = int(f_ssr)
                r_flight.rvsm = f_rvsm
                r_flight.tcas = f_tcas
                r_flight.adsb = f_adsb
                r_flight.dlink = f_dlink
                r_flight.last_version = 1
            self.session.add(r_flight)

        logging.debug("%d vols ont été importés" % len(l_flights))

    def __import_plots(self, lines, flight):
        """
        Importe les plots relatifs à un vol à partir d'une liste de lignes en entrée et les stocke dans la BDD
        :param lines: liste des lignes contenant les plots à importer
        :param flight: vol dont on veut importer les plots
        :return: None
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
                                tendency= c_tendency, hour=c_hour, flight_id=flight.id, version=1)
            self.session.add(tmp_cone)

    def __import_flightplan(self, lines, flight):
        """
        Importe le plan de vol relatif à un vol à partir d'une liste de lignes en entrée et les stocke dans la BDD
        :param lines: liste des lignes contenant le plan de vol à importer
        :param flight: vol concerné
        :return: None
        """
        # Extraction de la ligne correspondant au plan de vol
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

    def __import_layer(self, lines):
        """
        Importe les couches à partir d'une liste de lignes en entrée et les stocke dans la BDD
        :param lines: liste des lignes contenant les couches à importer
        :return: None
        """
        logging.debug("Importation des couches")

        block_start, block_end = 0, 0
        for (i, line) in enumerate(lines):
            if "NLayers:" in line:
                block_start = i+1                                     #début du bloc = ligne première couche
                block_end = block_start + int(line.split()[1])        #fin du bloc = ligne du dernier plot + 1 (ATTENTION)
                break                                                 #On quitte une fois fini
        l_layers = lines[block_start:block_end]

        # Remplissage des tables
        for layer in l_layers:
            (l_name, l_floor, l_ceiling, l_climb_delay_first, l_climb_delay_others,
             l_descent_delay, l_descent_distance) = layer.split()

            r_layer = self.session.query(mod.Layer) \
                .filter(mod.Layer.name == l_name) \
                .first()

            if r_layer is None:
                 # Ajout de la balise a la bdd si elle n'y est pas deja
                 r_layer = mod.Layer(name = l_name,
                                     floor = int(l_floor),
                                     ceiling = int(l_ceiling),
                                     climb_delay_first = int(l_climb_delay_first),
                                     climb_delay_others = int(l_climb_delay_others),
                                     descent_delay = int(l_descent_delay),
                                     descent_distance = float(l_descent_distance))

            else:
                 # Cas ou une balise portant le meme nom est dans la bdd
                 r_layer.floor = l_floor,
                 r_layer.ceiling = l_ceiling,
                 r_layer.climb_delay_first = l_climb_delay_first,
                 r_layer.climb_delay_others = l_climb_delay_others,
                 r_layer.descent_delay = l_descent_delay,
                 r_layer.descent_distance = l_descent_distance

            self.session.add(r_layer)

        logging.debug("%d couches ont été importées" % len(l_layers))



if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)-15s - %(levelname)s - %(message)s', level=logging.DEBUG)
    if len(sys.argv) != 2:
        sys.exit("Usage : importation.py <file>")
    db_file = "/tmp/importations.db"
    db_connection = connection.DatabaseConnection(file_path=db_file)
    import_obj = RejeuImportation(db_connection)
    import_obj.import_file(sys.argv[1])

    # Test rapide sur la BDD importee
    print("------------ Test sur la base de données --------------")
    session_test = import_obj.session
    print("Affichage d'une balise")
    print(session_test.query(mod.Beacon).first())
    print("Affichage des informations sur les vols")
    for flight in session_test.query(mod.Flight):
        print(flight)
        print(flight.display_cones_extract())
    print("Affichage des plans de vol")
    for fpl in session_test.query(mod.FlightPlan):
        print(fpl)
    print("Affichage des couches")
    imported_layers = session_test.query(mod.Layer)
    for layer in imported_layers:
        print(layer)
    print("Test couche")
    print("Layer pour FL=100 est : %s." % utils.layer_s_name_from_FL(imported_layers , 100) )


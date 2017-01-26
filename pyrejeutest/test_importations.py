# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre", "Audrey"

import sys
sys.path.append('/home/eleve/Documents/RejeuTraffic')       #Correction de l'erreur d'importation du module pyrejeu

import unittest
import os
from pyrejeu import importations
from pyrejeu import models as mod
from pyrejeu import connection

#Initialisation de la base de données et importation des infos du fichier testfile

testfile="/home/eleve/Documents/RejeuTraffic/pyrejeutest/test_file.txt"
db_file = "/tmp/unittest_importations.db"
if os.path.isfile(db_file):
    os.unlink(db_file)
db_connection = connection.DatabaseConnection(file_path=db_file)
import_obj = importations.RejeuImportation(db_connection)
import_obj.import_file(testfile)

class ImportationsTest(unittest.TestCase):
    """Test case utilisé pour tester les fonction du module 'importations' et la cohérence de la base de données."""
    def setUp(self):
        """Initialisation des tests."""
        self.session = db_connection.get_session()
        self.beacons = self.session.query(mod.Beacon).all()
        self.flights = self.session.query(mod.Flight).all()
        self.all_cones = self.session.query(mod.Cone).all()

    def tearDown(self):
        """Terminaison des tests"""
        pass

    #**     Tests sur les balises       **#

    def test_number_of_beacons(self):
        no_beacons = len(self.beacons)
        self.assertEqual(no_beacons, 8)

    def test_beacon_names(self):
        beacon_names = [beacon.name for beacon in self.beacons]
        expected_list = ['MAKOX', 'TW', 'LFCR', 'GAI', 'LASBO', 'AGN', 'TOU', 'LFBO']
        self.assertListEqual(beacon_names, expected_list)

    def test_types_of_beacons_attributes(self):
        for beacon in self.beacons:
            self.assertIsInstance(beacon.id, int)
            self.assertIsInstance(beacon.name, basestring)
            self.assertIsInstance(beacon.pos_x, float)
            self.assertIsInstance(beacon.pos_y, float)

    # **     Tests sur les vols       **#

    def test_number_of_flights(self):
        no_flights = len(self.flights)
        self.assertEqual(no_flights, 2)

    def test_flight_ids(self):
        flight_ids = [flight.id for flight in self.flights]
        expected_list = [10001, 10002]
        self.assertListEqual(flight_ids, expected_list)

    def test_types_of_flight_attributes(self):
        for flight in self.flights:
            self.assertIsInstance(flight.id, int)
            self.assertIsInstance(flight.h_dep, int)
            self.assertIsInstance(flight.h_arr, int)
            self.assertIsInstance(flight.fl, int)
            self.assertIsInstance(flight.v, int)
            self.assertIsInstance(flight.callsign, basestring)
            self.assertIsInstance(flight.type, basestring)
            self.assertIsInstance(flight.dep, basestring)
            self.assertIsInstance(flight.arr, basestring)
            self.assertIsInstance(flight.ssr, int)
            self.assertIsInstance(flight.rvsm, basestring)
            self.assertIsInstance(flight.tcas, basestring)
            self.assertIsInstance(flight.adsb, basestring)
            self.assertIsInstance(flight.dlink, basestring)
            self.assertIsInstance(flight.last_version, int)
            self.assertIsInstance(flight.flight_plan, mod.FlightPlan)
            for cone in flight.cones:
                self.assertIsInstance(cone, mod.Cone)

    def test_flight_hours(self):
        for flight in self.flights:
            # Les heures de départ et d'arrivée sont entre 00:00:00 et 23:59:59
            self.assertIn(flight.h_dep, range(0,3600*24-1))
            self.assertIn(flight.h_arr, range(0,3600*24-1))
            # L'heure de départ est avant l'heure d'arrivée
            self.assertLess(flight.h_dep, flight.h_arr, "Heure de départ avant heure d'arrivée, vol %d" % flight.id)

    def test_number_of_related_cones(self):
        for flight in self.flights:
            no_associated_cones = self.session.query(mod.Cone).filter(mod.Cone.flight == flight).count()
            if flight.id == 10001:
                self.assertEqual(no_associated_cones, 203)
            else:
                self.assertEqual(no_associated_cones, 146)

    #**     Tests sur les plots       **#

    def test_number_of_cones(self):
        no_cones = len(self.all_cones)
        self.assertEqual(no_cones, 349)

    def test_type_of_cone_attributes(self):
        for cone in self.all_cones:
            #Test sur le type des paramètres
            self.assertIsInstance(cone.id, int)
            self.assertIsInstance(cone.pos_x, float)
            self.assertIsInstance(cone.pos_y, float)
            self.assertIsInstance(cone.vit_x, int)
            self.assertIsInstance(cone.vit_y, int)
            self.assertIsInstance(cone.flight_level, int)
            self.assertIsInstance(cone.rate, int)
            self.assertIsInstance(cone.tendency, int)
            self.assertIsInstance(cone.hour, int)
            self.assertIsInstance(cone.flight_id, int)
            self.assertIsInstance(cone.version, int)
            self.assertIsInstance(cone.flight, mod.Flight)

    def test_cones_hour(self):
        for cone in self.all_cones:
            # L'heure du plot est entre 00:00:00 et 23:59:59
            self.assertIn(cone.hour, range(0,3600*24-1))

    def test_cones_tendency_and_rate(self):
        for cone in self.all_cones:
            # Tendance = montée, palier ou descente
            self.assertIn(cone.tendency, [-1, 0, 1])
            # La tendance est cohérente avec le taux de montée
            if cone.rate > 0:
                self.assertEqual(cone.tendency, 1)
            elif cone.rate < 0:
                self.assertEqual(cone.tendency, -1)
            else:
                self.assertEqual(cone.tendency, 0)

    def test_all_cones_are_linked_to_flights(self):
        for cone in self.all_cones:
            self.assertIn(cone.flight, self.flights)

    def test_relationship_cone_flight_consistency(self):
        for flight in self.flights:
            # Heures de départ et d'arrivée du vol sont celles du premier et dernier plot
            self.assertEqual(flight.h_dep, flight.cones[0].hour)
            self.assertEqual(flight.h_arr, flight.cones[-1].hour)


if __name__ == '__main__':
    unittest.main()
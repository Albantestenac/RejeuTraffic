# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre", "Audrey"

import sys
sys.path.append('/home/eleve/Documents/RejeuTraffic')       #Correction de l'erreur d'importation du module pyrejeu

import unittest
from pyrejeu import utils
from pyrejeu import models

class UtilsTest(unittest.TestCase):
    """Test case utilisé pour tester les fonction du module 'utils'."""

    def setUp(self):
        """Initialisation des tests."""
        self.hour_str = "12:54:27"
        self.hour_sec = 12*3600+54*60+27
        self.hour_hh_mm = "12:54"
        self.sim_start = 36458
        self.sim_end = 45036
        self.flight_list = [models.Flight(h_dep=self.sim_start, h_arr=self.sim_start+400), models.Flight(h_dep=self.sim_start+600, h_arr=self.sim_end)]

    def test_str_to_sec(self):
        """Teste le fonctionnement de la fonction de conversion 'HH:MM:SS' -> secondes."""
        value = utils.str_to_sec(self.hour_str)
        self.assertEqual(value, self.hour_sec)

    def test_sec_to_str(self):
        """Teste le fonctionnement de la fonction de conversion secondes -> 'HH:MM:SS'."""
        string = utils.sec_to_str(self.hour_sec)
        self.assertEqual(string, self.hour_str)

    def test_sec_to_str_without_sec(self):
        """Teste le fonctionnement de la fonction de conversion secondes -> 'HH:MM'."""
        string = utils.sec_to_str_without_sec(self.hour_sec)
        self.assertEqual(string, self.hour_hh_mm)

    def test_extract_sim_bounds(self):
        """Teste le fonctionnement de la fonction d'extraction des bornes horaires de la simulation."""
        (start, end) = utils.extract_sim_bounds(self.flight_list)
        self.assertEqual(start, self.sim_start)
        self.assertEqual(end, self.sim_end)

if __name__ == '__main__':
    unittest.main()
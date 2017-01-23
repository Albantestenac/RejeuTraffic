# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre", "Audrey"

import sys
sys.path.append('/home/eleve/Documents/RejeuTraffic')       #Correction de l'erreur d'importation du module pyrejeu

import unittest
from pyrejeu import importations
from pyrejeu import models

class UtilsTest(unittest.TestCase):
    """Test case utilisé pour tester les fonction du module 'importations' et la cohérence de la base de données."""

    def setUp(self):
        """Initialisation des tests."""
        self.file="/home/eleve/Documents/RejeuTraffic/pyrejeutest/test_file.txt"


if __name__ == '__main__':
    unittest.main()
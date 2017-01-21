# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre", "Audrey"

import unittest
from pyrejeu import utils

class UtilsTest(unittest.TestCase):
    """Test case utilisé pour tester les fonction du module 'utils'."""

    def setUp(self):
        """Initialisation des tests."""
        self.hour_str = "12:54:27"
        self.hour_sec = 12*3600+54*60+27

    def test_str_to_sec(self):
        """Teste le fonctionnement de la fonction str_to_sec."""
        value = utils.str_to_sec(self.hour_str)
        self.assertEqual(value, self.hour_sec)

    def test_sec_to_str(self):
        """Teste le fonctionnement de la fonction sec_to_str"""
        string = utils.sec_to_str(self.hour_sec)
        self.assertEqual(string, self.hour_str)

if __name__ == '__main__':
    unittest.main()
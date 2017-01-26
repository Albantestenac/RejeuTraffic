# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre", "Audrey"

import sys
sys.path.append('/home/eleve/Documents/RejeuTraffic')       #Correction de l'erreur d'importation du module pyrejeu

import unittest
from pyrejeu import clock
from pyrejeu import connection as db_connection

class ClockTest(unittest.TestCase):
    """Test case utilisé pour tester les fonction du module 'clock'"""

    def __init__(self, db_connection, start_time=0):
        self.running = True
        self.paused = True
        self.current_time = start_time
        self.db_con = db_connection
        self.session = db_connection.get_session()
        # abonnement aux messages relatifs à l'horloge
        self.__set_subscriptions()
        self.myClock = clock.RejeuClock(db_connection, ut.str_to_sec("11:24:00"))

    def setUp(self):
        pass

    def test_set_rate_positif(self):
        self.myClock.rate = 1
        self.myClock.set_rate(9)
        self.assertEqual(self.myClock.rate, 9)

    def test_set_rate_negatif(self):
        self.myClock.rate = 1
        self.myClock.set_rate(-2)
        self.assertEqual(self.myClock.rate, -2)

    def test_set_rate_nul(self):
        self.myClock.paused = False
        self.myClock.set_rate(0)
        self.assertEqual(self.myClock.rate, 0)
        self.assertTrue(self.myClock.paused)

    def test_start(self):
        self.myClock.paused = True
        self.myClock.start()
        self.assertFalse(self.myClock.paused)

    def test_stop(self):
        self.myClock.paused = False
        self.myClock.stop()
        self.assertTrue(self.myClock.paused)

    def test_close(self):
        self.myClock.running = True
        self.myClock.close()
        self.assertEqual(self.myClock.running, False)

    def test_restart_with_rate(self):
        self.myClock.paused = True
        self.myClock.set_rate(2)
        self.assertFalse(self.myClock.paused)

    def test_send_init_time(self):
        self.current_time = 12*3600
        self.myClock.set_init_time("14:32:25")
        self.assertEqual(self.myClock.current_time, 14*3600+32*60+25)


if __name__ == '__main__':
    unittest.main()





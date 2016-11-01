author="Alban"

import random
import unittest

class RandomTest(unittest.TestCase):
    """Testcase utilise pour tester les fonctions du module random"""

    def test_choice(self):
        liste = list(range(10))
        elt = random.choice(liste)
        #Verifie que 'elt' est dans 'liste'
        self.assertIn(elt, liste)

unittest.main()


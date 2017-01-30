# -*- coding: utf-8 -*-

import os
from pyrejeutest import test_importations
from pyrejeutest import test_utils

if __name__ == "__main__":
    x = 0
    while x!=4 :
        #Demander à l'utilisateur ce qu'il souhaite faire
        print("\n Welcome in rejeu_test. What do you want to do ? \n [1] test importations.py \n [2] test utils.py \n [3] test everything \n [4] exit rejeu_test \n")
        #Prendre en compte le choix de l'utilisateur
        x=input()

        if x==1 :
            os.system("python ./pyrejeutest/test_importations.py")
        elif x==2 :
            os.system("python ./pyrejeutest/test_utils.py")
        elif x==3 :
            os.system("python ./pyrejeutest/test_importations.py")
            os.system("python ./pyrejeutest/test_utils.py")
        elif x==4 :
            print("Exiting test... Good bye !")
        else :
            print("\n Please choose a number between 1 and for")






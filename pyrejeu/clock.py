# -*- coding: utf-8 -*-
Author = "Alban", "Audrey"

import ivy.std_api as ivy
import time
import logging
import pyrejeu.models as mod
import utils
import math


class RejeuClock(object):

    def __init__(self):
        self.running = True
        self.current_time = 0

    def run(self):
        while self.running:
            time.sleep(1)
            logging.debug("Loop running")

            # récupérer les plots à envoyer

            list_cones = self.session.querry(mod.Cone) \
                .filter(mod.Cone.name == self.current_time)
            print(list_cones)

            # pour chaque plot
            #ivy.IvySendMsg("")

            for cone in list_cones:
                # par défaut : SSR = 0000 ...
                msg = "TrackMovedEvent Flight=%d CallSign=%d SSR=0000 Sector=SL Layers=F,I X=%f Y=%f Vx=%d Vy=%d Afl=%d Rate=%f Heading=323 GroundSpeed=%f Tendency=%d Time=%d" % \
                      ( cone.flight, cone.flight.callsign, cone.pos_x, cone.pos_y, cone.vit_x, cone.vit_y, cone.fl, cone.rate, math.rac((cone.vit_x)**2+(cone.vit_y)**2) , cone.tendency, utils.sec_to_str(cone.hour) )
                ivy.IvySendMsg(msg)

            self.current_time += 1

    def pause(self):
        pass

    def stop(self):
        self.running = False


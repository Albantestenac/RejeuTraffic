# -*- coding: utf-8 -*-
Author = "Alban", "Audrey", "Alexandre"

import ivy.std_api as ivy
import time
import logging
import pyrejeu.models as mod
import utils
import math
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(mod.engine)

class RejeuClock(object):

    def __init__(self, start_time=0):
        self.running = True
        self.current_time = start_time
        self.session = Session()

    def run(self):
        while self.running:
            logging.debug("Loop running, SimTime=%s" \
                    % utils.sec_to_str(self.current_time))
            ivy.IvySendMsg("ClockEvent Time=%s Rate=1 Bs=0" \
                    % utils.sec_to_str(self.current_time))

            # récupérer les plots à envoyer

            list_cones = self.session.query(mod.Cone) \
                .filter(mod.Cone.hour == self.current_time)

            # pour chaque plot
            for cone in list_cones:
                # par défaut : SSR = 0000 ...
                if cone.flight.pln_event == 0 :
                    # ATTENTION A MODIFIER POUR LIST (cf focntion "listing" de la classe FlightPlan de models.py)
                    msg_pln_event = "PlnEvent Flight=%d Time=%s CallSign=%s AircraftType=%s Ssr=0000 Speed=%d Rfl=%d Dep=%s Arr=%s Rvsm=TRUE Tcas=TA_ONLY Adsb=NO DLink=NO List=--" %\
                                    (cone.flight.id, cone.hour, cone.flight.callsign, cone.flight.type, cone.flight.v, cone.flight.fl,cone.flight.dep, cone.flight.arr)
                    ivy.IvySendMsg(msg_pln_event)
                    cone.flight.pln_event=1
                g_speed = math.sqrt((cone.vit_x)**2+(cone.vit_y)**2)
                msg = "TrackMovedEvent Flight=%d CallSign=%s Ssr=0000 Sector=SL Layers=F,I X=%f Y=%f Vx=%f Vy=%f Afl=%d Rate=%f Heading=323 GroundSpeed=%f Tendency=%d Time=%s" %\
                      ( cone.flight.id, cone.flight.callsign, cone.pos_x, cone.pos_y, cone.vit_x, cone.vit_y, cone.flight_level, cone.rate, g_speed, cone.tendency, utils.sec_to_str(cone.hour) )
                #logging.debug("Message envoye : %s" % msg)
                ivy.IvySendMsg(msg)

            self.current_time += 1
            time.sleep(1)

    def pause(self):
        pass

    def stop(self):
        self.running = False
        self.session.commit()

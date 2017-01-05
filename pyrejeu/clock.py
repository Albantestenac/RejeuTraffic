# -*- coding: utf-8 -*-
__author__ = "Alban", "Audrey", "Alexandre"

from ivy.std_api import IvyBindMsg
from ivy.std_api import IvySendMsg
import time
import logging
import pyrejeu.models as mod
import utils
import math
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=mod.engine)

class RejeuClock(object):

    def __init__(self, start_time=0):
        self.running = True
        self.paused = True
        self.current_time = start_time
        self.rate = 1.0
        self.session = Session()
        # abonnement aux messages relatifs à l'horloge
        self.__set_subscriptions()

    def __set_subscriptions(self):
        IvyBindMsg(lambda *l: self.start(), '^ClockStart')
        IvyBindMsg(lambda *l: self.stop(), '^ClockStop')

    def main_loop(self):

        # Envoi des infos de début et de fin de la simulation
        list_flights = self.session.query(mod.Flight)
        (start_time, stop_time) = utils.extract_sim_bounds(list_flights)

        msg_rangeupdate = "RangeUpdateEvent FirstTime=%s LastTime=%s" % (
            utils.sec_to_str(start_time), utils.sec_to_str(stop_time))
        time.sleep(0.5)
        logging.debug(msg_rangeupdate)
        IvySendMsg(msg_rangeupdate)

        #Boucle d'horloge
        while self.running:
            if self.paused:
                # en pause, on ne doit plus faire avancer l'horloge
                # et émettre les messages
                time.sleep(0.1)
                continue

            logging.debug("Loop running, SimTime=%s" \
                    % utils.sec_to_str(self.current_time))
            IvySendMsg("ClockEvent Time=%s Rate=1 Bs=0" \
                    % utils.sec_to_str(self.current_time))

            # récupérer les plots à envoyer
            list_cones = self.session.query(mod.Cone) \
                                     .filter(mod.Cone.hour == self.current_time)

            # pour chaque plot
            for cone in list_cones:
                # par défaut : SSR = 0000 ...
                if cone.flight.pln_event == 0 :
                    # ATTENTION A MODIFIER POUR LIST (cf focntion "listing" de la classe FlightPlan de models.py)
                    msg_pln_event = "PlnEvent Flight=%d Time=%s CallSign=%s AircraftType=%s Ssr=0000 Speed=%d Rfl=%d Dep=%s Arr=%s Rvsm=TRUE Tcas=TA_ONLY Adsb=NO DLink=NO List=%s" %\
                                    (cone.flight.id, cone.hour, cone.flight.callsign, cone.flight.type, cone.flight.v, cone.flight.fl,cone.flight.dep, cone.flight.arr, cone.flight.flight_plan.listing())
                    IvySendMsg(msg_pln_event)
                    cone.flight.pln_event=1
                g_speed = math.sqrt((cone.vit_x)**2+(cone.vit_y)**2)
                msg = "TrackMovedEvent Flight=%d CallSign=%s Ssr=0000 Sector=SL Layers=F,I X=%f Y=%f Vx=%f Vy=%f Afl=%d Rate=%f Heading=323 GroundSpeed=%f Tendency=%d Time=%s" %\
                      ( cone.flight.id, cone.flight.callsign, cone.pos_x, cone.pos_y, cone.vit_x, cone.vit_y, cone.flight_level, cone.rate, g_speed, cone.tendency, utils.sec_to_str(cone.hour) )
                #logging.debug("Message envoye : %s" % msg)
                IvySendMsg(msg)

            self.current_time += 1
            time.sleep(1.0/self.rate)

    def stop(self):
        logging.debug("Clock Stopped")
        self.paused = True

    def start(self):
        logging.debug("Clock Started")
        self.paused = False

    def close(self):
        self.running = False

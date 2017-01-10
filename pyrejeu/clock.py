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
        IvyBindMsg(lambda *l: self.modify_rate(l[1]), '^SetClock Rate=(\S+)')
        IvyBindMsg(lambda *l: self.modify_init_time(l[1]), '^SetClock Time=(\S+)')
        IvyBindMsg(lambda *l: self.send_beacons(l[1]), "^GetAllBeacons MsgName=(\S+)")
        IvyBindMsg(lambda *l: self.send_pln(l[1], int(l[2]), l[3])), "^GetPln MsgName=(\S+) Flight=(\S+) From=(\S+)"


    def main_loop(self):
        # Envoi des infos de début et de fin de la simulation
        list_flights = self.session.query(mod.Flight)
        (start_time, stop_time) = utils.extract_sim_bounds(list_flights)

        msg_rangeupdate = "RangeUpdateEvent FirstTime=%s LastTime=%s" % (
            utils.sec_to_str(start_time), utils.sec_to_str(stop_time))
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
            IvySendMsg("ClockEvent Time=%s Rate=%d Bs=0" \
                    % (utils.sec_to_str(self.current_time), self.rate))

            # récupérer les plots à envoyer
            list_cones = self.session.query(mod.Cone) \
                                     .filter(mod.Cone.hour == self.current_time)

            # pour chaque plot
            for cone in list_cones:
                # par défaut : SSR = 0000 ...
                if cone.flight.pln_event == 0 :
                    # ATTENTION A MODIFIER POUR LIST (cf focntion "listing" de la classe FlightPlan de models.py)
                    msg_pln_event = "PlnEvent Flight=%d Time=%s CallSign=%s AircraftType=%s Ssr=%d Speed=%d Rfl=%d Dep=%s Arr=%s Rvsm=%s Tcas=%s Adsb=%s DLink=%s List=%s" %\
                                    (cone.flight.id, utils.sec_to_str(cone.hour), cone.flight.callsign, cone.flight.type, cone.flight.ssr, cone.flight.v, cone.flight.fl, cone.flight.dep,
                                     cone.flight.arr, cone.flight.rvsm, cone.flight.tcas, cone.flight.adsb, cone.flight.dlink, cone.flight.flight_plan.listing())
                    IvySendMsg(msg_pln_event)
                    cone.flight.pln_event=1
                g_speed = math.sqrt((cone.vit_x)**2+(cone.vit_y)**2)
                msg = "TrackMovedEvent Flight=%d CallSign=%s Ssr=%d Sector=-- Layers=F X=%f Y=%f Vx=%d Vy=%d Afl=%d Rate=%d Heading=323 GroundSpeed=%d Tendency=%d Time=%s" %\
                      ( cone.flight.id, cone.flight.callsign, cone.flight.ssr, cone.pos_x/60, cone.pos_y/60, cone.vit_x, cone.vit_y, cone.flight_level, cone.rate, int(g_speed), cone.tendency, utils.sec_to_str(cone.hour) )
                #logging.debug("Message envoye : %s" % msg)
                IvySendMsg(msg)

            if self.rate>0 :
                self.current_time += 1
                time.sleep(1.0 / self.rate)
            else :
                self.current_time -=1
                time.sleep(-1.0 / self.rate)


    def stop(self):
        logging.debug("Clock Stopped")
        self.paused = True

    def start(self):
        logging.debug("Clock Started")
        self.paused = False

    def close(self):
        self.running = False

    def modify_rate(self, rate_value):
        logging.debug("SetClock")
        self.rate = int(rate_value)

    def modify_init_time(self, init_time):
        logging.debug("Set Init Time")
        self.current_time = utils.str_to_sec(init_time)

    def send_beacons(self, msg_name):
        l_beacons = self.session.query(mod.Beacon)
        count = 0
        msg = "AllBeacons %s Slice=" % (msg_name)
        for beacon in l_beacons:
            msg += beacon.display_beacon() + " "
            count += 1
            if count == 50:
                IvySendMsg(msg.strip())
                count = 0
                msg = "AllBeacons %s Slice=" % (msg_name)
        if count > 0:
            IvySendMsg(msg)
        IvySendMsg("AllBeacons %s EndSlice" % msg_name)

    def send_pln(self, msg_name, flight_id, init_beacon):
        if init_beacon == "now":
            pass

        msg_pln_event = "PlnEvent Flight=%d Time=%s CallSign=%s AircraftType=%s Ssr=%d Speed=%d Rfl=%d Dep=%s Arr=%s Rvsm=%s Tcas=%s Adsb=%s DLink=%s List=%s" % \
                        (flight.id, utils.sec_to_str(self.current_time), flight.callsign, flight.type, flight.ssr, flight.v, flight.fl, flight.dep, flight.arr,
                         flight.rvsm, flight.tcas, flight.adsb, flight.dlink, flight.flight_plan.listing())
        IvySendMsg(msg_pln_event)




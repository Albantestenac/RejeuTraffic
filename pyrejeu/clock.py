# -*- coding: utf-8 -*-
"""
Module composé d'une unique classe RejeuClock gérant la simulation, l'horloge et les messages émis/reçu sur le bus.
"""
__author__ = "Alban", "Audrey", "Alexandre"

from ivy.std_api import IvyBindMsg
from ivy.std_api import IvySendMsg
import time
import logging
import models as mod
import utils
import math
import control
import re

class RejeuClock(object):

    def __init__(self, db_connection, start_time=0):
        """
        Initialisation d'un objet RejeuClock

        :param db_connection: Connexion à la base de données

        :param start_time: Heure de départ à 0 secondes par défaut
        """
        self.running = True
        self.paused = True
        self.current_time = start_time
        self.rate = 1.0
        self.db_con = db_connection
        self.session = db_connection.get_session()
        # abonnement aux messages relatifs à l'horloge
        self.__set_subscriptions()

    def __set_subscriptions(self):
        """
        Abonnements aux messages du bus Ivy afin de traiter les différentes actions de l'utilisateur

        :return: NONE
        """
        IvyBindMsg(lambda *l: self.start(), '^ClockStart')
        IvyBindMsg(lambda *l: self.stop(), '^ClockStop')
        IvyBindMsg(lambda *l: self.set_rate(l[1]), '^SetClock Rate=(\S+)')
        IvyBindMsg(lambda *l: self.set_init_time(l[1]), '^SetClock Time=(\S+)')
        IvyBindMsg(lambda *l: self.send_beacons(l[1]), "^GetAllBeacons MsgName=(\S+)")
        IvyBindMsg(lambda *l: self.send_pln(l[1], int(l[2]), l[3]), "^GetPln MsgName=(\S+) Flight=(\S+) From=(\S+)")
        IvyBindMsg(lambda *l: self.send_sectors_info(l[1], int(l[2])), "^GetSectorsInfos MsgName=(\S+) Flight=(\S+)")
        IvyBindMsg(lambda *l: self.set_heading(l[0], int(l[1]), int(l[2])), '^AircraftHeading Flight=(\S+) To=(\S+)')
        IvyBindMsg(lambda *l: self.set_heading(l[0], int(l[1]), int(l[2]), side=l[3]), '^AircraftHeading Flight=(\S+) To=(\S+) By=(\S+)')
        IvyBindMsg(lambda *l: self.set_heading(l[0], int(l[1]), int(l[2]), rate=int(l[3])), '^AircraftHeading Flight=(\S+) To=(\S+) Rate=(\S+)')
        IvyBindMsg(lambda *l: self.set_heading(l[0], int(l[1]), int(l[2]), side=l[3], rate=int(l[4])), '^AircraftHeading Flight=(\S+) To=(\S+) By=(\S+) Rate=(\S+)')
        IvyBindMsg(lambda *l: self.reset_heading(int(l[1])), '^CancelLastOrder Flight=(\S+)')
        IvyBindMsg(lambda *l: self.send_trajectory(l[1], l[2], l[3]), 'GetTrajectory MsgName=(\S+) Flight=(\S+) From=(\S+)')

    def main_loop(self):
        """
        Boucle principale permettant l'utilisation de l'objet RejeuClock

        :return: NONE
        """
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
            list_cones = self.session.query(mod.Cone)\
                                     .join(mod.Cone.flight)\
                                     .filter(mod.Cone.hour == self.current_time,
                                             mod.Cone.version == mod.Flight.last_version)


            # pour chaque plot
            for cone in list_cones:
                g_speed = math.sqrt((cone.vit_x)**2+(cone.vit_y)**2)
                heading = utils.get_heading(cone.vit_x, cone.vit_y)
                msg = "TrackMovedEvent Flight=%d CallSign=%s Ssr=%d Sector=-- Layers=F X=%f Y=%f Vx=%d Vy=%d Afl=%d Rate=%d Heading=%d GroundSpeed=%d Tendency=%d Time=%s" %\
                      ( cone.flight.id, cone.flight.callsign, cone.flight.ssr, cone.pos_x/64, cone.pos_y/64, cone.vit_x, cone.vit_y, cone.flight_level, cone.rate, heading,int(g_speed), cone.tendency, utils.sec_to_str(cone.hour) )
                #logging.debug("Message envoye : %s" % msg)
                IvySendMsg(msg)

            IvySendMsg("EndTransmissionEvent Time=%s" % (utils.sec_to_str(self.current_time)))

            if self.rate>0 :
                self.current_time += 1
                time.sleep(1.0 / self.rate)
            else :
                self.current_time -=1
                time.sleep(-1.0 / self.rate)
        self.session.close()

    def stop(self):
        """
        Met en pause l'horloge et donc la simulation

        :return: NONE
        """
        logging.debug("Clock Stopped")
        self.paused = True

    def start(self):
        """
        Lance la simulation en lançant l'horloge

        :return: NONE
        """
        logging.debug("Clock Started")
        self.paused = False

    def close(self):
        """
        Arrête l'horloge et ferme le programme

        :return: NONE
        """
        self.running = False

    def set_rate(self, rate_value):
        """
        Modifie la vitesse de la simulation

        :param rate_value: Vitesse (Float)

        :return: NONE
        """
        logging.debug("SetClock")
        self.rate = int(rate_value)

    def set_init_time(self, init_time):
        """
        Modifie l'heure à laquelle on effectue la simulation

        :param init_time: Heure d'initialisation

        :return: NONE
        """
        logging.debug("Set Init Time")
        self.current_time = utils.str_to_sec(init_time)

    def send_beacons(self, msg_name):
        """
        En réponse à GetAllBeacons, Rejeu envoie l'ensemble des balises enregistrées.

        :param msg_name: Identifiant du msg envoyé et émit en réponse

        :return: NONE
        """
        session = self.db_con.get_session()
        l_beacons = session.query(mod.Beacon)
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
        session.close()

    def send_pln(self, msg_name, flight_id, init_order):
        """
        En réponse à GetPln, Rejeu renvoie le plan de vol associé au vol dans le message.

        :param msg_name: Identifiant du message envoyé et émis en réponse

        :param flight_id: Num de vol (Int)

        :param init_order: now, un nom de balise ou une heure (Str)

        :return: NONE
        """
        session = self.db_con.get_session()
        flight = session.query(mod.Flight).filter(mod.Flight.id == flight_id).first()
        if init_order == "now":
            starting_time = self.current_time
            starting_beacon = None
        elif init_order == "origin":
            starting_beacon = None
            starting_time = None
        elif len(init_order.split(':'))>1:
            starting_beacon = None
            starting_time = utils.str_to_sec(init_order)
        else :
            starting_beacon = init_order
            starting_time = None
        route = utils.extract_route(flight.flight_plan, starting_beacon, starting_time)
        msg_pln = "Pln %s Flight=%d Time=%s CallSign=%s AircraftType=%s Ssr=%d Speed=%d Rfl=%d Dep=%s Arr=%s Rvsm=%s Tcas=%s Adsb=%s DLink=%s List=%s" % \
                        (msg_name, flight.id, utils.sec_to_str(self.current_time), flight.callsign, flight.type, flight.ssr, flight.v, flight.fl, flight.dep, flight.arr,
                         flight.rvsm, flight.tcas, flight.adsb, flight.dlink, route.strip())
        flight.pln_event = 1
        IvySendMsg(msg_pln)
        session.close()

    def send_sectors_info(self, msg_name, flight_id):
        """
        Envoie la liste des secteurs

        :param msg_name: Identifiant du message envoyé et émis en réponse

        :param flight_id: Num de vol (Int)

        :return: NONE
        """
        msg = "SectorsInfo %s Flight=%d List=--" % (msg_name, flight_id)
        IvySendMsg(msg)

    def set_heading(self, agent, flight_id, new_heading, side="", rate=3):
        """
        Appelle la fonction set_heading de control qui crée la nouvelle route suite à un ordre
        de changement de cap après réception d'un message Ivy Aircraft Heading.

        :param flight_id: Num de vol (Int).

        :param new_heading: Nouveau cap (Int).

        :return: NONE
        """
        logging.debug("Set Heading")
        session = self.db_con.get_session()
        control.set_heading(session, flight_id, new_heading, self.current_time, side, rate)
        session.close()
        # send report event
        order = "AircraftHeading|{0}|{1}".format(flight_id, new_heading)
        IvySendMsg("ReportEvent {0} Result=OK "
                   "Info=NIL Order={1}".format(agent, order))
        # send trajectory update event
        IvySendMsg("TrajectoryUpdateEvent Flight={0}".format(flight_id))

    def reset_heading(self, flight_id):
        """
        Appelle la fonction delete_last_version de control qui annule l'ordre de changement de cap
        après réception d'un message Ivy CancelLastOrder

        :param flight_id: Num de vol (Int).

        :return: NONE
        """
        logging.debug("Reset Heading")
        session = self.db_con.get_session()
        control.delete_last_version(session, flight_id)
        session.close()
        # send trajectory update event
        IvySendMsg("TrajectoryUpdateEvent Flight={0}".format(flight_id))

    def send_trajectory(self, msg_name, flight_id, from_type):
        session = self.db_con.get_session()
        start = 0
        if from_type == "now":
            start = self.current_time
        elif re.match("^\d{2}:\d{2}:\d{2}$", from_type):
            start = utils.str_to_sec(from_type)
        flight = session.query(mod.Flight).filter(mod.Flight.id == flight_id).first()
        logging.debug("Vol %d : last_version = %d"%(flight.id, flight.last_version))
        cones = session.query(mod.Cone)\
                       .join(mod.Cone.flight)\
                       .filter(mod.Cone.flight_id == flight_id,
                               mod.Cone.hour > start,
                               mod.Cone.version == mod.Flight.last_version)\
                       .order_by(mod.Cone.hour)\
                       .all()

        nb_msg = (len(cones)/30) + 1
        for i in range(0, nb_msg):
            first, last = 30*i, min(30*(i+1), len(cones))
            data = " ".join([c.format() for c in cones[first:last]])
            if data != "":
                IvySendMsg("Trajectory %s Slice=%s" % (msg_name, data))
        IvySendMsg("Trajectory %s EndSlice" % msg_name)
        session.close()




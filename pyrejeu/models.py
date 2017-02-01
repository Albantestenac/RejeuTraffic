# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre"


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from pyrejeu import utils

Base = declarative_base()


class Beacon(Base):
    """
    Classe associée à la table contenant l'ensemble des balises

    :param id: Identifiant de la balise dans la table

    :param name: Nom de la balise

    :param pos_x: Position de la balise sur l'axe x (NM)

    :param pos_y: Position de la balise sur l'axe y (NM)
    """
    __tablename__='beacons'

    id = Column(Integer, primary_key=True)
    name = Column(String(10))
    pos_x = Column(Float)
    pos_y = Column(Float)

    def __repr__(self):
        return "<Beacon(name='%s', pos_x=%f, pos_y=%f)>" % (self.name, self.pos_x, self.pos_y)

    def display_beacon(self):
        #Fonction renvoyant la balise au format "NOM X,xx Y,yy" (pour messages Ivy principalement)
        return "%s %f %f" % (self.name, self.pos_x, self.pos_y)


class Flight(Base):
    """
    Classe associée à la table contenant l'ensemble des vols

    :param id: Numéro de vol

    :param h_dep: Heure de départ (sec à partir de 00:00:00)

    :param h_arr: Heure d'arrivée (sec à partir de 00:00:00)

    :param fl: Niveau de col de croisière

    :param v: Vitesse de croisière (kts)

    :param callsign: Identifiant appel pour controleur

    :param type: Type d'avion

    :param dep: Aéroport de départ

    :param arr: Aéroport d'arrivee

    :param ssr: Code transpondeur

    :param rvsm: TRUE ou FALSE suivant l'équipement RVSM de l'avion.

    :param tcas: OFF ou TA_ONLY ou TA_RA suivant l'équipement TCAS de l'avion

    :param adsb: Equipement adsb : NO ou YES ou OUT_ONLY

    :param dlink: TRUE ou FALSE suivant l'équipement Data Link de l'avion

    :param last_version: Dernière version des plots associés au vol

    :param flight_plan: Plan de vol associé à ce vol

    :param cones: Ensemble des plots du vol
    """
    __tablename__='flights'

    id = Column(Integer, primary_key=True)
    h_dep = Column(Integer)
    h_arr = Column(Integer)
    fl  = Column(Integer)
    v = Column(Integer)
    callsign = Column(String(10))
    type = Column(String(10))
    dep = Column(String(10))
    arr = Column(String(10))
    ssr = Column(Integer)
    rvsm = Column(String(10))
    tcas = Column(String(10))
    adsb = Column(String(10))
    dlink = Column(String(10))
    last_version = Column(Integer)

    # déclaration des relations
    flight_plan = relationship("FlightPlan", uselist=False, back_populates="flight")
    cones = relationship("Cone", back_populates="flight")

    def __repr__(self):
        return "<Flight(h_dep=%d, h_arr=%d, fl=%d, v=%d, callsign=%s, type=%s, dep=%s, arr=%s, " \
               "ssr=%d, rvsm=%s, tcas=%s, adsb=%s, datalink=%s, last_version=%d)>" % \
               (self.h_dep, self.h_arr, self.fl, self.v, self.callsign, self.type, self.dep, self.arr,
                self.ssr, self.rvsm, self.tcas, self.adsb, self.dlink, self.last_version)

    def display_cones_extract(self):
        def repr(c_list):
            return "\n\t".join([str(c) for c in c_list])

        return "\t%s\n\t ... \n\t%s" % (repr(self.cones[0:2]), repr(self.cones[-3:-1]))


class Cone(Base):
    """
    Classe associée à la table contenant l'ensemble des plots

    :param id: Identifiant du plot dans la table

    :param pos_x: Position du plot sur l'axe y (1/64 NM, CAUTRA)

    :param pos_y: Position du plot sur l'axe y (1/64 NM, CAUTRA)

    :param vit_x: Vitesse de l'avion correspondant au plot sur l'axe x (kts)

    :param vit_y: Vitesse de l'avion correspondant au plot sur l'axe y (kts)

    :param flight_level: FL de l'avion correspondant au plot

    :param rate: Vitesse verticale de l'avion correspondant au plot (ft/min)

    :param tendency: Tendance, montée/palier/descente

    :param hour: Heure d'activation du plot (sec à partir de 00:00:00)

    :param flight_id: Numéro de vol correspondant au plot

    :param version: Version du cone (modification de trajectoire)

    :param flight: Vol associé au plot
    """
    __tablename__='cones'

    id = Column(Integer, primary_key=True)
    pos_x = Column(Float)
    pos_y = Column(Float)
    vit_x = Column(Integer)
    vit_y = Column(Integer)
    flight_level = Column(Integer)
    rate = Column(Integer)
    tendency = Column(Integer)
    hour = Column(Integer)
    flight_id = Column(Integer, ForeignKey('flights.id'))
    version = Column(Integer)

    # déclaration des relations
    flight = relationship("Flight", back_populates="cones")

    def __repr__(self):
        return"<Cone(pos_x=%f, pos_y=%f, vit_x=%d, vit_y=%d, flight_level=%d, rate=%f, tendency=%d, hour=%d, flight=%d, version=%d)>" % \
              (self.pos_x, self.pos_y, self.vit_x, self.vit_y, self.flight_level, self.rate, self.tendency, self.hour, self.flight.id, self.version)

    def format(self):
        return "%.2f %.2f %s %d" % (self.pos_x/64.0, self.pos_y/64.0,
                                    utils.sec_to_str(self.hour),
                                    self.flight_level)


class FlightPlan(Base):
    """
    Classe associée à la table contenant l'ensemble des plans de vol

    :param id: Identifiant du plan de vol dans la table

    :param flight_id: Numero du vol correspondant

    :param flight: Vol associé à ce plan de vol

    :param beacons: Ensemble des balises du plan de vol (objet FlightPlanBeacon)
    """
    __tablename__='flightplans'

    id = Column(Integer, primary_key=True)
    flight_id = Column(Integer, ForeignKey('flights.id'))

    # déclaration des relations
    flight = relationship("Flight", back_populates="flight_plan")
    beacons = relationship("FlightPlanBeacon", back_populates="flight_plan")

    def __repr__(self):
        res = "<FlightPlan(flight=%d)>" % self.flight.id
        for b in self.beacons:
            res += "\n\t%s" % str(b)
        return res


class FlightPlanBeacon(Base):
    """
    Classe associée à la table contenant l'ensemble des balises contenues dans des plans de vol

    :param id: Identifiant de la balise dans la table

    :param order: Ordre de la balise dans le plan de vol

    :param hour: Heure de survol (s à partir de 00:00:00)

    :param V_or_A: Passage Vertical (V) ou à proximité (A)

    :param FL: Niveau de vol au survol

    :param flight_plan_id: Id du plan de vol correspondant

    :param beacon_name: Nom de la balise

    :param flight_plan: Plan de vol associé
    """
    __tablename__='flightplan_beacons'

    id = Column(Integer, primary_key=True)
    order = Column(Integer)
    hour = Column(Integer)
    V_or_A = Column(String)
    FL = Column(Integer)
    flight_plan_id = Column(Integer, ForeignKey('flightplans.id'))
    beacon_name = Column(String(10), ForeignKey('beacons.name'))

    # déclaration des relations
    flight_plan = relationship("FlightPlan", back_populates="beacons")

    def __repr__(self):
        return "<FlightPlanBeacon(order=%d, beacon_name=%s, hour=%d)>" % \
               (self.order, self.beacon_name, self.hour)


class Layer(Base):
    """
    Classe associée à la table contenant l'ensemble des couches

    :param name: Nom de la couche

    :param floor: Niveau plancher

    :param ceiling: Niveau plafond

    :param climb_delay_first: Temps (min) avant la première balise de la couche.
                               mettre l'avion dans cette couche, quand il y arrive en descendant

    :param climb_delay_others: Non implémenté

    :param descent_delay: Temps (min) avant la premiere balise de la couche.
                            mettre l'avion dans cette couche, quand il y arrive en descendant

    :param descent_distance: Non implémenté
    """
    __tablename__='layer'

    name = Column(String, primary_key=True)             # Nome de la couche
    floor = Column(Integer)                             # Niveau plancher
    ceiling = Column(Integer)                           # Niveau plafond
    climb_delay_first = Column(Integer)                 # Temps (min) avant la première balise de la couche.
                                                            # mettre l'avion dans cette couche, quand il y arrive en descendant
    climb_delay_others = Column(Integer)                # Non implementé
    descent_delay = Column(Integer)                     # Temps (min) avant la premiere balise de la couche.
                                                            # mettre l'avion dans cette couche, quand il y arrive en descendant
    descent_distance = Column(Float)                    # Non implémenté

    def __repr__(self):
        return "<Layer(name=%s, floor=%d, ceiling=%d, climb_delay_first=%d, climb_delay_others=%d, descent_delay=%d, descent_distance=%f)>" % \
               (self.name, self.floor, self.ceiling, self.climb_delay_first, self.climb_delay_others, self.descent_delay, self.descent_distance)


if __name__ == "__main__":
    print(Beacon(name='Test', pos_x=10.2, pos_y=-1563.869).display_beacon())
    print(Flight(h_dep=1020, h_arr=1125, fl=340, v=235 , callsign='AF4185', type='A320',
                 dep='LFBO', arr='LFPO', ssr=1000, rvsm="TRUE", tcas="OFF", adsb="YES", dlink="FALSE", pln_event=0))
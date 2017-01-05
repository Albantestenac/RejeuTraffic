# -*- coding: utf-8 -*-
__author__ = "Alban", "Alexandre"

from sqlalchemy.pool import StaticPool
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
import utils


# Mettre echo a True pour acceder au mode verbeux
engine = create_engine('sqlite:///:memory:', 
                       connect_args={'check_same_thread':False},
                       poolclass=StaticPool,
                       echo=False)
Base = declarative_base()


class Beacon(Base):
    __tablename__='beacons'

    id = Column(Integer, primary_key=True)  # Identifiant balise
    name = Column(String(10))               # Nom de la balise
    pos_x = Column(Float)                   # Position de la balise sur l'axe x
    pos_y = Column(Float)                   # Position de la balise sur l'axe y

    def __repr__(self):
        return "<Beacon(name='%s', pos_x=%f, pos_y=%f)>" % (self.name, self.pos_x, self.pos_y)



class Flight(Base):
    __tablename__='flights'

    id = Column(Integer, primary_key=True)                  # Numero de vol
    h_dep = Column(Integer)                                 # Heure de depart        A VOIR AVEC HORLOGE
    h_arr = Column(Integer)                                 # Heure d arrivee        A VOIR AVEC HORLOGE
    fl  = Column(Integer)                                   # Flight level
    v = Column(Integer)                                     # Vitesse
    callsign = Column(String(10))                           # Identifiant appel pour controleur
    type = Column(String(10))                               # Type d avion
    dep = Column(String(10))                                # Aeroport de depart
    arr = Column(String(10))                                # Aeroport d arrivee
    ssr = Column(Integer)									# ssr = Code transpondeur. 0000 si inconnu.
    rvsm = Column(String(10))                  			    # rvsm = TRUE ou FALSE suivant l'équipement RVSM de l'avion.)-
    tcas = Column(String(10))								# tcas = OFF ou TA_ONLY ou TA_RA suivant l'équipement TCAS de l'avion
    adsb = Column(String(10))								# adbs = NO ou YES ou OUT_ONLY
    dlink = Column(String(10))								# dlink = TRUE ou FALSE suivant l'équipement Data Link de l'avion
    pln_event = Column(Integer)                             # PLN Event émis oui=1 ou non=0 

    # déclaration des relations
    flight_plan = relationship("FlightPlan", uselist=False, back_populates="flight")
    cones = relationship("Cone", back_populates="flight")

    def __repr__(self):
        return "<Flight(h_dep=%d, h_arr=%d, fl=%d, v=%d, callsign=%s, type=%s, dep=%s, arr=%s, " \
               "ssr=%s, rvsm=%s, tcas=%s, adsb=%s, datalink=%s, pln_event=%d)>" % \
               (self.h_dep, self.h_arr, self.fl, self.v, self.callsign, self.type, self.dep, self.arr, 
                self.ssr, self.rvsm, self.tcas, self.adsb, self.dlink, self.pln_event)

    def display_cones_extract(self):
        def repr(c_list):
            return "\n\t".join([str(c) for c in c_list])

        return "\t%s\n\t ... \n\t%s" % (repr(self.cones[0:2]), repr(self.cones[-3:-1]))


class Cone(Base):
    __tablename__='cones'

    id = Column(Integer, primary_key=True)              # Identifiant du plot
    pos_x = Column(Float)                               # Position du plot sur l'axe x
    pos_y = Column(Float)                               # Position du plot sur l'axe y
    vit_x = Column(Float)                               # Vitesse de l'avion correspondant au plot sur l'axe x
    vit_y = Column(Float)                               # Vitesse de l'avion correspondant au plot sur l'axe y
    flight_level = Column(Integer)                      # FL de l'avion correspondant au plot
    rate = Column(Float)                                # Vitesse verticale de l'avion correspondant au plot
    tendency = Column(Integer)                          # Tendance, montee ou descente
    hour = Column(Integer)                              # Heure d'activation du plot
    flight_id = Column(Integer, ForeignKey('flights.id'))  # Numero de vol correspondant au plot

    # déclaration des relations
    flight = relationship("Flight", back_populates="cones")

    def __repr__(self):
        return"<Cone(pos_x=%f, pos_y=%f, vit_x=%f, vit_y=%f, flight_level=%d, rate=%f, tendency=%d, hour=%d, flight=%d)>" % \
              (self.pos_x, self.pos_y, self.vit_x, self.vit_y, self.flight_level, self.rate, self.tendency, self.hour, self.flight.id)


class FlightPlan(Base):
    __tablename__='flightplans'

    id = Column(Integer, primary_key=True)                  # Identifiant du plan de vol
    flight_id = Column(Integer, ForeignKey('flights.id'))      # Numero du vol correspondant

    # déclaration des relations
    flight = relationship("Flight", back_populates="flight_plan")
    beacons = relationship("FlightPlanBeacon", back_populates="flight_plan")

    def __repr__(self):
        res = "<FlightPlan(flight=%d)>" % self.flight.id
        for b in self.beacons:
            res += "\n\t%s" % str(b)
        return res

    def listing(self):
        #Fonction renvoyant le plan de vol au format "NOM (V ou A) HEURE FL "
        for b in self.beacons:
            res = b.beacon_name + " "
            res += b.V_or_A + " "
            res += utils.sec_to_str_without_sec(b.hour) + " "
            res += str(b.FL) + " "
        return res


class FlightPlanBeacon(Base):
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


Base.metadata.create_all(engine)

if __name__ == "__main__":
    print(Beacon(name='Test', pos_x=10.2, pos_y=-1563.869))
    print(Flight(h_dep=1020, h_arr=1125, fl=340, v=235 ,
                 callsign='AF4185', type='A320', 
                 dep='LFBO', arr='LFPO', id_flp=20))

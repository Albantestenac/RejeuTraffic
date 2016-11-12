author = "Alban", "Alexandre"

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, ForeignKey

engine = create_engine('sqlite:///:memory', echo=False)

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
    callsign = Column(String(10))                           # Identifiant appel pour controleur
    type = Column(String(10))                               # Type d avion
    dep = Column(String(10))                                # Aeroport de depart
    arr = Column(String(10))                                # Aeroport d arrivee
    h_dep = Column(Integer)                                 # Heure de depart        A VOIR AVEC HORLOGE
    h_arr = Column(Integer)                                 # Heure d arrivee        A VOIR AVEC HORLOGE
    id_flp = Column(Integer, ForeignKey('flightplans.id'))  # Id plan de vol associe

    def __repr__(self):
        return "<Flight(callsign='%s', type=%s, dep=%s, arr=%s, h_dep=%d, h_arr=%d, id_flp=%d)>" % \
               (self.callsign, self.type, self.dep, self.arr, self.h_dep, self.h_arr, self.id_flp)

class Cone(Base):
    __tablename__='cones'

    id = Column(Integer, primary_key=True)              # Identifiant du plot
    pos_x = Column(Float)                               # Position du plot sur l'axe x
    pos_y = Column(Float)                               # Position du plot sur l'axe y
    vit_x = Column(Float)                               # Vitesse de l'avion correspondant au plot sur l'axe x
    vit_y = Column(Float)                               # Vitesse de l'avion correspondant au plot sur l'axe y
    flight_level = Column(Integer)                      # FL de l'avion correspondant au plot
    rate = Column(Float)                                # Vitesse verticale de l'avion correspondant au plot
    tendency = Column(String(10))                       # Tendance, montee ou descente
    hour = Column(Integer)                              # Heure d'activation du plot
    flight = Column(Integer, ForeignKey('flights.id'))  # Numero de vol correspondant au plot

    def __repr__(self):
        return"<Cone(pos_x=%f, pos_y=%f, vit_x=%f, vit_y=%f, flight_level=%d, rate=%f, tendency=%s, hour=%d, flight=%d)>" % \
              (self.pos_x, self.pos_y, self.vit_x, self.vit_y, self.flight_level, self.rate, self.tendency, self.hour, self.flight)

class FLightPlan(Base):
    __tablename__='flightplans'

    id = Column(Integer, primary_key=True)                  # Identifiant du plan de vol
    flight = Column(Integer, ForeignKey('flights.id'))      # Numero du vol correspondant
    beacon_dep = Column(Integer, ForeignKey('beacons.id'))  # Balise de depart

    def __repr__(self):
        return"<FlightPlan(flight=%d, beacon_dep=%d)>" % \
              (self.flight, self.beacon_dep)

class FLightPlanBeacon:
    __tablename__='flightplan_beacons'

    id = Column(Integer, primary_key=True)
    id_flp = Column(Integer, ForeignKey('flightplans.id'))
    order = Column(Integer)
    beacon_name = Column(String(10), ForeignKey('beacons.name'))
    hour = Column(Integer)

    def __repr__(self):
        return"FLightPlanBeacon(id_flp=%d, order=%d, beacon_name=%s, hour=%d)>" % \
              (self.id_flp, self.order, self.beacon_name, self.hour)


Base.metadata.create_all(engine)

balise = Beacon(name='Test', pos_x=10.2, pos_y=-1563.869)
vol = Flight(callsign='AF4185', type='A320', dep='LFBO', arr='LFPO', h_dep=1020, h_arr=1125, id_flp=20)

print balise
print vol

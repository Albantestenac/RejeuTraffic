# -*- coding: utf-8 -*-

import sys
import os
from ivy.std_api import *
from optparse import OptionParser
import logging
import signal
from pyrejeu.clock import RejeuClock
from pyrejeu.importations import RejeuImportation
from pyrejeu import utils as ut
from sqlalchemy.orm import sessionmaker
import pyrejeu.models as mod

Session = sessionmaker(bind=mod.engine)

ivy_logger = logging.getLogger('Ivy')
logging.basicConfig(format='%(asctime)-15s - %(levelname)s - %(message)s')


def on_cx_proc(agent, connected):
    if connected == IvyApplicationDisconnected:
        logging.info('Ivy application %r was disconnected', agent)
    else:
        logging.info('Ivy application %r was connected', agent)


def on_die_proc(agent, _id):
    logging.info('received the order to die from %r with id = %d', agent, _id)


def connect(app_name, ivy_bus):
    IvyInit(app_name,                   # Nom de l'application fournie à Ivy
            "[%s ready]" % app_name,    # Message 'ready'
            0,                          # main loop is local (ie. using IvyMainloop)
            on_cx_proc,                 # handler appelé sur connexion/déconnexion
            on_die_proc)
    IvyStart(ivy_bus)

if __name__ == "__main__":
    # gestion des options
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.set_defaults(ivy_bus="127.255.255.255:2010", verbose=False,
                        app_name="Rejeu", ivy_debug=False)
    parser.add_option('-d', '--debug', action='store_true', dest='verbose',
                      help='View debug message.')
    parser.add_option('-i', '--ivy-debug', action='store_true', 
                      dest='ivy_debug', help='View ivy debug messages')
    parser.add_option('-b', '--ivybus', type='string', dest='ivy_bus',
                      help='Bus id (format @IP:port, default to 127.255.255.255:2010)')
    parser.add_option('-a', '--appname', type='string', dest='app_name',
                      help='Application Name')
    (options, args) = parser.parse_args()

    # initialisation du log
    level, ivy_level = logging.INFO, logging.ERROR
    if options.verbose:  # Si mode verbeux choisi
        level = logging.DEBUG
    if options.ivy_debug:
        ivy_level = logging.INFO
    logging.getLogger().setLevel(level)
    ivy_logger.setLevel(ivy_level)

    # importation du fichier
    if len(args) != 1 or not os.path.isfile(args[0]):
        sys.exit("Error: Usage rejeu.py [options] <trace_file>")
    import_obj = RejeuImportation()
    import_obj.import_file(args[0])

    # connection au bus ivy
    logging.info("Connexion to Ivy bus")
    connect(options.app_name, options.ivy_bus)

    # création de l'horloge
    clock = RejeuClock(ut.str_to_sec("11:24:00"))

    # gestion des signaux
    def handler(signum, frame):
        clock.close()
        IvyStop()
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    # lancement de la boucle principale
    clock.main_loop()



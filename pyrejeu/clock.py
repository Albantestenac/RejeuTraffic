Author = "Alban"

import ivy.std_api as ivy
import time
import logging
import pyrejeu.models as mod


class RejeuClock(object):

    def __init__(self):
        self.running = True
        self.current_time = 0

    def run(self):
        while self.running:
            time.sleep(1)
            logging.debug("Loop running")
            # récupérer les plots à envoyer
            # pour chaque plot
            #ivy.IvySendMsg("")
            self.current_time += 1

    def pause(self):
        pass

    def stop(self):
        self.running = False


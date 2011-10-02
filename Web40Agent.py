#TODO Improve this class
'''
Basic agent for Web40
'''

import os
import sys
import time

sys.path.append('..')

import spade
from spade import Behaviour
from xmpp import Message,Protocol

host = "127.0.0.1"
tags=["presence","message","Iq"]

class ConvBehav(spade.Behaviour.Behaviour):

    def __init__(self):
        spade.Behaviour.Behaviour.__init__(self)
        self._state = 0
        
    
    def _process(self):
        msg = self._receive(True)
        print "--- Message Received: %s" %msg
        
        
        
class MainBehav(spade.Behaviour.Behaviour):
    """
    #TODO
    add description
    """

    def _process(self):
        msg = self._receive(True)
        print "+Message received %s" % msg
        sndr = msg.getFrom().getStripped()
        if(not self.myAgent._conversations.has_key(sndr)):
            print "***Adding handler"
            templ=Behaviour.BehaviourTemplate(None)
            for i in tags:
                mess = Protocol(i)
                mess.setFrom(sndr)
                tmp = Behaviour.MessageTemplate(mess,regex=True)
                templ= templ or tmp
            b = ConvBehav()
            self.myAgent._conversations[sndr]=b
            self.myAgent.addBehaviour(b,templ)
            print "***Added "

        
        #print str(msg)


class Web40Agent(spade.Agent.Agent):
                
    def __init__(self, agentjid, password, port=5222, debug=[], p2p=False):
        spade.Agent.Agent.__init__(self, agentjid, password, port=port, debug=debug, p2p=p2p)
        self._conversations = {}
    def _setup(self):
        mb = MainBehav()
        self.setDefaultBehaviour(mb)
        print "Agent Web40 started"


a = Web40Agent("a@"+host,"secret")

time.sleep(1)
#a.setDebugToScreen()
a.start()

alive = True
import time
while alive:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        alive=False
a.stop()
sys.exit(0)

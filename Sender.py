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
import xmpp

host = "127.0.0.1"


class Sender(spade.Agent.Agent):
        
    class SendMsgBehav(spade.Behaviour.OneShotBehaviour):
        """
        #TODO
        add description
        """

        def _process(self):
            msg = xmpp.Message(to="a@127.0.0.1/spade")
            msg.setBody("testSendMsg")
            print ">Sending message in 3 . . ."
            time.sleep(1)
            print ">Sending message in 2 . . ."
            time.sleep(1)
            print ">Sending message in 1 . . ."
            time.sleep(1)

            self.myAgent.send(msg)
            
            print "I sent a message"
            #print str(msg)
    
    class RecvMsgBehav(spade.Behaviour.EventBehaviour):
        """
        This EventBehaviour gets launched when a message that matches its template arrives at the agent
        """

        def _process(self):            
            print "This behaviour has been triggered by a message!"
            msg =self._receive(True)
            print msg
            print "%%Type:",type(msg)
            print "#########Bye"
            rep = msg.buildReply()
            rep.setBody(msg.getBody())
            self.myAgent.send(rep)
            print "Message sent"
            
    
    def _setup(self):
        # Create the template for the EventBehaviour: a message from myself
        msg = xmpp.Message(frm=".*@127.0.0.1/spade")
       # template.setSender(spade.AID.aid("prueba2@"+host,["xmpp://prueba2@"+host+"/spade"]))
        t = spade.Behaviour.MessageTemplate(msg,regex=True)
        print "Template:",t
        
        # Add the EventBehaviour with its template
        self.addBehaviour(self.RecvMsgBehav(),t)
        
        # Add the sender behaviour
        self.addBehaviour(self.SendMsgBehav())

    
a = Sender("a@"+host,"secret")

time.sleep(1)
a.setDebugToScreen()
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

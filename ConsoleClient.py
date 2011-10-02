'''
Created on Aug 26, 2011

@author: balkian
'''
import xmpp
import time
import logging
import threading
import sys
import traceback
import cmd

x = logging.getLogger("consoleClient")
x.setLevel(logging.DEBUG)
h = logging.StreamHandler()
f = logging.Formatter("%(levelname)s %(asctime)s %(funcName)s %(lineno)d %(message)s")
x.addHandler(h)

class jabberProcess(threading.Thread):

    def __init__(self, socket):
        self.jabber = socket
        #self._alive = True
        self._forceKill = threading.Event()
        self._forceKill.clear()
        threading.Thread.__init__(self)
        self.setDaemon(False)

    def _kill(self):
        try:
            self._forceKill.set()
        except:
            #Agent is already dead
            pass

    def forceKill(self):
        return self._forceKill.isSet()

    def run(self):
        """
        periodic jabber update
        """
        while not self.forceKill():
            try:
                err = self.jabber.Process(0.4)
            except Exception, e:
                _exception = sys.exc_info()
                if _exception[0]:
                    x.debug( '\n'+''.join(traceback.format_exception(_exception[0], _exception[1], _exception[2])).rstrip(),"err")
                    x.debug("Exception in jabber process: "+ str(e))
                    x.debug("Jabber connection failed (dying)")
                    self._kill()
                    err = None

                if err == None or err == 0:  # None or zero the integer, socket closed
                    x.debug("Client disconnected (dying)")
                    self._kill()

class ConsoleClient(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)              # initialize the base class
        self.prompt = "Command> "   # customize the prompt
        self.intro = 'Console client with basic functionalities'
    
    def _add_local(self, jid):
        if not jid.find('@')+1:
            return "%s@127.0.0.1"%jid
        return jid

    
    def error_handler(self, type, value, traceback): 
        print "Error:", type 
        print "Value:", value

    def messageHandler(self, conn, mess, raiseFlag=True):
        x.info('Got a message: %s' % mess)
    
    def presenceHandler(self, conn, mess, raiseFlag=True):
        x.info('Got a presence: %s' % mess)
        x.info('Type: %s'%str(mess.getType()))
        if str(mess.getType()) == 'subscribe':
            x.info('Subscribe request')
            self.conn.sendPresence(mess.getFrom(), 'subscribed')
    
    def iqHandler(self, conn, mess, raiseFlag=True):
        x.info('Got an iq: %s' % mess)
            
    def auth(self,tjid,passwd,autoregister=False):
        jid=xmpp.JID(tjid)
        user,server=jid.getNode(),jid.getDomain()
        x.info('Using: %s @ %s : %s' % (user,server,passwd))
        self.conn=xmpp.Client(jid.getDomain(),5222,debug=[])
        tries=5
        while not self.conn.connect(use_srv=None) and tries >0:
            time.sleep(0.005)
            tries -=1
        if tries <=0 :
            x.info("There is no XMPP server at " + server + " . Agent dying...")
            sys.exit(2)
    
        if (self.conn.auth(user,passwd) == None):
    
            x.error( "First auth attempt failed. Trying to register")
    
            if (autoregister):
                self.reg(jid,passwd)
                self.auth(tjid,passwd)
            return
        print "%s got authed"%(user)
        
        self.conn.RegisterHandler('message',self.messageHandler)
        self.conn.RegisterHandler('presence',self.presenceHandler)
        self.conn.RegisterHandler('iq',self.iqHandler)
        self.conn.sendInitPresence(False)
        jabber_process = jabberProcess(self.conn)
        jabber_process.start()


        
    def reg(self,jid,passwd):
        user,server=jid.getNode(),jid.getDomain()
        conn=xmpp.Client(server,5222,debug=[])
        conn.connect()
        x.info('user %s server %s' % (user,server))
#        xmpp.features.getRegInfo(conn,jid.getDomain())
        xmpp.features.register(conn,jid.getDomain(),\
        {'username':user, 'password':str(passwd), 'name':user})

    def do_auth(self,line):
        jid=raw_input('Enter jid: ')
        passwd=raw_input('Enter password:')
        reg=raw_input('Autoregister? [Y/n]: ')
        autoregister=(reg.lower() in ['true','yes','y'])
        jid = self._add_local(jid)
        self.auth(jid,passwd,autoregister)

    def do_send(self,line):
        jid=raw_input('To: ')
        body=raw_input('Body:')
        jid=self._add_local(jid)
        mess=xmpp.Message(jid, body)
        self.conn.send(mess)
        
    def do_raw(self,line):
        self.conn.send(line)


if __name__ == '__main__':
    cl = ConsoleClient()
    cl.cmdloop()

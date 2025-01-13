# coding: utf-8

import time,sys,os
sys.path.append(os.getcwd())
sys.path.append(os.getcwd()+'/../')

from HPSocket import TcpPack

class Client(TcpPack.HP_TcpPackClient):
    counter = 0
    EventDescription = TcpPack.HP_TcpPackServer.EventDescription

    @EventDescription
    def OnSend(self, Sender, ConnID, Data):
        print('[%d, OnSend] < %s' % (ConnID, repr(Data)))

    @EventDescription
    def OnConnect(self, Sender, ConnID):
        print('[%d, OnConnect] Success.' % ConnID)

    @EventDescription
    def OnReceive(self, Sender, ConnID, Data):
        self.Send(Sender=Sender, ConnID=ConnID, Data=Data)
        print('[%d, OnReceive] < %s' % (ConnID, repr(Data)))
        self.SendTest()

    def SendTest(self):
        self.counter += 1
        self.Send(self.Client, 'try start %d'%self.counter)


if __name__ == '__main__':
    cnt = Client()
    cnt.Start(host='127.0.0.1', port=6000, head_flag=0x169)
    cnt.SendTest()
    while True:
        time.sleep(1)
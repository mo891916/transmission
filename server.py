import os

from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol

from mytool import get_vnn_ip
from mytool import clean_file_folder, writefile
from mytool import byte_utf8, str_utf8

clients = []
AUTHENTICATION = 0
CMD_TEXT = 1
BAT_IP = 2
VERSION = 'VERSION:1.2'
sourceDir = 'download'


class MyDownLoad(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.prepare = 0
        self.filename = ""
        self.recvBuffer = byte_utf8('')
        self.vnnIp = str(get_vnn_ip()) + '\t'
        if not os.path.exists('D:\\download'):
            os.makedirs('D:\\download')
        if not os.path.exists(sourceDir):
            os.makedirs(sourceDir)
        os.system('copy download\\*.* "D:\\download"')

    def transport_write_str(self, my_str):
        self.transport.write(byte_utf8(str(my_str)))

    def connectionMade(self):
        self.transport_write_str(self.vnnIp + VERSION)

    def dataReceived(self, data):
        self.operate_date(data)

    def operate_date(self, data):
        self.recvBuffer = self.recvBuffer + data
        while len(self.recvBuffer) > 0:
            index_begin = self.recvBuffer.find(byte_utf8('CMD_BEGIN'))
            index_end = self.recvBuffer.find(byte_utf8('CMD_END'))
            if index_begin >= 0 and index_end >= 0:
                line = self.recvBuffer[index_begin + 9:index_end]
                self.recvBuffer = self.recvBuffer[index_end + 7:]
                if line == byte_utf8('Sync'):
                    clean_file_folder(sourceDir)
                if line[0:3] == byte_utf8('End'):
                    self.prepare = 0
                    self.transport_write_str(self.vnnIp + self.filename)
                elif line[0:5] == byte_utf8('File:'):
                    name = str_utf8(line[5:])
                    self.filename = os.path.join(sourceDir, name)
                    self.prepare = 1
                elif line[0:7] == byte_utf8('Folder:'):
                    name = str_utf8(line[7:])
                    self.filename = os.path.join(sourceDir, name)
                    os.mkdir(self.filename)
                elif self.prepare == 1:
                    writefile(self.filename, line)
            else:
                break


class DownLoadFactory(Factory):
    def __init__(self):
        self.numProtocols = 0

    def buildProtocol(self, addr):
        return MyDownLoad(self)


class MyServer(Protocol):
    def __init__(self, factory):
        self.factory = factory
        self.pwd = '12321'
        self.vnnIp = str(get_vnn_ip()) + '\t'

    def transport_write_str(self, my_str):
        self.transport.write(byte_utf8(str(my_str)))

    def connectionMade(self):
        self.transport_write_str(self.vnnIp + VERSION)
        clients.append(self)

    def connectionLost(self, reason):
        clients.remove(self)

    def dataReceived(self, data):
        data = str_utf8(data)
        data_dic = eval(data)
        try:
            if data_dic[AUTHENTICATION] == self.pwd:
                for key in data_dic.keys():
                    if key == CMD_TEXT:
                        cmd = data_dic[key]
                        flag = os.system(cmd)
                        if flag == 0:
                            result = 'cmd【%s】execute success \n' % cmd
                        else:
                            result = 'cmd【%s】execute failed \n' % cmd
                        self.transport_write_str(self.vnnIp + result)
                        self.transport_write_str(self.vnnIp + 'operate_over\n')
                    elif key == BAT_IP:
                        cmds = data_dic[key]
                        for cmd in cmds:
                            flag = os.system(cmd)
                            if flag == 0:
                                result = 'bat【%s】execute success \n' % cmd
                            else:
                                result = 'bat【%s】execute failed \n' % cmd
                            self.transport_write_str(result)
                        self.transport_write_str(self.vnnIp + 'operate_over \n')
            else:
                self.transport_write_str(self.vnnIp + 'Authenticate failed！')
                self.transport.loseConnection()
        except:
            self.transport_write_str(self.vnnIp + 'deal failed！')
            self.transport.loseConnection()


class ServerFactory(Factory):
    def buildProtocol(self, addr):
        return MyServer(self)


server_point = TCP4ServerEndpoint(reactor, 9901)
server_point.listen(ServerFactory())

download_point = TCP4ServerEndpoint(reactor, 9900)
download_point.listen(DownLoadFactory())

reactor.run()

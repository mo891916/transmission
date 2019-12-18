from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
from mytool import byte_utf8, str_utf8

port0 = 9900
port1 = 9901
port2 = 9902
db = Connection_log(db='log')
ip_stores = [[1, '10.148.1.1', 'desc01'], [2, '10.148.1.2', 'desc02']]
store_ip = {'1desc01': '10.148.1.1', '2desc02': '10.148.1.2'}


class FeedBack(Protocol):
    def dataReceived(self, data):
        datas = str_utf8(data).split('\n')
        for data in datas:
            if data.find('10.148') >= 0:
                strs = data.split('\t')
                print(ip_stores[strs[0]], strs[1:])
                db.operate_alt("insert into t_log_control (computer,message) values ('%s','%s')" % (
                    ip_stores[strs[0]].strip(), '\t'.join(strs[1:])))
            else:
                print(data)
            if data.find('operate_over') > -1:
                self.connectionLost()

    def connectionMade(self):
        self.transport.write(byte_utf8(str(data_dic)))


class SendFactory(ClientFactory):
    def __init__(self):
        self.protocol = None

    def buildProtocol(self, addr):
        self.protocol = FeedBack()
        return self.protocol

    def clientConnectionLost(self, connector, reason):
        print("断开连接: ", reason)

    def clientConnectionFailed(self, connector, reason):
        print("连接失败: ", reason)
        # del (self)


data_dic_kill = {0: '12321', 1: r'TASKKILL /F /IM server.exe'}
data_dic_start = {0: '12321', 1: r'start "" server.exe'}
data_dic_hi = {0: '12321'}
data_dic_copy_all = {0: '12321', 1: r'copy E:\application\download\*.* "E:\M6广告" /y'}
data_dic_del = {0: '12321', 1: r'del /f/s/q "D:\download\"document*"'}
data_dic_update_time = {0: '12321', 1: r'net time \\10.148.1.3 /set /y'}
data_dic_md = {0: '12321', 1: r'IF NOT EXIST "E:\tools" MD "E:\tools"'}

data_dic = data_dic_kill
send_factory = SendFactory()
keys = ['1desc01']
for key in keys:
    reactor.connectTCP(store_ip[key], port2, send_factory)
reactor.run()

import os

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory

from mytool import byte_utf8, str_utf8

ip_stores = [[1, '10.148.1.1', 'desc01'], [2, '10.148.1.2', 'desc02']]
store_ip = {'1desc01': '10.148.1.1', '2desc02': '10.148.1.2'}
port0 = 9900
tran_folder = 'D:\\transport'
# db connecter to log message
db = Connection_log(db='log')


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

    def transport_write_str(self, my_str):
        self.transport.write(byte_utf8(str(my_str)))

    def connectionMade(self):
        self.transport_write_str("CMD_BEGIN")
        self.transport_write_str("Sync")
        self.transport_write_str("CMD_END")
        self.send_file_folder(tran_folder)

    def send_file_folder(self, folder):
        for f in os.listdir(folder):
            sourceF = os.path.join(folder, f)
            if os.path.isfile(sourceF):
                # 传送一段
                self.transport_write_str("CMD_BEGIN")
                self.transport_write_str("File:" + sourceF[len(tran_folder) + 1:])
                self.transport_write_str("CMD_END")
                fp = open(sourceF, 'rb')
                while 1:
                    filedata = fp.read(10240)
                    if not filedata:
                        break
                    else:
                        self.transport_write_str("CMD_BEGIN")
                        self.transport.write(filedata)
                        self.transport_write_str("CMD_END")
                fp.close()
                self.transport_write_str("CMD_BEGIN")
                self.transport_write_str("End")
                self.transport_write_str("CMD_END")
            if os.path.isdir(sourceF):
                self.transport_write_str("CMD_BEGIN")
                self.transport_write_str("Folder:" + sourceF[len(tran_folder) + 1:])
                self.transport_write_str("CMD_END")
                self.send_file_folder(sourceF)


port = port0
send_factory = ClientFactory()
send_factory.protocol = FeedBack
keys = ['1desc01']

for key in keys:
    reactor.connectTCP(store_ip[key], port, send_factory)
reactor.run()

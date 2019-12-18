import os
import socket


def get_vnn_ip():
    add_infos = socket.getaddrinfo(socket.gethostname(), None, family=socket.AF_INET)
    for add_info in add_infos:
        ip = add_info[-1][0]
        if ip.find('10.148') > -1:
            return ip
    return


def delete_file_folder(src):
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc = os.path.join(src, item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass


def clean_file_folder(src):
    delete_file_folder(src)
    os.mkdir(src)


def writefile(filename, data):
    fp = open(filename, 'a+b')
    fp.write(data)
    fp.close()


def byte_utf8(my_str):
    return bytes(my_str, encoding='utf-8')


def str_utf8(my_byte):
    return str(my_byte, encoding='utf-8')

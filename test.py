from time import sleep
from connection import Imap, AccountConfig
from storage import Email, file_from_local

conf = AccountConfig()
conf.imap.user = 'chat@hennige-it.de'
conf.imap.password = 'testFUbla'
conf.imap.host = 'imap.hennige-it.de'
#conf.imap_host = 'hennige-it.de'
conf.imap.port = 993
conf.smtp.user = 'chat@hennige-it.de'
conf.smtp.password = 'testFUbla'
conf.smtp.host = 'smtp.hennige-it.de'
conf.smtp.port = 465
connections = []


if __name__ == "__main__":
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    #ssl_context.verify_mode = ssl.CERT_NONE

    imap = Imap(conf, unsafe=True)
    att = file_from_local('/home/frank/kodi_crashlog-20190508_180630.log')
    
    #email = Email(imap).new('/chat/', 'info@hennige-it.de', 'Faruk')
    email = Email(imap, imap.uids[-1])
    email.add_file(att)
    #email.remove_file_by_id('XUFrd0gv')
    #email.remove_file_by_id('tiFt59AS')
    email.save()
    #email.body.add_item('message', 'child')
    #email.add_file(att)
    #email.body.remove_item('86xoerHx')
    #ppp = email.body.add_item('message')
    #email.save()
    import pdb; pdb.set_trace()  # <---------

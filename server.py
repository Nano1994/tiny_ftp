import os
from socket import *
class ftp_server(object):
	BUFSIZE = 4096
	login_state = False
	HOST = ''
	PORT = 1234
	ADDR = (HOST,PORT)
	user = 'nano'
	password = '123'
	data_sock = 0
	data_client_sock = 0
	data_port = 0
	data_type = "ASCII"
	def __init__(self):
		self.sock = socket(AF_INET,SOCK_STREAM)
		self.clientSock = 0
		self.sock.bind(self.ADDR)
		self.sock.listen(5)

	def run(self):
		while True:
			print "waiting for client to connect"
			self.clientSock,addr = self.sock.accept()
			self.welcome()
			print "accept client"
			self.clientSock.send("localhost\n")
			while True:
				raw_cmd = self.clientSock.recv(self.BUFSIZE)
				if  raw_cmd[:4]=='QUIT':
					break 
				self.handle_cmd(raw_cmd)
				
			self.clientSock.close()

	def handle_cmd(self,raw_cmd):
		cmd = raw_cmd[:-2].split()
		if cmd[0]=='USER':
			self.handle_user(cmd)
		elif cmd[0]=='PASS':
			self.handle_pass(cmd)
		elif cmd[0]=='PASV':
			self.handle_pasv(cmd)
		elif cmd[0]=='LIST':
			self.handle_list(cmd)
		elif cmd[0]=='PWD':
			self.handle_pwd(cmd)
		elif cmd[0]=='RETR':
			self.handle_retr(cmd)
		elif cmd[0]=='STOR':
			self.handle_stor(cmd)
		elif cmd[0]=='TYPE':
			self.handle_type(cmd)
		elif cmd[0]=='DELE':
			self.handle_dele(cmd)
		elif cmd[0]=='CWD':
			self.handle_cwd(cmd)
		else :
			self.handle_error_cmd()
	def welcome(self):
		self.clientSock.send("220 Welcome to Portal of My FTP server\n")

	def handle_user(self,cmd):
		if len(cmd) != 2:
			self.handle_error_para()
		elif cmd[1]!=self.user :
			self.clientSock.send("530 wrong user\n")
		else :
			self.clientSock.send("331 Password required for %s\n"%cmd[1])
	def handle_pass(self,cmd):
		if len(cmd) != 2:
			self.handle_error_para()
		elif cmd[1]!= self.password:
			self.clientSock.send("530 wrong password\n")
		else :
			self.clientSock.send("230- Quotas on: \n")
			self.clientSock.send("230 User %s logged in\n"%self.user)
	def handle_pasv(self,cmd):
		if len(cmd) != 1:
			self.handle_error_para()
		else :
			self.data_sock = socket(AF_INET,SOCK_STREAM)
			self.data_sock.bind((self.HOST,0))
			self.data_sock.listen(5)
			ip,port = self.data_sock.getsockname()
			self.clientSock.send("227 Entering Passive Mode (%s,%u,%u).\n"%(",".join(ip.split('.')),(port>>8&0xff),(port&0xff)))
			self.data_client_sock,addr= self.data_sock.accept()
			self.data_sock.close()
	def handle_list(self,cmd):
		if len(cmd) >= 2:
			self.handle_error_para()
		elif len(cmd) == 1:
			self.clientSock.send("150 Opening %s mode data connection for file list\n"%self.data_type)
			file_list = os.listdir('.')
			data = ''
			for f in file_list:
				data = data + f +'\n'
			self.data_client_sock.send(data)
			self.clientSock.send("226 Transfer complete\n")
		else :
			self.clientSock.send("150 Opening %s mode data connection for file list\n"%self.data_type)
			os.listdir(cmd[1])
			data = ''
			for f in file_list:
				data = data + f +'\n'
			self.data_client_sock.send(data)
			self.clientSock.send("226 Transfer complete\n")
		self.data_client_sock.close()
		#self.data_sock.close()
	def handle_pwd(self,cmd):
		if len(cmd) != 1 :
			self.handle_error_para()
		else :
			self.clientSock.send("257 The current working directory is"+os.getcwd())
	def handle_retr(self,cmd):
		if len(cmd) != 2 :
			self.handle_error_para()
		else :
			try:
				if self.data_type=="ASCII":
					f = open(cmd[1])
				elif self.data_type=="IMAGE":
					f = open(cmd[1],'rb')

			except IOError:
				self.clientSock.send("550 No such file\n")
				self.data_client_sock.close()
				return 
			while(1):
				self.clientSock.send("150 Opening %s mode data connection for file transfer\n"%self.data_type)
				data = f.read(self.BUFSIZE)
				if not data:
					break
				self.data_client_sock.send(data)
			f.close()
			self.clientSock.send("226 Transfer complete\n")
		self.data_client_sock.close()

	def handle_stor(self,cmd):
		if len(cmd) != 2 :
			self.handle_error_para()
		else :
			if self.data_type =='ASCII':
				f = open(cmd[1],'w')
			else :
				f = open(cmd[1],'wb')
			self.clientSock.send("150 Opening %s mode data connection for file transfer\n"%self.data_type)
			while(1):
				data = self.data_client_sock.recv(self.BUFSIZE)
				if not data:
					break
				f.write(data)
			f.close()
			self.data_client_sock.close()
			self.clientSock.send("226 Transfer complete\n")
	def handle_type(self,cmd):
		if len(cmd) != 2 :
			self.handle_error_para()
		else :
			if cmd[1]=='A':
				self.data_type = 'ASCII'
				self.clientSock.send("200 Type set to %s\n"%cmd[1])
			elif cmd[1] == 'I':
				self.data_type = 'IMAGE'
				self.clientSock.send("200 Type set to %s\n"%cmd[1])
			else :
				self.clientSock.send("500 'Type %s' not understood\n"%cmd[1])
	def handle_dele(self,cmd):
		if len(cmd) != 2:
			self.handle_error_para()
		else :
			try :
				os.remove(cmd[1])
				self.clientSock.send("250 delete operation successful\n")
			except OSError :
				self.clientSock.send("550 No such file or directory\n")
	def handle_cwd(self,cmd):
		if len(cmd) != 2 :
			self.handle_error_para()
		else :
			try:
				os.chdir(cmd[1])
				self.clientSock.send("250 change directory to %s\n"%cmd[1])
			except IOError:
				self.clientSock.send("550 No such file or directory\n")

	def handle_error_cmd(self):
		self.clientSock.send("500 wrong command\n")
	def handle_error_para(self):
		self.clientSock.send("501 wrong parameter\n")



def main():
	my_ftp = ftp_server()
	my_ftp.run()
if __name__ == '__main__':
	main()
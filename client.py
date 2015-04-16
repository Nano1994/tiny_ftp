from socket import *
import re
import os
class ftp_client(object):
	"""docstring for ftp_client"""
	BUFSIZE = 4096
	login_state = False
	def __init__(self, hostname):
		super(ftp_client, self).__init__()
		self.hostname = hostname
		self.port = 21
		self.data_port = 0
		self.addr = (self.hostname,self.port)
		self.client_sock = socket(AF_INET,SOCK_STREAM)
		self.data_sock = 0
		self.client_sock.connect(self.addr)
		print self.client_sock.recv(self.BUFSIZE)
		print self.client_sock.recv(self.BUFSIZE)
		#print "welcome:"+data+"-----end of a command--------"
	def sendcmd(self,cmd):
		self.client_sock.send(cmd)
		return self.client_sock.recv(self.BUFSIZE)

	def login(self,username='',password=''):
		self.username = username
		self.password = password
		info = self.sendcmd("USER "+self.username+"\r\n")
		print "username_word:"+info#+"----------end of a command---------"
		if info[:3] == '331':
			info = self.sendcmd("PASS "+self.password+"\r\n")
			if info[:3] == '230':
				print info
				print self.client_sock.recv(self.BUFSIZE)
				self.login_state = True
				#print "-------end of a command------"
			else :
				print info
				print "password error"
		else :
			print info
			print "username error"

	def pasv(self):
		info = self.sendcmd("PASV "+"\r\n")
		if info[:3]=="227":
			p =re.compile(r'\d+')
			number = p.findall(info)
			self.data_port=  (int(number[5])*256+int(number[6]))%65536
			self.data_sock = socket(AF_INET,SOCK_STREAM)
			self.data_sock.connect((self.hostname,self.data_port))
		else :
			print "pasv error"
		print info

	def ls(self,path=''):
		self.pasv()
		info_file = self.sendcmd("LIST "+path+"\r\n")
		print info_file
		data_file = self.data_sock.recv(self.BUFSIZE)
		print data_file
		self.data_sock.close()
		info_file = self.client_sock.recv(self.BUFSIZE)
		print info_file
		#info_dir = self.sendcmd("NLST "+path+"\r\n")
		#data_dir = self.data_sock.recv(self.BUFSIZE)
		
		#print info_dir
		#print "second\n"+data_dir
		#print data_dir
		#print data_file# + data_dir

	def pwd(self):
		print self.sendcmd("PWD "+"\r\n")
		

	def cd(self,path):
		info = self.sendcmd("CWD "+path+"\r\n")
		print "cd:"+info
	def get(self,file_name):
		self.pasv()
		self.type('I')
		info = self.sendcmd("RETR "+file_name+"\r\n")
		if info[:3] == '550':
			print info
		else :
			f = open(file_name,'wb')
			while(1):
				data = self.data_sock.recv(self.BUFSIZE)
				if not data :
					break
				f.write(data)
			f.close()
			self.data_sock.close()
			print self.client_sock.recv(self.BUFSIZE)

	def put(self,file_name):
		self.pasv()
		self.type('I')
		try:
			f = open(file_name)
		except IOError:
			print "No such file"
			self.data_sock.close()
			return
		info = self.sendcmd("STOR "+file_name+"\r\n")
		while(1):
			data = f.read(self.BUFSIZE)
			if not data:
				break
			self.data_sock.send(data)
		f.close()
		self.data_sock.close()
		print self.client_sock.recv(self.BUFSIZE)
	def type(self,mode):
		print self.sendcmd("TYPE "+mode+'\r\n')

	def delete(self,file_name):
		print self.sendcmd("DELE "+file_name+'\r\n')

	def logout(self):
		print self.sendcmd("QUIT "+'\r\n')
		self.login_state = False
def parsing(raw_cmd):
	list_cmd = raw_cmd.split()
	#print list_cmd
	return list_cmd
def main():
	while 1:
		print "ftp>"
		raw_cmd = raw_input()
		list_cmd= parsing(raw_cmd)
		if list_cmd[0]=='login':
			my_ftp = ftp_client(list_cmd[1])
			my_ftp.login(list_cmd[2],list_cmd[3])

		elif list_cmd[0]=='exit':
			break;

		elif list_cmd[0]=='ls':
			if len(list_cmd) == 1:
				my_ftp.ls()
			else:
				my_ftp.ls(list_cmd[1])

		elif list_cmd[0]=='pwd':
			my_ftp.pwd()

		elif list_cmd[0]=='logout':
			my_ftp.logout()

		elif list_cmd[0]=='put':
			if len(list_cmd) >= 2:
				my_ftp.put(list_cmd[1])
			else :
				print "the filename can't be empty"

		elif list_cmd[0]=='get':
			if len(list_cmd) >= 2:
				my_ftp.get(list_cmd[1])
			else :
				print "the filename can't be empty"

		elif list_cmd[0]=='rm':
			if len(list_cmd) >= 2:
				my_ftp.delete(list_cmd[1])
			else :
				print "the filename can't be empty"

		elif list_cmd[0]=='cd':
			if len(list_cmd) >= 2:	
				my_ftp.cd(list_cmd[1])
			else :
				print "please enter a path"

		else :
			print "wrong command"
if __name__ == '__main__':
	main()

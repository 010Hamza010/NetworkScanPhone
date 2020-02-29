from os import popen
from threading import Thread
from re import search
from time import sleep
from datetime import datetime as dt
from getmac import get_mac_address
from requests import get
import socket

Data = []

ValidIp = []
OpenPort = []

sent_ip=0
sent_port=0

errors=0

def Scan():
	global sent_port,OpenPort
	port = current_port
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		s.connect((Target,port))
	except ConnectionRefusedError:
		#port is close
		pass
	except:
		#50% The host is down
		#50% Connection lost
		pass
	else:
		OpenPort.append(port)
	sent_port-=1
def Ping():
	global sent_ip,errors
	ip = '192.168.1.'+str(current_ip)
	info = ''.join(popen('ping -c 1 -W 5 {}'.format(ip)))
	if not search('Network is unreachable', info):
		if not search('100%',info):
			ValidIp.append(ip)
			print('[!] Device Found => {}'.format(ip))
	else:
		errors+=1
	sent_ip-=1
def Check():
	try:
		get('http://192.168.1.1')
	except:
		return False
	else:
		return True

if __name__ == '__main__':
	while True:
		if Check():
			start_time = dt.today().strftime('%Y/%m/%d %X')
			print('The script start at : {}'.format(start_time))
			Data.append('The script start at : {}'.format(start_time))
			try:
				PublicIp = get('http://api.ipify.org').text
			except:
				pass
			else:
				Data.append('Public Ip : '+PublicIp)
				print('Public Ip : '+PublicIp)
				break
	for current_ip in range(1,254):
		Thread(target = Ping).start()
		sent_ip+=1
	#Loop untill every ping finish
	while True:
		if sent_ip == 0:
			#check if the router is in the list -_-
			if '192.168.1.1' not in ValidIp:
				ValidIp.append('192.168.1.1')

			print('There is {} devices in the network'.format(len(ValidIp)))
			Data.append('There is {} devices in the network'.format(len(ValidIp)))
			for ip in sorted(ValidIp):
				if errors < 5:
					print('-'*6,ip,'-'*6)
					Data.append('-'*6+ip+'-'*6)
					try:
						print(socket.gethostbyaddr(ip)[0])
						Data.append(socket.gethostbyaddr(ip)[0])
					except:
						pass
					mac = get_mac_address(ip=ip)

					tried=0
					while str(type(mac)).split("'")[1] == 'NoneType':
						if tried < 5:
							tried+=1
							mac = get_mac_address(ip=ip)
						else:
							print('[!] Impossible to get the mac address')
							Data.append('[!] Impossible to get the mac address')
							break

					print('MAC : {}'.format(mac))
					Data.append('MAC : {}'.format(mac))
					Target = ip
					OpenPort = []

					for current_port in range(1,100):
						Thread(target = Scan).start()
						sent_port+=1
						sleep(0.2)
					#loop untill the scan finish
					while True:
						if sent_port == 0:
							if len(OpenPort) > 0:
								for port in sorted(OpenPort):
									print('[{}] Is open'.format(port))
									Data.append('[{}] Is open'.format(port))
							else:
								print('All the ports are closed')
								Data.append('All the ports are closed')
							break
				else:
					print('[!] Connection lost!')
					break
				ValidIp.remove(ip)
			if errors >= 5:
				for ip in sorted(ValidIp):
					print('-'*6,ip,'-'*6)
					Data.append('-'*6+ip+'-'*6)

			end = dt.today().strftime('%Y/%m/%d %X')
			print('The script end at : {}'.format(end))
			Data.append('The script finish at : {}'.format(end))
			#save the data
			with open('NetworkScan-{}.txt'.format(PublicIp),'w') as file:
				file.write('\n'.join(Data))
			break

import subprocess
from time import strftime,gmtime
import json
import os
import requests
import pymysql
import threading
def main():
	try:
		ipaddress={}
		for row in conn_mysql():
			ipaddr=row[1]
			rtspaddr=row[2]
			if check_ip(ipaddr):
				ipaddress[ipaddr]=rtspaddr
				#command1='mkdir '+ipaddr
				#command='nohup ffmpeg -re -rtsp_transport tcp -i '+row[2]+' -codec:v copy -codec:a aac  -f hls -hls_list_size 6 -hls_wrap 10 -hls_time 5 '+row[1]+'/live1.m3u8&'
				#print(command)
				
			else:
				print(ipaddr+"不通")
		print(ipaddress)
		threads=[]
		for ip in ipaddress.items():
			t=threading.Thread(target=transcode,args=(ip[0],ip[1]))
			threads.append(t)
		for t in threads:
			t.setDaemon(True)
			t.start()
		for t in threads:
			t.join()
		subprocess.getstatusoutput('printf "\n"')
	except:
		print ("Error: 数据错误")
def transcode(ipaddr,rtspaddr):
	if check_dir(ipaddr)==False:
		mkdircmd='mkdir '+ipaddr
		subprocess.getstatusoutput(mkdircmd)
	command='nohup ffmpeg -re -rtsp_transport tcp -i '+rtspaddr+' -codec:v copy -codec:a aac  -f hls -hls_list_size 6 -hls_wrap 10 -hls_time 5 '+ipaddr+'/live1.m3u8&'
	code,message=subprocess.getstatusoutput(command)
	if code==0:
		print(ipaddr+"开启转码成功")

def check_ip(ipaddr):
	command='ping -s 1000 -c 3 '+ipaddr
	a,b=subprocess.getstatusoutput(command)
	if '100% packet loss' in b:
		return False
	else:
		return True
def check_dir(ipaddr):
	flag=0
	for i in os.listdir():
		if i==ipaddr:
			flag=1
			break
	if flag==0:
		return False
	else:
		return True

def conn_mysql():
	conn=pymysql.connect(host='192.168.1.1',user='root',password='123456',db='ipcamera')
	cursor=conn.cursor()
	sql='select FName,FAddr,FSsrcURL from c4sm_ssrc where FRegionCode=10001'
	cursor.execute(sql)
	results=cursor.fetchall()
	conn.close()
	#print(results)
	return results

if __name__ == '__main__':
	main()

#!/usr/bin/env python
#coding=utf-8
from fabric.api import *
from fabric.context_managers import *
from fabric.contrib.console import confirm
from fabric.colors import red, green
from fabric.contrib.files import append
from fabric.utils import abort,error,warn,puts
import datetime,time

'''env.hosts = ['10.1.200.80','10.1.200.82']'''
'''env.exclude_hosts=['10.1.200.80']'''
env.password='lafaso@root2011'
env.command_timeout=180
env.timeout=3
env.connection_attempts=3


resin_home='/opt/priceimg/'
src_home='/opt/priceimg/generateImage/'
java_file_home='/opt/priceimg/generateImage/src/'
jsp_file_home='/opt/priceimg/generateImage/web/'
resin_shell='sh resin_price.sh'
checkstat_url="curl 'http://127.0.0.1:8091/generateImage/image/isLive.html'"
nginx_home='/opt/nginx-1.2.7'
nginx_restart=nginx_home+"/sbin/nginx -c "+nginx_home+"/conf/nginx.conf -s reload"
nginx_start=nginx_home+"/sbin/nginx -c "+nginx_home+"/conf/nginx.conf"
nginx_stop=nginx_home+"/sbin/nginx -s stop"

def runcommand(command):
    output=run(command)
    print output

def nginxrestart(command=nginx_restart):
    runcommand(command)

def nginxstop(command=nginx_stop):
    runcommand(command)

def nginxstart(command=nginx_start):
    runcommand(command)
	 
def codeupdate():
     with cd(src_home):
		output=run('svn up')
		print output
	 
def codecompile():
     with cd(resin_home):
     	output=run('sh antshell.sh')
        print("Executing on %s as %s" % (env.host, env.user))
        if output.find('BUILD SUCCESSFUL')!=-1:
            print 'antshell run successed!'
	    return True
        else:
			return False

def resinrestart():
    running=True
    count=0
    with cd(resin_home):
    	output=run(resin_shell)
    	print output
    time.sleep(10)
    while running:
	result=checkappstat()
        if result==True:
             running=False
             break
        else:
	    count+=10
	    if count>30:
		break
	    else:
		time.sleep(10)
    if count > 180:	
    	abort('checkappstat outtime 30s!')
	 
def checkappstat():
    output=run(checkstat_url)
    print("Executing on %s as %s" % (env.host, env.user))
    if output.strip()=='live!':
       print 'the resin has been started'
       return True
    else:
       print 'the resin failed to start'
       return false

def deploy():
     result=confirm("Dou you want to do this?")
     if result==True:
     	codeupdate()
	result=codecompile()
	if result == True:
		resinrestart()

@hosts('10.1.200.80')
def deploysingle():
     result=confirm("Dou you want to do this?")
     if result==True:
     	codeupdate()
	result=codecompile()
	if result == True:
		resinrestart()

@parallel(4)
def deployall():
     print(green("This parallel tasks are starting!"))
     with hide('running','stdout'):
     	codeupdate()
     	result=codecompile()
	if result == True:
		resinrestart()

@hosts('10.1.200.80')
def scptarcode():
    now=datetime.date.today()
    current_date=now.strftime('%Y%m%d')
    source_code_dir='product_code_'+current_date
    with cd('/opt/lafaso_product_web2'):
        run('svn co svn://192.168.0.6/lafaso_product/trunk '+source_code_dir)
        run('sh scptarcode.sh')

def uploadfileremote():
    now=datetime.date.today()
    current_date=now.strftime('%Y%m%d')
    source_code_dir='product_code_'+current_date
    put('/opt/lafaso_product_web2/'+source_code_dir+'.tar.gz','/opt/product_code/')
    with cd('/opt/product_code'):
        run('tar -zxvf '+source_code_dir+'.tar.gz')

@hosts('10.1.200.80')
def operateshell():
    while True:
       a = raw_input('Enter your words: ')
       if a == 'stop':
           break
       with cd('/opt/lafaso_product_web/'):
           run(a)

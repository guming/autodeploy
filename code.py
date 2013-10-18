import web,hashlib,ConfigParser
import commands
urls = (
'/', 'index',
'/login', 'login',
'/dodeploy','dodeploy'
)
cf = ConfigParser.ConfigParser()
cf.read("deploy.ini")
s = cf.sections()
user=cf.get("user", "uname")
md5_passwd=cf.get("user","upasswd")
servers_ip=cf.get("servers","ip")
slist=servers_ip.split(",")
for s in slist:
    print s
render = web.template.render('templates/')
class index:
    def GET(self):
        print "Hello, world!"
        return render.login()

class login:
    def POST(self):
        i = web.input()
        print i.username
        print i.password
        passwd=hashlib.md5(str(i.password)).hexdigest()
        print passwd
        if i.username!= user:
            return render.login()
        if passwd!= md5_passwd:
            return render.login()      
        return render.view(slist)

class dodeploy:
    def POST(self):
        i = web.input()
        print i.svalues
        print i.svalues.split(",")
        commands.getoutput("fab --hosts='"+i.svalues+"' -f autodeploy.py runcommand:command='free -m' > log.txt ")
        flog=open("log.txt","r")
        return render.viewlog(flog,"")

if __name__ == "__main__": 
    app=web.application(urls, globals())
    app.run()

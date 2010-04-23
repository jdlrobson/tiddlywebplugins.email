from tiddlyweb.config import config
import poplib
import smtplib
import time
from tiddlywebplugins import email as mailer
import email as emailpy
from tiddlyweb.commands import make_command

def pop_send_mail(email):
  try:
    smtp = config['mailer']['smtp']
    user = config['mailer']['username']
    password = config['mailer']['password']
  except KeyError:
    print "please add {mailer:'smtp':'','user':'','password':''} to your config file"
    return
  s=smtplib.SMTP()
  s.connect(smtp)
  s.login(user,password)
  s.sendmail(email["from"],email["to"],"%s\n\n%s"%(email["subject"],email["body"]))
  print "sent a mail"
  s.quit()
  pass

def determine_bag(emailAddress):
  return "email"

mailer.send_email = pop_send_mail
mailer.determine_bag = determine_bag

@make_command()
def mail_agent(args):
  print "booting up mail agent"
  pigscantfly = True
  try:
    settings = config['mailer']
  except KeyError:
    print "mail agent failed to start: add to your config 'mailer':{'host':'','username':'','password':''}"
    return
  server =settings["pop"]
  user =settings["username"]
  password =settings["password"]

  while pigscantfly:
    print "logging %s into %s"%(user,server)
    try:
      session = poplib.POP3(server)
      session.user(user)
      session.pass_(password)
    except Exception,e:
      print "failed to start mail agent. Will try again in 30s."
      time.sleep(5)
      return mail_agent(args)
    print "logged into mail agent"
    numMessages = len(session.list()[1])
    print "there are %s new messages"%numMessages
    for i in range(1,numMessages+1):
      print "ooohh a message!! :D :D :D"
      raw_email = session.retr(i)[1]
      email_string = ""
      for el in raw_email:
        email_string += el
        email_string += "\n"
      msg = emailpy.message_from_string(email_string)
      email = {"from":msg["From"],"to":msg["To"],"subject":msg["Subject"]}
      body = msg.get_payload()
      if type(body) == type([]):
        body = body[0].as_string()
      try:
        body.index("\n\n")
        body = body[body.index("\n\n"):] 
      except ValueError:
        body = body
      email["body"]=  body
      try:
        mailer.handle_email(email)
        session.dele(i)
      except Exception,e:
        print "error %s"%e
      pass
    session.quit()
    print "sleeping for a bit"
    time.sleep(10)

def init(configin):
  global config
  config = configin
  pass
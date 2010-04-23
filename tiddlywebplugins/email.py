"""
TODO: add in policy checking and mapping email addresses to users
"""
from tiddlyweb.commands import make_command
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
import logging
from tiddlyweb import control
from tiddlywebplugins.utils import get_store
from tiddlyweb.store import Store,NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.config import config
import feedparser
import datetime
DEFAULT_SUBSCRIPTION = "daily"

@make_command()
def parse_input(raw):
  """
  entry point from mail server
  
  twanager parse_input <raw email from server here>
  
  take a raw email input and turn it into something we can operate on
  """
  """
  email = email_object_function(raw)
  email_to_send = handle_email(email)
  smtp.send(email_to_send)
  """
  
def determine_bag(emailAddress):
  handle,host = emailAddress.split("@")
  host_bits=  host.split(".")
  return "%s_private"%host_bits[0]

def get_subscriptions_bag(store):
  subscription_bag = "subscriptions.%s"%DEFAULT_SUBSCRIPTION
  try:
    store.get(Bag(subscription_bag))
  except NoBagError:
    store.put(Bag(subscription_bag))
  return subscription_bag
  
def delete_subscription(email):
  store = get_store(config)
  recipe = determine_bag(email["to"])
  fromAddress = email["from"]  
  subscription_bag= get_subscriptions_bag(store)
  
  try:
    subscribers_tiddler = store.get(Tiddler("/recipes/%s/tiddlers"%recipe,subscription_bag))
    subscriber_emails = subscribers_tiddler.text.splitlines()
    new_subscriber_emails = []
    for i in subscriber_emails:
      if i != fromAddress:
        new_subscriber_emails.append(i)
    subscribers_tiddler.text = "\n".join(new_subscriber_emails)
    store.put(subscribers_tiddler)
  except NoTiddlerError:
    pass
    
      
def make_subscription(email):
  store = get_store(config)
  recipe = determine_bag(email["to"])
  fromAddress = email["from"]
  subscription_bag= get_subscriptions_bag(store)
  subscribers_tiddler = Tiddler("/recipes/%s/tiddlers"%recipe,subscription_bag)
  try:
    subscribers_tiddler = store.get(subscribers_tiddler)
    subscriber_emails = subscribers_tiddler.text.splitlines()
    if fromAddress not in subscriber_emails:
      subscriber_emails.append(fromAddress)
    subscribers_tiddler.text = "\n".join(subscriber_emails)
    store.put(subscribers_tiddler)
  except NoTiddlerError:
    subscribers_tiddler.text = fromAddress 
    store.put(subscribers_tiddler)

def get_host(atomurl):
  resource = atomurl.split("/")[2]
  resource = resource.replace("_private","")
  return "%s.tiddlyspace.com"%resource
  
def make_digest_email(tiddler,environ={}):
  mail_to_send = False
  email_addresses = tiddler.text.splitlines()
  url_suffix = tiddler.title +".atom"
  today = datetime.date.today()
  now = today.strftime("%Y%m%d000000")
  try:
    before = tiddler.fields["last_generated"]
  except KeyError:
    before = "19000220000000" #select a date wayyyyy in the past
  qs = "?select=modified:>%s&select=modified:<%s"%(before,now) #filter just the changes
  try:
    host_details = environ["tiddlyweb.config"]["server_host"]
    try:
      scheme = host_details["scheme"]+"://"
      if scheme == 'file://':
        qs = ""
        scheme = ''
    except KeyError:
      scheme=""
    try:
      host = host_details["host"]
    except KeyError:
      host=""
    try:
      port =  ":"+host_details["port"]
    except KeyError:
      port =""
  except KeyError:
    host = ""
    scheme = ""
    port = ""
  feed_url ="%s%s%s%s%s"%(scheme,host,port,url_suffix,qs)
  feed = feedparser.parse(feed_url)  
  entries = feed.entries
  subject = "Email Digest: %s"%feed['feed']['title']
  if len(entries) == 0:
    return False
  body = u"<html>"
  for entry in entries:
    body += u'<div><a href="%s">%s</a>%s</div>'%(entry['link'],entry['title'],entry['summary'])
  body += u"</html>"
  mail_to_send = {"bcc":email_addresses,"subject":subject,"body":body,"from":"subscriptions@%s"%get_host(tiddler.title)}
  tiddler.fields['last_generated'] = "20100101010101"#add timestamp
  return mail_to_send
  
@make_command()
def make_digest(args):
  bag = args[0]
  bag = store.get(Bag(bag))
  for tiddler in bag.list_tiddlers():
    mail = make_digest_email(tiddler)
    send_email(mail)
  
def retrieve_from_store(email):
    """
    get the tiddler requested by the email from the store 
    and return it as an email
    """
    store = get_store(config)
    tiddler = Tiddler(email['subject'])
    bag = determine_bag(email['to'])
    tiddler.bag = bag
    
    try:
        tiddler = store.get(tiddler)
        response_text = tiddler.text
    except NoTiddlerError:
        #Tiddler not found. Return a list of all tiddlers
        bag = Bag(bag)
        bag = store.get(bag)
        response_text = 'The following tiddlers are in %s:\n' % email['to'].split('@')[1]
        tiddlers = bag.gen_tiddlers()
        tiddlers = [tiddler for tiddler in tiddlers]
        response_text += '\n'.join([tiddler.title for tiddler in tiddlers])

    response_email = {
        'from': email['to'],
        'to': email['from'],
        'subject': tiddler.title,
        'body': response_text
    }
    
    return response_email
  
def put_to_store(email):
  '''
  email is put into store
  '''
  pass

def get_action(email):
  to = email["to"].split("@")
  return to[0]
  
def handle_email(email):
  '''
  Takes an email and figures out what to do with it
  '''
  action = get_action(email)
  if action == 'view':
    return retrieve_from_store(email)
  elif action =='post':
    return put_to_store(email)
  elif action =='subscribe':
    return make_subscription(email)
  elif action =='unsubscribe':
    return delete_subscription(email)

def send_email(mail):
  print "i dont know how to send email yet"
  pass

def init(config_in):
    """
    initialise email module
    """
    global config
    config = config_in

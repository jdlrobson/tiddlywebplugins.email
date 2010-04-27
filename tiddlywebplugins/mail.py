"""
TODO: add in policy checking and mapping email addresses to users
"""
import re
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

class EmailAddressError(Exception):
    pass

def determine_bag(emailAddress):
  """
  temporary function to map email address to bag name
  
  TODO - replace with a proper mapping function
       - add support for choice between recipes and bags
  """
  handle, host = emailAddress.split("@")
  host_bits = host.split(".")
  return "%s_private" % host_bits[0]

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
    subscribers_tiddler = store.get(Tiddler("bags/%s/tiddlers"%recipe,subscription_bag))
    subscriber_emails = subscribers_tiddler.text.splitlines()
    new_subscriber_emails = []
    for i in subscriber_emails:
      if i != fromAddress:
        new_subscriber_emails.append(i)
    subscribers_tiddler.text = "\n".join(new_subscriber_emails)
    store.put(subscribers_tiddler)
  except NoTiddlerError:
    pass
  
  return {"from":email["to"],"to":email["from"],"subject":"You have been unsubscribed to %s"%recipe,"body":"Harry the dog is currently whining in sadness."}
  
      
def make_subscription(email):
  store = get_store(config)
  recipe = determine_bag(email["to"])
  fromAddress = email["from"]
  subscription_bag= get_subscriptions_bag(store)
  subscribers_tiddler = Tiddler("bags/%s/tiddlers"%recipe,subscription_bag)
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
    
  return {"from":email["to"],"to":email["from"],"subject":"You have subscribed to %s"%recipe,"body":"You will now receive daily digests. To unsubscribe please email unsubscribe@%s"}

def get_email_host(atomurl,env=False):
  resource = atomurl.split("/")[1]
  try:
    host = env["server_host"]["host"]
    scheme = env["server_host"]["scheme"]
  except KeyError:
    host = ""
    scheme = ""
  
  if scheme == 'file':
    host = "tiddlyspace.com"
  if host[0:4] =="www.":
    host = host[4:]
  resource = resource.replace("_private","")
  resource = resource.replace("_public","")
  return "%s.%s"%(resource,host)
  
def make_digest_email(tiddler,environ={}):
  mail_to_send = False
  email_addresses = tiddler.text.splitlines()
  url_suffix = tiddler.title +".atom"
  now = datetime.datetime.now()
  nowstr = now.strftime("%Y%m%d%H%M%S")
  try:
    before = tiddler.fields["last_generated"]
  except KeyError:
    before = "19000220000000" #select a date wayyyyy in the past
  qs = "?select=modified:>%s"%(before) #filter just the changes
  try:
    prefix = config["server_prefix"]
  except KeyError:
    prefix = ""
  try:
    host_details = config["server_host"]
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
  base_feed_url= "%s%s%s%s/%s"%(scheme,host,port,prefix,url_suffix)
  feed_url ="%s%s"%(base_feed_url,qs)
  print feed_url
  feed = feedparser.parse(feed_url)  
  entries = feed.entries
  if len(entries) == 0:
    print "no activity on this feed"
    return False
    
  subject = "Email Digest: %s"%feed['feed']['title']
  htmlbody = u'<html><div>note you can <a href="%s">subscribe to this feed via atom feed</a></div>'%base_feed_url
  body = u'''note you can subscribe to this feed via atom feed <%s>

'''%base_feed_url
  for entry in entries:
    if "summary" not in entry:
      entry["summary"] = ""
    if "title" not in entry:
      entry["title"] = ""
    if "link" not in entry:
      entry["link"] = ""
    body += '''%s <%s>
%s

'''%(entry['title'],entry['link'],entry['summary'])
    htmlbody += u'<div><a href="%s"><h1>%s</h1></a>%s</div>'%(entry['link'],entry['title'],entry['summary'])
  htmlbody += u'</html>'

  if email_addresses:
    mail_to_send = {"bcc":email_addresses,"subject":subject,"body":body,"bodyhtml":htmlbody,"from":"ben.gillies@bt.com"}
  else:
    mail_to_send = False
  
  tiddler.fields['last_generated'] = nowstr#add timestamp
  store = get_store(config)
  store.put(tiddler)
  return mail_to_send
  
@make_command()
def make_digest(args):
  """
  make_digest subscriptions.daily
  """
  bag = args[0]
  store= get_store(config)
  bag = store.get(Bag(bag))
  for tiddler in bag.list_tiddlers():
    tiddler = store.get(tiddler)
    mail = make_digest_email(tiddler)
    if mail:
      send_email(mail)

def clean_subject(subject):
    """
    remove RE: and FWD: from the subject
    """
    regex = '^(?:(?:RE\: ?)|(?:FWD: ?))+'
    return re.sub(regex, '', subject)

def retrieve_from_store(email):
    """
    get the tiddler requested by the email from the store 
    and return it as an email
    """
    store = get_store(config)
    tiddler_title = clean_subject(email['subject'])
    tiddler = Tiddler(tiddler_title)
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
    """
    email is put into store
    """
    store = get_store(config)
    tiddler = Tiddler(email['subject'])
    tiddler.bag = determine_bag(email['to'])
    tiddler.text = email['body']
    toTags, toBase = email['to'].split('@')
    tiddler.tags = toTags.split('+')
    tiddler.tags.remove('post')
    store.put(tiddler)

    response_email = {
        'from': 'view@%s' % toBase,
        'to': email['from'],
        'subject': tiddler.title,
        'body': tiddler.text
    }

    return response_email

def get_action(to):
    """
    determine whether we are posting, viewing or subscribing
    """
    if(type(to) == type({})):
      to = to["to"]
      
    def matcher(m):
      return m.group(1)
    to = re.sub("[^\<]*\<([^\>]+)\>",matcher,to)
    first_part = to.split("@", 1)[0]
    return first_part.split('+', 1)[0]
  
def handle_email(email):
    """
    Takes an email and figures out what to do with it
    """
    action = {
        'view': retrieve_from_store,
        'post': put_to_store,
        'subscribe': make_subscription,
        'unsubscribe': delete_subscription
    }

    try:
        response_email = action[get_action(email['to'])](email)
    except KeyError:
        raise EmailAddressError('Unsupported email address %s' % email['to'])
    
    send_email(response_email)
    return response_email

def send_email(mail):
  print "i dont know how to send email yet. please implement send_email"
  pass

def init(config_in):
    """
    initialise email module
    """
    global config
    config = config_in

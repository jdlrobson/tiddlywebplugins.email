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

DEFAULT_SUBSCRIPTION = "daily"

class EmailAddressError(Exception):
    pass

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
    print "xhere"
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

    return response_email

def init(config_in):
    """
    initialise email module
    """
    global config
    config = config_in

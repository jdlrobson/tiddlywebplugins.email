from tiddlywebplugins import email as mailer
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
import logging,os
from tiddlyweb import control
from tiddlywebplugins.utils import get_store
from tiddlyweb.store import Store,NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.config import config
from test import setup

def setup_module(module):
  module.store = Store(config['server_store'][0], config['server_store'][1],environ={'tiddlyweb.config': config})
  module.environ = {'tiddlyweb.store':module.store,'tiddlyweb.config': config}
  module.environ["tiddlyweb.config"]["server_host"]={"scheme":"file","host":"%s"%os.getcwd()}
  module.environ["tiddlyweb.config"]["server_prefix"] = "/test"
def test_subscribe():
  #setup
  setup(store)
  empty =Tiddler("recipes/osmosoft_private/empty","subscriptions.daily")
  empty.text = '''jon.robson@bt.com
  fnd@osmosoft.com
  '''
  store.put(empty)
  
  #run
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"bengillies@gmail.com","subject":"","body":""})
  
  #verify
  tid = store.get(Tiddler("recipes/osmosoft_private/tiddlers","subscriptions.daily"))
  assert tid.text == "bengillies@gmail.com"
 
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"jeremy@osmosoft.com","subject":"","body":""})
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"jdlr@osmosoft.com","subject":"","body":""})
    
  tid = store.get(Tiddler("recipes/osmosoft_private/tiddlers","subscriptions.daily"))
  lines = tid.text.splitlines()
  assert len(lines) == 3
  for i in [u"bengillies@gmail.com",u"jeremy@osmosoft.com",u"jdlr@osmosoft.com"]:
    assert i in lines
    
  email = mailer.handle_email({"to":"unsubscribe@osmosoft.tiddlyspace.com","from":"jdlr@osmosoft.com","subject":"","body":""})
  email = mailer.handle_email({"to":"unsubscribe@osmosoft.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"","body":""})
  tid = store.get(Tiddler("recipes/osmosoft_private/tiddlers","subscriptions.daily"))
  lines = tid.text.splitlines()
  email = mailer.make_digest_email(tid,environ)
  bcc = email["bcc"]
  assert len(bcc) == 2
  assert len(lines) == 2
  assert email["from"] == 'subscriptions@osmosoft.tiddlyspace.com'
  for i in [u"bengillies@gmail.com",u"jeremy@osmosoft.com"]:
    assert i in lines
    assert i in bcc

  assert email['subject'] == u"Email Digest: Tiddlers in bag for testing purposes"
  tid = store.get(tid)
  assert 'last_generated' in tid.fields
  
  from tiddlywebplugins import email as dummymailer
  global totalsent 
  totalsent= 0
  def new_sendmail(email):
    global totalsent
    print "sending as part of make_digest_email test"
    totalsent += 1
  dummymailer.send_email = new_sendmail
  dummymailer.make_digest(["subscriptions.daily"])
  assert totalsent is 1 #one email is sent with all the email addresses blind carbon copied. osmosoft_private/empty is empty so wont cause emails
  
  email= mailer.make_digest_email(store.get(Tiddler("recipes/osmosoft_private/empty","subscriptions.daily")),environ) #now since there was no changes to the store you would expect no email
  assert email is False
  
  
'''
emailing subscriptions@osmosoft.tiddlyspace.com gives you details on how you can subscribe/unsubscribe
open for discussion

if i subscribe to a feed how do i confirm my email?
if i confirm my email for one feed do i need to confirm it for all other feeds?
can other users subscribe me to spaces?
subscribing to tags or fields
subscribe-weekly@osmosoft.tiddlyspace.com #subscribe weekly rather then daily
subscribe@osmosoft.tiddlyspace.com  {subject: <tiddler.title>,text:"weekly"} #subscribe to a weekly digest of <tiddler.title>
'''
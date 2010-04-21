from tiddlywebplugins import email as mailer
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
import logging
from tiddlyweb import control
from tiddlywebplugins.utils import get_store
from tiddlyweb.store import Store,NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.config import config
from test import setup

def setup_module(module):
  module.store = Store(config['server_store'][0], config['server_store'][1],environ={'tiddlyweb.config': config})
  module.environ = {'tiddlyweb.store':module.store,'tiddlyweb.config': config}

def test_subscribe():
  #setup
  setup(store)
  
  #run
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"bengillies@gmail.com","subject":"","body":""})
  
  #verify
  tid = store.get(Tiddler("/recipes/osmosoft_private/tiddlers.atom","subscriptions.daily"))
  assert tid.text == "bengillies@gmail.com"
 
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"jeremy@osmosoft.com","subject":"","body":""})
  email = mailer.handle_email({"to":"subscribe@osmosoft.tiddlyspace.com","from":"jdlr@osmosoft.com","subject":"","body":""})
  
  tid = store.get(Tiddler("/recipes/osmosoft_private/tiddlers.atom","subscriptions.daily"))
  lines = tid.text.splitlines()
  assert len(lines) == 3
  for i in [u"bengillies@gmail.com",u"jeremy@osmosoft.com",u"jdlr@osmosoft.com"]:
    assert i in lines
    
  email = mailer.handle_email({"to":"unsubscribe@osmosoft.tiddlyspace.com","from":"jdlr@osmosoft.com","subject":"","body":""})
  email = mailer.handle_email({"to":"unsubscribe@osmosoft.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"","body":""})
  tid = store.get(Tiddler("/recipes/osmosoft_private/tiddlers.atom","subscriptions.daily"))
  lines = tid.text.splitlines()
  assert len(lines) == 2
  for i in [u"bengillies@gmail.com",u"jeremy@osmosoft.com"]:
    assert i in lines
    

'''
open for discussion
subscribing to tags or fields
subscribe-weekly@osmosoft.tiddlyspace.com #subscribe weekly rather then daily
subscribe@osmosoft.tiddlyspace.com  {subject: <tiddler.title>,text:"weekly"} #subscribe to a weekly digest of <tiddler.title>
'''
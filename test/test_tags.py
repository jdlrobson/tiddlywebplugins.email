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

def test_posting_of_tags_via_email_address():  
  #setup
  setup(store)
  tid =Tiddler("Hey there","ben_private")
  tid.tags = ["rainbows","colourful"]
  store.put(tid)
  #run
  mailer.handle_email({"to":"post+foo+bar+baz@ben.tiddlyspace.com","subject":"Hey there","body":"tiddler text"})
  
  #verify
  tid = store.get(tid)
  assert tid.tags == ["rainbows","colourful","foo","bar","baz"]
  
def test_posting_of_tags_via_tag_address():
  #setup
  setup(store)
  tid =Tiddler("GettingStarted","jon_private")
  tid.tags = ["z"]
  store.put(tid)
  
  #run
  mailer.handle_email({"to":"tags@jon.tiddlyspace.com","subject":"GettingStarted","body":"foo,bar,baz"})
  
  #verify
  tiddler = store.get(tid)
  assert tiddler.tags == ["z","foo","bar","baz"]
  
  #run
  mailer.handle_email({"to":"tags@jon.tiddlyspace.com","subject":"GettingStarted","body":"[[tiddlyweb fun]] [[tiddlytastical, commas]] tiddlywiki fun"})
  
  #verify
  tiddler = store.get(tid)
  assert tiddler.tags == ["z","foo","bar","baz","tiddlyweb fun","tiddlytastical, commas","tiddlywiki","fun"]

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

def test_view():
  #setup
  setup(store)
  tid = Tiddler("GettingStarted","jon_private")
  tid.text= "the cat jumped over the moon"
  tid.tags = ["hello","world"]
  store.put(tid)
  
  #run
  email = mailer.handle_email({"to":"view@jon.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"GettingStarted","body":""})
  
  #verify
  assert email == {"to":"jdlrobson@gmail.com","from":"view@jon.tiddlyspace.com","subject":"GettingStarted","body":"the cat jumped over the moon"}
  
    
def test_view_tiddlers():
  #setup
  setup(store)
  tid = Tiddler("one","jon_private")
  store.put(tid)
  tid = Tiddler("two","jon_private")
  store.put(tid)
  tid = Tiddler("three","jon_private")
  store.put(tid)
  tid = Tiddler("four","jon_private")
  store.put(tid)
  
  #run
  email = mailer.handle_email({"to":"view@jon.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"","body":""})
  #verify
  assert email["to"] == "jdlrobson@gmail.com"
  body = email['body'].splitlines()
  assert body.pop(0) == 'The following tiddlers are in jon.tiddlyspace.com:'
  assert len(body) == 4
  for tiddler_name in body:
      assert tiddler_name in ['one','two','three','four']


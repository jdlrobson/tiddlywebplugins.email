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

def test_post_new():
  #setup
  setup(store)
  
  #run
  email = mailer.handle_email({"to":"post@jon.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"Jons brand spanking new tiddler","body":"i love email tiddlyweb"})
  
  #verify  
  try:
    tid = store.get(Tiddler("Jons brand spanking new tiddler","jon_private"))
  except NoTiddlerError:
    assert False == True
  assert tid.text == 'i love email tiddlyweb'
  assert tid.tags == []
  
  assert email["from"] == 'view@jon.tiddlyspace.com'
  assert email["to"] == 'jdlrobson@gmail.com'
  assert email["subject"] == 'Jons brand spanking new tiddler'
  
  tid.text = "I love email tiddlyweb."
  store.put(tid)
  
  reply = {"subject":"RE: Jons brand spanking new tiddler","from":"jdlrobson@gmail.com","to":"view@jon.tiddlyspace.com","body":"thanks tiddlyweb!"}
  email = mailer.handle_email(reply)
  assert email == {"body":"I love email tiddlyweb.","to":"jdlrobson@gmail.com","from":"view@jon.tiddlyspace.com","subject":"Jons brand spanking new tiddler"}

def test_post_existing():
  #setup
  setup(store)
  tid = Tiddler("i exist","ben")
  tid.fields['geo.lat'] = u"20"
  tid.fields['geo.long'] = u"2"
  tid.text = "data"
  tid.tags= ["a","b"]
  store.put(tid)
  #run
  email = mailer.handle_email({"to":"post@ben.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"i exist","body":"wipeout"})

  #verify  
  tid = store.get(Tiddler("i exist","jon_private"))
  assert tid.text == "wipeout"
  assert tid.fields['geo.lat'] == u"20"
  
  
def test_post_advanced(): #the body is how tiddlers are stored in textual representation
  #setup
  setup(store)
  
  #run
  advancedBody = '''
  tags: foo bar [[jon tag with spaces]]
  foo: val
  
  my text
  '''
  email = mailer.handle_email({"to":"post@jon.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"test","body":advancedBody})
  
  #verify  
  try:
    tid = store.get(Tiddler("test","jon_private"))
  except NoTiddlerError:
    assert False == True
  assert tid.text == ',my text'
  assert tid.tags == ["foo","bar","jon tag with spaces"]


def test_post_advanced_existing(): #the body is how tiddlers are stored in textual representation
  #setup
  setup(store)
  tid = Tiddler("test","jon_private")
  tid.tag = ["foo"]
  tid.text = "hello world"
  tid.fields['foo'] = 'bar'
  tid.fields['bar'] = 'baz'
  store.put(tid)
  
  advancedBody = '''
  tags: foo bar [[jon tag with spaces]]
  foo: val

  my text
  '''
  #run
  email = mailer.handle_email({"to":"post@jon.tiddlyspace.com","from":"jdlrobson@gmail.com","subject":"test","body":advancedBody})

  #verify  
  try:
    tid = store.get(Tiddler("test","jon_private"))
  except NoTiddlerError:
    assert False == True
  assert tid.text == ',my text'
  assert tid.tags == ["foo","bar","jon tag with spaces"]
  assert tid.fields['foo'] == 'val'
  assert "bar" not in tiddler.fields
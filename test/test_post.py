"""
Tests for interfacing using the post@... email address
"""
from test import setup
from tiddlywebplugins import mail as mailer

from tiddlyweb.model.tiddler import Tiddler 
from tiddlyweb.config import config
from tiddlyweb.store import NoTiddlerError

from tiddlywebplugins.utils import get_store

def setup_module(module): 
    module.store = get_store(config)
    module.environ = {
        'tiddlyweb.store': module.store,
        'tiddlyweb.config': config
    }

def test_post_new():
    """
    testing posting a new tiddler to tiddlyweb via email
    and that a reply to the response doesn't overwrite that tiddler
    """
    #setup
    setup(store)

    #run
    email = mailer.handle_email({
        'to': 'post@jon.tiddlyspace.com',
        'from': 'jdlrobson@gmail.com',
        'subject': 'Jons brand spanking new tiddler',
        'body': 'I love email tiddlyweb'
    })

    #verify  
    try:
        tiddler = Tiddler('Jons brand spanking new tiddler', 'jon_private')
        tiddler = store.get(tiddler)
    except NoTiddlerError:
        raise AssertionError('Tiddler has not been put into store')
    
    assert tiddler.text == 'I love email tiddlyweb'
    assert tiddler.tags == []
    
    assert email['from'] == 'view@jon.tiddlyspace.com'
    assert email['to'] == 'jdlrobson@gmail.com'
    assert email['subject'] == 'Jons brand spanking new tiddler'
    
    #check a reply doesn't overwrite the tiddler
    reply = {
        'subject': 'RE: Jons brand spanking new tiddler',
        'from': 'jdlrobson@gmail.com',
        'to': 'view@jon.tiddlyspace.com',
        'body': 'thanks tiddlyweb!'
    }
    
    #run
    email = mailer.handle_email(reply)
    
    #verify
    tiddler = Tiddler('Jons brand spanking new tiddler', 'jon_private')
    tiddler = store.get(tiddler)
    
    assert tiddler.text == 'I love email tiddlyweb'
    
    assert email == {
        'body': 'I love email tiddlyweb',
        'to': 'jdlrobson@gmail.com',
        'from': 'view@jon.tiddlyspace.com',
        'subject': 'Jons brand spanking new tiddler'
    }

def test_post_existing():
    """
    testing posting an existing tiddler to check that it is overwritten
    """
    #setup
    setup(store)
    tiddler = Tiddler('i exist','jon_private')
    tiddler.fields['geo.lat'] = '20'
    tiddler.fields['geo.long'] = '2'
    tiddler.text = 'data'
    tiddler.tags = ['a', 'b']
    store.put(tiddler)
    
    #run
    mailer.handle_email({
        'to': 'post@jon.tiddlyspace.com',
        'from': 'jdlrobson@gmail.com',
        'subject': 'i exist',
        'body': 'wipeout'
    })

    #verify  
    tiddler = store.get(Tiddler('i exist', 'jon_private'))
    assert tiddler.text == 'wipeout'
    assert tiddler.fields.get('geo.lat') == None
  
"""
#Test for a mechanism for allowing posting detailed tiddlers in future by advanced users
def test_post_advanced(): #the body is how tiddlers are stored in textual representation
  #setup
  setup(store)
  
  #run
  advancedBody = '''
  tags: foo bar [[jon tag with spaces]]
  foo: val
  
  my text
  '''
  email = mailer.handle_email({'to':'post@jon.tiddlyspace.com','from':'jdlrobson@gmail.com','subject':'test','body':advancedBody})
  
  #verify  
  try:
    tid = store.get(Tiddler('test','jon_private'))
  except NoTiddlerError:
    assert False == True
  assert tid.text == ',my text'
  assert tid.tags == ['foo','bar','jon tag with spaces']


def test_post_advanced_existing(): #the body is how tiddlers are stored in textual representation
  #setup
  setup(store)
  tid = Tiddler('test','jon_private')
  tid.tag = ['foo']
  tid.text = 'hello world'
  tid.fields['foo'] = 'bar'
  tid.fields['bar'] = 'baz'
  store.put(tid)
  
  advancedBody = '''
  tags: foo bar [[jon tag with spaces]]
  foo: val

  my text
  '''
  #run
  email = mailer.handle_email({'to':'post@jon.tiddlyspace.com','from':'jdlrobson@gmail.com','subject':'test','body':advancedBody})

  #verify  
  try:
    tid = store.get(Tiddler('test','jon_private'))
  except NoTiddlerError:
    assert False == True
  assert tid.text == ',my text'
  assert tid.tags == ['foo','bar','jon tag with spaces']
  assert tid.fields['foo'] == 'val'
  assert 'bar' not in tiddler.fields
"""
"""
Testing the inclusion of tags in email addresses
"""

from test import setup
from tiddlywebplugins import mail as mailer

from tiddlyweb.model.tiddler import Tiddler
from tiddlywebplugins.utils import get_store
from tiddlyweb.config import config

def setup_module(module): 
    module.store = get_store(config)
    module.environ = {
        'tiddlyweb.store': module.store,
        'tiddlyweb.config': config
    }

def test_posting_of_tags():
    """
    overwriting a tiddler with tags with a tiddler with
    a different set of tags via email
    """
    #setup
    setup(store)
    tiddler = Tiddler('Hey there', 'ben_private')
    tiddler.tags = ['rainbows', 'colourful']
    store.put(tiddler)

    #run
    mailer.handle_email({
        'to': 'post+foo+bar+baz@ben.tiddlyspace.com',
        'from': 'foo@bar.com',
        'subject': 'Hey there',
        'body': 'tiddler text'
    })

    #verify
    tiddler = Tiddler('Hey there', 'ben_private')
    tiddler = store.get(tiddler)
    assert tiddler.tags == ['foo', 'bar', 'baz']

"""
alternative tags implementation
def test_posting_of_tags_via_tag_address():
  #setup
  setup(store)
  tid =Tiddler('GettingStarted','jon_private')
  tid.tags = ['z']
  store.put(tid)
  
  #run
  mailer.handle_email({'to':'tags@jon.tiddlyspace.com','subject':'GettingStarted','body':'foo,bar,baz'})
  
  #verify
  tiddler = store.get(tid)
  assert tiddler.tags == ['z','foo','bar','baz']
  
  #run
  mailer.handle_email({'to':'tags@jon.tiddlyspace.com','subject':'GettingStarted','body':'[[tiddlyweb fun]] [[tiddlytastical, commas]] tiddlywiki fun'})
  
  #verify
  tiddler = store.get(tid)
  assert tiddler.tags == ['z','foo','bar','baz','tiddlyweb fun','tiddlytastical, commas','tiddlywiki','fun']
"""
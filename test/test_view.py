"""
Tests for interfacing using the view@... email address
"""
from test import setup
from tiddlywebplugins import email as mailer

from tiddlyweb.model.tiddler import Tiddler 
from tiddlyweb.config import config

from tiddlywebplugins.utils import get_store

def setup_module(module): 
    module.store = get_store(config)
    module.environ = {
        'tiddlyweb.store': module.store,
        'tiddlyweb.config': config
    }

def test_view():
    """
    test a request for viewing a single tiddler
    """
    #setup
    setup(store)
    tiddler = Tiddler('GettingStarted', 'jon_private')
    tiddler.text = 'the cat jumped over the moon'
    tiddler.tags = ['hello', 'world']
    store.put(tiddler)

    #run
    email = mailer.handle_email({
        'to': 'view@jon.tiddlyspace.com',
        'from': 'jdlrobson@gmail.com',
        'subject': 'GettingStarted',
        'body': ''
    })

    #verify
    assert email == {
        'to': 'jdlrobson@gmail.com',
        'from': 'view@jon.tiddlyspace.com',
        'subject': 'GettingStarted',
        'body': 'the cat jumped over the moon'
    }

def test_view_tiddlers():
    """
    test a request for viewing all tiddlers in a bag
    """
    #setup
    setup(store)
    tiddler = Tiddler('one', 'jon_private')
    store.put(tiddler)
    tiddler = Tiddler('two', 'jon_private')
    store.put(tiddler)
    tiddler = Tiddler('three', 'jon_private')
    store.put(tiddler)
    tiddler = Tiddler('four', 'jon_private')
    store.put(tiddler)

    #run
    email = mailer.handle_email({
        'to': 'view@jon.tiddlyspace.com',
        'from': 'jdlrobson@gmail.com',
        'subject': '',
        'body': ''
    })

    #verify
    assert email['to'] == 'jdlrobson@gmail.com'
    body = email['body'].splitlines()
    assert body.pop(0) == 'The following tiddlers are in jon.tiddlyspace.com:'
    assert len(body) == 4
    for tiddler_name in body: 
        assert tiddler_name in ['one', 'two', 'three', 'four']

def test_view_reply():
    """
    test a request for viewing based on a reply to a previous response
    ie - the subject has an RE: in it.
    """
    #setup
    setup(store)
    tiddler = Tiddler('GettingStarted', 'ben_private')
    tiddler.text = 'The quick brown fox jumped over the lazy dog'
    store.put(tiddler)
    
    #run
    email = mailer.handle_email({
        'to': 'view@ben.tiddlyspace.com',
        'from': 'bengillies@gmail.com',
        'subject': 'RE: GettingStarted',
        'body': ''
    })
    
    #verify
    assert email['to'] == 'bengillies@gmail.com'
    assert email['from'] == 'view@ben.tiddlyspace.com'
    assert email['subject'] == 'GettingStarted'
    assert email['body'] == 'The quick brown fox jumped over the lazy dog'
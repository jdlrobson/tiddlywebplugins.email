"""
set up functions required for tests
"""
from tiddlyweb.model.bag import Bag
from tiddlyweb.store import NoBagError


def setup(store):
    """
    setup a clean store
    """
    bags = [
        'jon_private',
        'ben_private',
        'osmosoft_private',
        'subscriptions.daily'
    ]
    
    for bag_name in bags:
        bag = Bag(bag_name)
        try:
            store.delete(bag)
        except NoBagError:
            pass
        store.put(bag)

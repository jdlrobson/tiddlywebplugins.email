from tiddlywebplugins import email as mailer
from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
import logging
from tiddlyweb import control
from tiddlywebplugins.utils import get_store
from tiddlyweb.store import Store,NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.config import config


def setup(store):
  #setup a clean store
  for bag_name in ["jon_private","ben_private","osmosoft_private"]:
    bag = Bag(bag_name)
    try:
      store.delete(bag)
    except NoBagError:
      pass
    store.put(bag)
  pass
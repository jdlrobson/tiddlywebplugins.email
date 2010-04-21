from tiddlyweb.model.bag import Bag
from tiddlyweb.model.tiddler import Tiddler
from tiddlyweb.model.recipe import Recipe
import logging
from tiddlyweb import control
from tiddlywebplugins.utils import get_store
from tiddlyweb.store import Store,NoTiddlerError, NoBagError, NoRecipeError
from tiddlyweb.config import config

def parse_input(raw):
  """
  entry point from mail server
  
  take a raw email input and turn it into something we can operate on
  """
  """
  email = email_object_function(raw)
  email_to_send = handle_email(email)
  smtp.send(email_to_send)
  """

def delete_subscription(email):
  pass
  
def make_subscription(email):
  pass

def retrieve_from_store(email):
  pass
  
def put_to_store(email):
  '''
  email is put into store
  '''
  pass

def get_action(email):
  to = email["to"].split("@")
  return to[0]
  
def handle_email(email):
  '''
  Takes an email and figures out what to do with it
  '''
  action = get_action(email)
  if action == 'view':
    return retrieve_from_store(email)
  elif action =='post':
    return put_to_store(email)
  elif action =='subscribe':
    return make_subscription(email)
  elif action =='unsubscribe':
    return delete_subscription(email)
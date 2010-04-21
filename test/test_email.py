from tiddlywebplugins import email as mailer

def test_get_action():
  action = mailer.get_action({"to":"view@jon.tiddlyspace.com"})
  assert action == 'view'
  
  action = mailer.get_action({"to":"post@jon.tiddlyspace.com"})
  assert action == 'post'
  
  action = mailer.get_action({"to":"subscribe@jon.tiddlyspace.com"})
  assert action == 'subscribe'
  
  action = mailer.get_action({"to":"unsubscribe@jon.tiddlyspace.com"})
  assert action == 'unsubscribe'
  
def test_determine_recipe():
  environ = {"tiddlyweb.config":{"server_host":{"host":"tiddlyspace.com"}}}
  bag= mailer.determine_recipe("view@jon.tiddlyspace.com")
  assert bag == 'jon_private'
  
  bag = mailer.determine_recipe("radeedadadadad@jeremy-user.tiddlyspace.com")
  assert bag == "jeremy-user_private"
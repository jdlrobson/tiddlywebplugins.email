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
  
def test_determine_bag():
    environ = {"tiddlyweb.config":{"server_host":{"host":"tiddlyspace.com"}}}
    bag= mailer.determine_bag("view@jon.tiddlyspace.com")
    assert bag == 'jon_private'

    bag = mailer.determine_bag("radeedadadadad@jeremy-user.tiddlyspace.com")
    assert bag == "jeremy-user_private"

def test_clean_subject():
    subject = 'RE: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo bar'
    
    subject = 'RE:[list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo bar'
    
    subject = 'FWD: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo bar'
    
    subject = 'FWD: RE: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo bar'
    
    subject = 'RE: FWD: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo bar'
    
    subject = 'RE: [list]Foo FWD: bar RE: '
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == '[list]Foo FWD: bar RE: '
    
    subject = 're: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == 're: [list]Foo bar'
    
    subject = 'fwd: [list]Foo bar'
    cleaned_subject = mailer.clean_subject(subject)
    assert cleaned_subject == 'fwd: [list]Foo bar'
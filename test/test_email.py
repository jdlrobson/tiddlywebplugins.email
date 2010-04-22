"""
test some helper functions
"""

from tiddlywebplugins import email as mailer

def test_get_action():
    """
    test extracting the intended action from the email address
    """
    action = mailer.get_action("view@jon.tiddlyspace.com")
    assert action == 'view'

    action = mailer.get_action("post@jon.tiddlyspace.com")
    assert action == 'post'

    action = mailer.get_action("subscribe@jon.tiddlyspace.com")
    assert action == 'subscribe'

    action = mailer.get_action("unsubscribe@jon.tiddlyspace.com")
    assert action == 'unsubscribe'
    
    action = mailer.get_action("post+tag1+tag2@jon.tiddlyspace.com")
    assert action == 'post'
  
def test_determine_bag():
    """
    test extracting the bag to be used from the email address
    
    NOTE - this will need to be updated when determine_bag is replaced
    """
    bag = mailer.determine_bag("view@jon.tiddlyspace.com")
    assert bag == 'jon_private'

    bag = mailer.determine_bag("radeedadadadad@jeremy-user.tiddlyspace.com")
    assert bag == "jeremy-user_private"

def test_clean_subject():
    """
    test that RE: and FWD: can be stripped successfully
    """
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
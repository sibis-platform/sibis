#!/usr/bin/env python

##
##  See COPYING file distributed along with the ncanda-data-integration package
##  for the copyright and license terms
##

# Mail-related stuff
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from sibispy import sibislogger as slog

class email:
    """ Class handling email communication with XNAT users and admin."""

    # Initialize class.
    def __init__(self, sibis_admin_email = None):
        self._sibis_admin_email = sibis_admin_email
        self._messages_by_user = dict()
        self._admin_messages = []
        
    # Add to the message building up for a specific user
    def add_user_message( self, uname, msg ):
        if uname not in self._messages_by_user:
            self._messages_by_user[uname] = [msg]
        else:
            self._messages_by_user[uname].append( msg )

    # Add to the message building up for the admin
    def add_admin_message( self, msg ):
        self._admin_messages.append( msg )

    # Send pre-formatted mail message 
    def send( self, subject, from_email, to_email, html ):
        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = ', '.join( to_email )

        # Record the MIME types of both parts - text/plain and text/html.
        text = ''
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
    
        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)
        msg.attach(part2)
    
        # Send the message via local SMTP server.
        s = smtplib.SMTP( self._smtp_server )
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail( from_email, to_email, msg.as_string() )
        
        # Send email also to sibis admin if defined
        if self._sibis_admin_email and to_email != self._sibis_admin_email : 
            s.sendmail( from_email, self._sibis_admin_email, msg.as_string() )

        s.quit()

    # Send mail to one user
    def mail_user( self,  user_email, admin_email, title, intro_text, prolog,  msglist ):
        problem_list = [ '<ol>' ]
        for m in msglist:
            problem_list.append( '<li>%s</li>' % m )
        problem_list.append( '</ol>' )
            
        # Create the body of the message (a plain-text and an HTML version).
        html = '<html>\n <head></head>\n <body>\n' + intro_text + '\n %s\n' % ('\n'.join( problem_list ) + prolog + '\n\
</p>\n\
</body>\n\
</html>' 
        self.send( title, admin_email, [ user_email ], html )

    # ----- Send summary mail to admin
    def mail_admin( self ):
        problem_list = []
        if len( self._messages_by_user ) > 0:
            problem_list.append( '<ul>' )
            for (uname,msglist) in self._messages_by_user.iteritems():
                problem_list.append( '<li>User: %s</li>' % uname )
                problem_list.append( '<ol>' )
                for m in msglist:
                    problem_list.append( '<li>%s</li>' % m )
                problem_list.append( '</ol>' )
            problem_list.append( '</ul>' )

        if len( self._admin_messages ) > 0:
            problem_list.append( '<ol>' )
            for m in self._admin_messages:
                problem_list.append( '<li>%s</li>' % m )
            problem_list.append( '</ol>' )            

        text = ''

        # Create the body of the message (a plain-text and an HTML version).
        html = '<html>\n\
<head></head>\n\
<body>\n\
We have detected the following problem(s) with data on <a href="%s">NCANDA XNAT image repository</a>:</br>\n\
%s\n\
</p>\n\
</body>\n\
</html>' % (self._site_url, '\n'.join( problem_list ))
    
        self.send( "%s XNAT problem update" % self._site_name, self._xnat_admin_email, [ self._xnat_admin_email ], html )

    def send_all( self ):
        # Run through list of messages by user
        if len( self._messages_by_user ):
            for (uname,msglist) in self._messages_by_user.iteritems():
                self.mail_user( uname, msglist )

        if len( self._messages_by_user ) or len( self._admin_messages ):
            self.mail_admin

    def dump_all( self ):
	print "USER MESSAGES:"
	print self._messages_by_user
	print "ADMIN_MESSAGES:"
	print self._admin_messages

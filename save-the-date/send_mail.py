#!/usr/bin/python

import base64
from email.mime.text import MIMEText
import hashlib
import httplib2
import sys
import uuid
import yaml

from apiclient import discovery
from oauth2client import client


_SUBJECT = 'Jen & Brett\'s Wedding: Save the Date'


def main():
  if len(sys.argv) != 3:
    print 'Usage: {} <token> <config>'.format(sys.argv[0])
    return 1

  creds = client.AccessTokenCredentials(sys.argv[1], 'bulk-emailer/1.0')
  http = creds.authorize(httplib2.Http())
  gmail_service = discovery.build('gmail', 'v1', http=http)
  batch = gmail_service.new_batch_http_request()

  with open('template.html', 'r') as tmpl_file:
    tmpl = tmpl_file.read()
    with open(sys.argv[2], 'r') as config_file:
      config = yaml.load(config_file)
      for id, recipient in enumerate(config['recipients']):
        el = '{}{:02}'.format(config['tracking_prefix'], id)
        el += base64.b32encode(hashlib.md5(el).digest())[:2]
        msg = MIMEText(tmpl.format(recipient=recipient['to'],
                                   we=config['we'],
                                   signature=config['signature'],
                                   cid=uuid.uuid4(),
                                   el=el),
                       'html')
        msg['subject'] = _SUBJECT
        msg['from'] = config['from']
        msg['to'] = recipient['email']
        if id == 0:
          print 'Sample:\n' + msg.as_string() + '\n\n'

        body = {'raw': base64.urlsafe_b64encode(msg.as_string())}
        print 'Adding {} ({})'.format(recipient['email'], el)
        batch.add(gmail_service.users().messages().send(userId=config['user_id'], body=body))

  try:
    batch.execute()
  except Exception as error:
    print 'An error has occurred: {}'.format(error)


if __name__ == '__main__':
  main()

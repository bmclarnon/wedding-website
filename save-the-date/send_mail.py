#!/usr/bin/python

import base64
from email.mime.text import MIMEText
import httplib2
import sys
import uuid
import yaml

from apiclient import discovery
from oauth2client import client


_SUBJECT = 'Save the Date: Aug 20, 2016'


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
        msg = MIMEText(tmpl.format(recipient=recipient['to'],
                                   we=config['we'],
                                   signature=config['from'],
                                   cid=uuid.uuid4(),
                                   el='{}{}'.format(config['tracking_prefix'], id)),
                       'html')
        msg['subject'] = _SUBJECT
        msg['from'] = config['from']
        msg['to'] = recipient['email']
        body = {'raw': base64.urlsafe_b64encode(msg.as_string())}
        print 'Adding {}'.format(recipient['email'])
        batch.add(gmail_service.users().messages().send(userId=config['user_id'], body=body))

  try:
    print batch.execute()
  except Exception as error:
    print 'An error has occurred: {}'.format(error)


if __name__ == '__main__':
  main()

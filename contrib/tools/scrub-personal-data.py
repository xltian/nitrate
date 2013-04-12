"""
Django's manage.py has a 'dumpdata' command to dump the database in json
form.  The json dump can be used to create fixtures.

This is a simple script to scrub personal data from a json database dump.
"""
import simplejson
import re
input = simplejson.load(open('datadump.json'))
result = []
for obj in input:
    #if obj['model'] == 'management.testattachments':
    #    # Drop these
    #    continue

    if obj['model'] == 'management.testattachmentdata':
        # Drop these
        continue

    if obj['model'] == 'accounts.profiles':
        obj['fields']['login_name'] = 'user_%i@example.com' % obj['pk']
        obj['fields']['realname'] = 'John Doe #%i' % obj['pk']
        obj['fields']['cryptpassword'] = ''

    if obj["model"] == "testcases.testcaseruns":
        # Replace anything that looks like an email address with a dummy one:
        if obj['fields']['notes']:
            obj['fields']['notes'] = re.sub(r'(\S+)@(\S+)',
                                            'jdoe@example.com',
                                            obj['fields']['notes'])

    result.append(obj)

print simplejson.dumps(result, indent=4)


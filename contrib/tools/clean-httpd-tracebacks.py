"""
Script to extract readable Python tracebacks from httpd error logs

Supply /var/log/httpd/[ssl_]error_log* to stdin
Writes cleaned up tracebacks from Django's mod_python to stdout
"""
import sys
import re
for line in sys.stdin:
    m = re.match('.+PythonHandler django.core.handlers.modpython: (.*), referer: .*', line)
    if m:
        err_line = m.group(1)
        err_line = err_line.replace('\\n', '\n')
        print err_line

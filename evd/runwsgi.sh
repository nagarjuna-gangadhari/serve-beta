uwsgi --close-on-exec -s /tmp/uwsgi_evd.sock --chdir /Users/vishy/evidyaloka/evd --pp .. -w django_wsgi -C666 -p 4

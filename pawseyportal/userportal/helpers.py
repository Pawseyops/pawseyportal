import os

if 'SCRIPT_NAME' in os.environ:
    wsgibasepath=os.environ['SCRIPT_NAME']
else:
    wsgibasepath=''

def wsgibase():
        return wsgibasepath

def siteurl(request):
    d = request.__dict__
    u = ''
    if d['META'].has_key('HTTP_X_FORWARDED_HOST'):
        #The request has come from outside, so respect X_FORWARDED_HOST
        u = d['META']['wsgi.url_scheme'] + '://' + d['META']['HTTP_X_FORWARDED_HOST'] + wsgibase() + '/'
    else:
        #Otherwise, its an internal request
        host = d['META'].get('HTTP_HOST')
        if not host:
            host = d['META'].get('SERVER_NAME')
             
        u = d['META']['wsgi.url_scheme'] + '://' + host + wsgibase() + '/' 
    return u

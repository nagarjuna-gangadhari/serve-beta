import re

from django.template import Library
from django.template.defaultfilters import timesince, truncatewords, truncatewords_html
from django.utils.safestring import mark_safe
import simplejson

register = Library()

@register.filter
def keyvalue(dit, key):    
    return dit[key]

@register.filter
def gt(value, arg):
    return value > int(arg)

@register.filter
def lt(value, arg):
    return value < int(arg)

@register.filter
def gte(value, arg):
    return value >= int(arg)

@register.filter
def lte(value, arg):
    return value <= int(arg)

@register.filter
def length_gt(value, arg):
    return len(value) > int(arg)

@register.filter
def length_lt(value, arg):
    return len(value) < int(arg)

@register.filter
def length_gte(value, arg):
    return len(value) >= int(arg)

@register.filter
def length_lte(value, arg):
    return len(value) <= int(arg)

@register.filter
def cname(value, arg=None):
    return value.__class__.__name__

@register.filter
def strip_p(value, arg=None):
    value = value.rendered.strip()
    if value.lower().count('<p>') == 1:
        value = re.sub('^<p>(?i)', '', value)
        value = re.sub('</p>$(?i)', '', value)
    return mark_safe(value.strip())

@register.filter
def brief(value, arg='p'):
    value = value.rendered.strip()
    nvalue = value

    if '<p>' in nvalue.lower():
        values = re.findall('<p>(.*?)</p>(?is)', nvalue)
        nvalue = values[0].strip() if values else nvalue

    if arg.isdigit():
        CHARS_PER_WORD = 8
        ntvalue = truncatewords_html(nvalue, int(arg)/CHARS_PER_WORD)
        if ntvalue == nvalue and value != nvalue:
            value = ntvalue + ' ...'
        else:
            value = ntvalue

    elif value != nvalue:
        value = nvalue + ' ...'

    return mark_safe(value)

@register.filter
def dt(value, arg=None):
    x = '<span title="%s" class="light">%s ago</span>' % (value.isoformat(), timesince(value))
    return mark_safe(x)

@register.filter
def nth(value, arg=None):
    value = str(value)

    if value == '1':
        s = 'st'

    elif value.endswith('2'):
        s = 'nd'

    elif value.endswith('3'):
        s = 'rd'

    else:
        s = 'th'

    return value + s

@register.filter
def modulo(num, val):
    return num % val

@register.filter
def fetch(listing, index):
    return listing[index]

@register.filter
def split(string, delimiter):
    return string.split(delimiter)

@register.filter
def add(value, arg=0):
    if isinstance(value, (str, unicode)) and value.isdigit():
        value = int(value)
    else:
        return value

    if not isinstance(value, int):
        return value

    return value + arg

@register.filter
def add_digits(value, arg=0):

    return value + arg

@register.filter
def concat(str1, str2 = ""):

    return str1 + str2

@register.filter
def truncatesmart(value, limit=80):
    """
    FROM: http://www.djangosnippets.org/snippets/1259/
    Truncates a string after a given number of chars keeping whole words.
    
    Usage:
        {{ string|truncatesmart }}
        {{ string|truncatesmart:50 }}
    """
    
    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value
    
    # Make sure it's unicode
    value = unicode(value)
    
    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value
    
    # Cut the string
    value = value[:limit]
    
    # Break into words and remove the last
    words = value.split(' ')[:-1]
    
    # Join the words and return
    return ' '.join(words) + '...'


@register.filter
def json_script(value, element_id):
    """
    Output value JSON-encoded, wrapped in a <script type="application/json">
    tag. Not safe method to XSS attacks and needs to implement conditional formating.
    """
    json_str = simplejson.dumps(value)
    format_string = '<script id="{}" type="application/json">{}</script>'.format(element_id, mark_safe(json_str))
    return mark_safe(format_string)

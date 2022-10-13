import os
import MySQLdb
from decimal import Decimal
import hashlib
import colorsys
import json
from django.core.serializers.json import DjangoJSONEncoder

import traceback

#import Image as PIL
from PIL import Image as PIL

from django import template
from django.db.models.fields.files import FieldFile
from django.template import Library
from django.core.files.base import ContentFile
from django.conf import settings
from web.utils import get_doc, HANDLING_CREDITS, parse_flags
from web.models import *
from partner.models import Partner
from web.query import get_items_by_tag
from dateutil.relativedelta import relativedelta
from django.db.models import Q,Count
from configs.models import UserSettings, RoleDefaultSettings
from webext.models import Recognition
NO_IMAGE = '/static/images/no_image_available.gif'
register = Library()


def get_object_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.DoesNotExist:
        return None


def C(context, c):
    #c['request'] = context['request']
    #c['user'] = context.get('user', '')
    #c['ref_path'] = context.get('ref_path', '')
    return c

@register.inclusion_tag('activity_center.html', takes_context=True)
def activity_center(context, user):
    try:
        userp = user.userprofile
        role_preferences = userp.rolepreference_set.all()
        link = ''
        role_list = []
        for ent in role_preferences:
            temp = {}
            temp['name'] = ent.role.name
            temp['short_name'] = ent.role.name.lower().replace(' ','').replace('-', '')
            temp['status'] =  ent.role_onboarding_status
            role_list.append(temp)
    except UserProfile.DoesNotExist:
        role_list = []
    return C(context, { 'role_list' : role_list })

@register.inclusion_tag('footer_widget.html', takes_context=True)
def footer_widget(context):
    centers = Center.objects.all()
    states = []
    subjects = []
    for center in centers:
        states.append(center.state)
    states = list(set(states))[0:8]
    courses = Course.objects.all()
    for course in courses:
        subjects.append(course.subject)
    subjects = list(set(subjects))[0:8]

    return C(context, {'states': states, 'subjects': subjects})

@register.inclusion_tag('login_badge.html', takes_context=True)
def login_badge(context, user):
    profile = UserProfile.objects.filter(user=user)
    if len(profile) > 0:
        profile = profile[0]
    return C(context, {"profile": profile})

@register.assignment_tag
def is_partners(id):
    partner = get_object_or_none(Partner, contactperson=id)
    if partner:
        return partner.id
    return partner

    
def make_number_verb(num):
    stripped_num = str(num)
    last_num = str(num)[-1]
    if stripped_num == "11":
        return stripped_num + "th"
    elif last_num == "1":
        return stripped_num + "st"
    elif last_num == "2":
        return stripped_num + "nd"
    elif last_num == "3":
        return stripped_num + "rd"
    else:
        return stripped_num + "th"

def make_hour(hour):
    if hour >= 12 and hour <=23:
        hour = str(hour) + " PM"
    else:
        hour = str(hour) + " AM"

    return hour

def make_date_time(date_time):
    month_map = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    date_time_arr = {"date":"", "time":""}
    if not date_time:
        return date_time_arr
    time_str = ""
    time_str = time_str + make_hour(date_time.hour)
    date_str = make_number_verb(date_time.day)
    date_str = date_str +" "+ month_map[date_time.month - 1]

    date_time_arr["date"] = date_str
    date_time_arr["time"] = time_str


    return date_time_arr

@register.inclusion_tag('breadcrumb_widget_new.html', takes_context=True)
def breadcrumb(context, user, user_id=None):

    print '1 : ' + str(datetime.datetime.now())
    try:
        profile = UserProfile.objects.filter(user=user)
        if profile:
            profile = profile[0]
    except UserProfile.DoesNotExist:
        profile = None
    is_centeradmin, is_teacher, is_both, is_superuser,is_content_reviewer,csd_panel_member, is_contentadmin, is_pam_volunteer,is_pam_funding,is_pam_delivery,is_contentdeveloper,is_classassistant, is_vol_admin, is_vol_coordinator, is_partner, is_delivery, is_digital_partner, is_funding,is_volunteer, partner_status,is_field_coordinator,is_delivery_coordinator,is_fc_partnerchannel,tsd_panel_member, is_partner_account_manager,is_orgUnit,is_well_wisher,is_internal = [False] * 28
    if user.is_superuser: is_superuser = True
    if profile:
        if len(profile.role.filter(name = "TSD Panel Member")) > 0:tsd_panel_member = True
        if len(profile.role.filter(name = "CSD Panel Member")) > 0:csd_panel_member = True
        if len(profile.role.filter(name = "Content Reviewer")) > 0:is_content_reviewer = True
        if len(profile.role.filter(name = "Center Admin")) > 0 and len(profile.pref_roles.filter(name = "Teacher")) > 0: is_both = True
        if len(profile.role.filter(name = "Center Admin")) > 0: is_centeradmin = True
        if len(profile.pref_roles.filter(name = "Partner Account Manager")) > 0:
            #print "***** IS ACCOUNT MANAGER ******"
            is_partner_account_manager = True
        if len(profile.pref_roles.filter(type = "Internal")) > 0: is_internal = True
        if len(profile.role.filter(name = "Class Assistant")) > 0 and len(profile.pref_roles.filter(name = "Teacher")) > 0: is_both = True
        if len(profile.role.filter(name = "Class Assistant")) > 0: is_classassistant = True
        if len(profile.role.filter(name = "Content Admin")) > 0 and len(profile.pref_roles.filter(name = "Teacher")) > 0: is_contentadmin = True; is_teacher = True
        if len(profile.role.filter(name = "Content Developer")) > 0 and len(profile.pref_roles.filter(name = "Teacher")) > 0: is_contentdeveloper = True; is_teacher = True
        elif len(profile.role.filter(name = "Content Admin")) > 0: is_contentadmin = True
        elif len(profile.pref_roles.filter(name = "Teacher")) > 0: is_teacher = True
        elif len(profile.pref_roles.filter(name = "Content Developer")) > 0: is_contentdeveloper = True
        elif len(profile.pref_roles.filter(name = "vol_admin")) > 0: is_vol_admin = True
        elif len(profile.pref_roles.filter(name = "vol_co-ordinator")) > 0: is_vol_coordinator = True
        if len(profile.role.filter(name = "Partner Admin")) > 0: is_partner = True
        if len(profile.role.filter(name = "Well Wisher")) > 0: is_well_wisher = True
        if len(profile.pref_roles.filter(name = "vol_admin")) > 0: is_vol_admin = True
        if len(profile.pref_roles.filter(name = "vol_co-ordinator")) > 0: is_vol_coordinator = True
     
        if len(profile.role.filter(name = "Field co-ordinator")) > 0:
            is_field_coordinator = True
            uroles = profile.role.all()
            rp = uroles.filter(Q(name='Field co-ordinator') or Q(name='Partner Admin'))
            rolepreference_outcome = []
            for role in rp:
                try:
                    rolepreference = RolePreference.objects.get(userprofile_id=profile.id,role_id=role.id)
                    if rolepreference.role_status =='New' or rolepreference.role_status =='Active':
                        rolepreference_outcome.append(rolepreference.role_outcome)
                except RolePreference.DoesNotExist:
                    pass
            if profile.referencechannel.partner_id and 'Recommended' in rolepreference_outcome:
                is_fc_partnerchannel = True
        if len(profile.role.filter(name = "Delivery co-ordinator")) > 0: is_delivery_coordinator = True
    if user.partner_set.values():
        if user.partner_set.values()[0]['status'] == 'Approved': partner_status = True

    print '2 : ' + str(datetime.datetime.now())
    partner = user.partner_set.all()
    if partner:
        partner_types = partner[0].partnertype.values()
        print(partner_types)
        for partnerty in partner_types:
            if partnerty['name'] == 'Delivery Partner': is_delivery = True
            if partnerty['name'] == 'Digital Partner': is_digital_partner = True
            if partnerty['name'] == 'Funding Partner': is_funding = True
            if partnerty['name'] == 'Volunteering Partner': is_volunteer = True
            if partnerty['name'] == 'Organization Unit': is_orgUnit = True
            

    user_sessions = Session.objects.filter(teacher = user)
    my_offering_arr, offerings, topics_arr, offerings_arr = [], [], [], []


    print '3 : ' + str(datetime.datetime.now())
    try:
        for session in user_sessions:
            offerings.append(session.offering)
    except Exception as exp:
        exception_trace = traceback.format_exc()
        print "**EXCEPTION**\n", str(exception_trace)

    offerings_arr = set(offerings)

    for offering in offerings_arr:
        my_topics = []
        planned_topics = offering.planned_topics.all()
        if planned_topics:
            for planned_topic in planned_topics:
                topic = { "title": planned_topic.title, "url": planned_topic.url }
                my_topics.append(topic)
        topic = {
            "subject": offering.course.subject,
            "grade": offering.course.grade,
            "board": offering.course.board_name,
            "my_topics": my_topics
        }
        topics_arr.append(topic)

    print '4 : ' + str(datetime.datetime.now())
    try:
        for session in user_sessions:
            offerings.append(session.offering)
    except Exception as exp:
        exception_trace = traceback.format_exc()
        print "*** EXCEPTION ***\n", str(exception_trace)

    offerings = set(offerings)
    for offering in offerings:
        my_offering = {
                    "subject": offering.course.subject,
                    "grade": offering.course.grade,
                    "start": make_date_time(offering.start_date)['time'],
                    "date": make_date_time(offering.start_date)['date'],
                    "day": offering.start_date.weekday(),
                    "center": offering.center.name,
                    "id": offering.id
        }
        my_offering_arr.append(my_offering)

    print '5 : ' + str(datetime.datetime.now())
    if is_classassistant: user_centers = Center.objects.filter(assistant = user)
    elif is_field_coordinator: user_centers = Center.objects.filter(field_coordinator = user)
    elif is_delivery_coordinator: user_centers = Center.objects.filter(delivery_coordinator = user)
    else: user_centers = Center.objects.filter(admin = user)

    center_courses = []
    courses = []
    all_centers = []
    students = []
    center_id = 0
    if user_centers:
        for center in user_centers:
            center_id = center.id
            center_board = center.board

            try:
                current_ay = Ayfy.objects.get(Q(start_date__lte = datetime.datetime.now()) & Q(end_date__gte=datetime.datetime.now()) & Q( board = center_board))
            except:
                current_ay = Ayfy.objects.get(end_date__year=datetime.datetime.now().year,board = center_board)

            center_offerings = Offering.objects.filter(center__id = center_id)
            for offering in center_offerings:
                center_courses.append({\
                                        "course" : offering.course.grade + "th " + offering.course.subject,\
                                        "start_date": make_date_time(offering.start_date)["date"]  ,\
                                        "end_date": make_date_time(offering.end_date)['date'],\
                                        "center": offering.center,\
                                        "offering_id": offering.id\
                                      })

            courses = Course.objects.all()
            all_centers = Center.objects.all()
            students = Student.objects.filter(center_id = center_id)

    print '6 : ' + str(datetime.datetime.now())
    if is_partner_account_manager:
        db= MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
            user=settings.DATABASES['default']['USER'],
            passwd=settings.DATABASES['default']['PASSWORD'],
            db=settings.DATABASES['default']['NAME'],
            charset="utf8", use_unicode=True)

        dict_cur = db.cursor(MySQLdb.cursors.DictCursor)
        query=" select * from partner_partner_partnertype  where partner_partner_partnertype.pam = '"+str(user.id)+"' and partner_partner_partnertype.partnertype_id=1 "
        dict_cur.execute(query)
        partner_name = dict_cur.fetchall()

        if partner_name:
            is_pam_volunteer =True

        query=" select * from partner_partner_partnertype  where partner_partner_partnertype.pam = '"+str(user.id)+"' and partner_partner_partnertype.partnertype_id=3"

        dict_cur.execute(query)
        fund_partner = dict_cur.fetchall()
        if fund_partner:
            is_pam_funding = True

        query=" select * from partner_partner_partnertype  where partner_partner_partnertype.pam = '"+str(user.id)+"' and partner_partner_partnertype.partnertype_id=2"

        dict_cur.execute(query)
        delivery_partner = dict_cur.fetchall()
        db.close()
        dict_cur.close()
        if delivery_partner:
            is_pam_delivery = True

    if is_delivery:
        center_courses = []
        courses = []
        all_centers = []
        students = []
        user_centers = Center.objects.filter(delivery_partner_id = user.partner_set.all()[0].id)
        for center in user_centers:
            center_id = center.id
            center_offerings = Offering.objects.filter(center__id = center_id)
            for offering in center_offerings:
                center_courses.append({\
                                "course" : offering.course.grade + "th " + offering.course.subject,\
                                "start_date": make_date_time(offering.start_date)["date"]  ,\
                                "end_date": make_date_time(offering.end_date)['date'],\
                                "center": offering.center,\
                                "offering_id": offering.id\
                                })
            courses = Course.objects.all()
            all_centers = Center.objects.all()
            students = Student.objects.filter(center_id = center_id)

    print '7 : ' + str(datetime.datetime.now())

    if is_funding:
        center_courses = []
        courses = []
        all_centers = []
        students = []
        user_centers = Center.objects.filter(Q(funding_partner_id = user.partner_set.all()[0].id))
        for center in user_centers:
            center_id = center.id
            center_offerings = Offering.objects.filter(center__id = center_id)
            for offering in center_offerings:
                center_courses.append({\
                            "course" : offering.course.grade + "th " + offering.course.subject,\
                            "start_date": make_date_time(offering.start_date)["date"]  ,\
                            "end_date": make_date_time(offering.end_date)['date'],\
                            "center": offering.center,\
                            "offering_id": offering.id\
                            })
            courses = Course.objects.all()
            all_centers = Center.objects.all()
            students = Student.objects.filter(center_id = center_id)

    print '8 : ' + str(datetime.datetime.now())

    if user.is_superuser:
        user_centers = Center.objects.all()
       # for site admin, he has will have all the centers as his centers
        if context['request'].path_info == "/centeradmin/":
            center_id = int(context['request'].GET['center_id'])
            centers = Center.objects.filter(id = center_id)
        else:
            centers = Center.objects.all()
        center_courses = []
        courses = []
        center_id = 0
        print 'centers count ' + str(len(user_centers))
        '''
        if centers:
            for center in centers:
                center_id = center.id
                center_offerings = Offering.objects.filter(center__id = center_id)
                for offering in center_offerings:
                    center_courses.append({\
                                            "course" : offering.course.grade + "th " + offering.course.subject,\
                                            "start_date": make_date_time(offering.start_date)["date"]  ,\
                                            "end_date": make_date_time(offering.end_date)['date'],\
                                            "center": offering.center,\
                                            "offering_id": offering.id\
                                          })

                
        '''
        courses = Course.objects.all()

    print '9 : ' + str(datetime.datetime.now())

    for center in user_centers:
        center_board = center.board
        if center_board is None:
            continue
        if center_board == 'eVidyaloka ':
            pass
        else:
            try:
                current_ay = Ayfy.objects.get(start_date__year = datetime.datetime.now().year, board = center_board)
            except:
                last_year = (datetime.datetime.now()+relativedelta(years=-1)).year
                current_ay = Ayfy.objects.get(start_date__year = last_year, board = center_board)
            center.ay = current_ay.id

    centers = Center.objects.all()
    all_ay = Ayfy.objects.filter(types= 'Academic Year')
    print '10 : ' + str(datetime.datetime.now())

    is_approved =False
    if is_funding and is_delivery:
        if user.partner_set.values()[0]['status'] == 'Approved':
            is_approved = True

    assigned_usr_center_id = None
    assigned_usr_offering_id = None
    if is_teacher or is_centeradmin and not is_delivery_coordinator:

        offering = Offering.objects.filter(active_teacher = user,status='running')
        if len(offering)>0:
            offr_assigned_usr = offering[0]
            assigned_usr_offering_id = offr_assigned_usr.id
            assigned_usr_center_id = offr_assigned_usr.center.id
    current_ay = Ayfy.objects.all().order_by('-id')[0]
    try:
        my_center_id = context['request'].GET['center_id']
        if my_center_id:
            my_center = Center.objects.get(id=int(my_center_id))
            try:
                current_ay = Ayfy.objects.get(start_date__year = datetime.datetime.now().year, board = my_center.board)
            except:
                my_ay = Ayfy.objects.filter(board=my_center.board).order_by('-id')
                current_ay = my_ay[0]
    except Exception as e:
        print("FT Exception", e);traceback.print_exc()
        
    return C(context, { "is_teacher": is_teacher,"is_content_reviewer":is_content_reviewer, "is_centeradmin":is_centeradmin, "user_centers":user_centers,"is_pam_delivery":is_pam_delivery,"is_pam_funding":is_pam_funding,"is_pam_volunteer":is_pam_volunteer,
                        "center_courses":center_courses, "courses":courses, "students": students,"is_partner_account_manager":is_partner_account_manager,
                        "center_id":center_id, "is_both":is_both, "my_offering":my_offering_arr, "is_superuser": is_superuser, 'is_internal': is_internal,
                        "topics": topics_arr, "centers":centers, "is_contentadmin": is_contentadmin,"csd_panel_member":csd_panel_member,
                        'is_contentdeveloper': is_contentdeveloper, 'user': user, "is_classassistant":is_classassistant,
                        'is_vol_admin':is_vol_admin, 'is_vol_coordinator':is_vol_coordinator,"is_approved":is_approved,
                        'is_partner' : is_partner, 'is_delivery' : is_delivery, 'is_funding' : is_funding, 'is_digital_partner':is_digital_partner,
                        'is_volunteer' : is_volunteer, 'partner_status' : partner_status, 'all_ay': all_ay, 'current_ay':current_ay,
                        'is_field_coordinator':is_field_coordinator,'is_delivery_coordinator':is_delivery_coordinator,'is_fc_partnerchannel':is_fc_partnerchannel,
                        'assigned_usr_offering_id':assigned_usr_offering_id,'assigned_usr_center_id':assigned_usr_center_id,'tsd_panel_member':tsd_panel_member,'is_orgUnit':is_orgUnit,'is_well_wisher':is_well_wisher})

@register.inclusion_tag('time_slot.html', takes_context=True)
def time_slots(context, id = None, w_days = None, w_slots = None, title = None):
    week_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week_map = {}
    if w_days and len(w_days) > 0 and len(w_slots) > 0:
        w_days = [ str(wd) for wd in w_days.split(";") ]
        w_slots = w_slots.split(";")
        for index,day in enumerate(w_days):#praneeth
           # week_map[str(day)] = [ int(ws) for ws in w_slots[index].split("-") ]
           week_map[str(day)] = [ int(ws.split(":")[0]) for ws in w_slots[index].split("-") ]

    return C(context, {"id": id, "label": title, "w_days": w_days, "w_slots": w_slots, "week_map": week_map, "week_days": week_days})

@register.inclusion_tag('ui/comment_widget.html', takes_context=True)
def comment(context, target, flags=None):
    flags = parse_flags(flags)

    return C(context, {'target': target, 'flags': flags})

@register.inclusion_tag('ui/outline_widget.html', takes_context=True)
def outline(context, node, depth):
    subnodes = Node.objects.filter(parent=node).order_by('order')
    return C(context, {'depth': depth + 1, 'node': node, 'subnodes': subnodes})

@register.inclusion_tag('ui/paginator_widget.html', takes_context=True)
def paginator(context, items, paging_url):
    previous_link = paging_url.replace('<PAGENO>',
        str(items.previous_page_number()))

    next_link = paging_url.replace('<PAGENO>',
        str(items.next_page_number()))

    return C(context, {'items': items, 'previous_link': previous_link,
            'next_link': next_link})

@register.inclusion_tag('ui/cart_widget.html', takes_context=True)
def cart(context):
    req = context['request']
    user = context['user']
    if user.is_anonymous():
        return ''

    show_checkout_link = not req.get_full_path().startswith('/cart/checkout/')

    cart_data = req.session.setdefault('cart', [])
    cart = []
    total_credits = Decimal('0.0')

    for item, num in cart_data:
        item = RedeemableItem.objects.get(id=int(item))
        item.opts = range(1, item.num + 1)
        cart.append((item, num))
        item_credits = item.credits * num
        item.item_credits = item_credits
        total_credits += item_credits

    total_credits = total_credits + HANDLING_CREDITS

    available_credits = user.get_profile().credits - total_credits
    sufficient_credits = (available_credits >= 0)

    data = {
            'cart': cart,
            'total_credits': total_credits,
            'available_credits': available_credits.copy_abs(),
            'handling_credits': HANDLING_CREDITS,
            'sufficient_credits': sufficient_credits,
            'checkout_link': show_checkout_link,
           }
    return C(context, data)

@register.inclusion_tag('ui/markitup_editor.html', takes_context=True)
def markup(context, widget_id, target):
    return C(context, {'widget_id': widget_id, 'target': target})

@register.inclusion_tag('ui/attachments_widget.html', takes_context=True)
def attachments(context, target, num):
    user = context['user']
    can_add = target.is_editable_by(user)
    return C(context, {'target': target, 'num': num, 'can_add': can_add})

def render(parser, token):
    contents = token.split_contents()
    tag_name = contents.pop(0)

    if len(contents) < 1:
        raise template.TemplateSyntaxError, "%r tag requires atleast one argument" % tag_name

    return RenderObj(contents)

class RenderObj(template.Node):
    def __init__(self, contents):
        self.contents = contents

    def render(self, context):
        resolved_contents = []

        for c in self.contents:
            resolved_contents.append(template.Variable(c).resolve(context))

        obj = resolved_contents.pop(0)
        if obj is None:
            return ''

        return obj.render(context, *resolved_contents)

register.tag('render', render)

def button(parser, token):
    args = token.split_contents()
    tag_name = args.pop(0)

    if len(args) < 1:
        raise template.TemplateSyntaxError, "%r tag atleast one argument" % tag_name

    link = args.pop(0)[1:-1]
    kwargs = dict([a.strip('\'').split('=', 1) for a in args])

    nodelist = parser.parse(('endbutton',))
    parser.delete_first_token()

    return Button(nodelist, link, kwargs)

class Button(template.Node):
    DEFAULTS = {
        'title': 'Click Here',
        'color': '7E9BDE',
        'hcolor': 'DEDEDE',
        'borderwidth': '1px',
        }

    def _ensure_range(self, val, min, max):
        if val < min: return min
        if val > max: return max
        return val

    def _get_text_color(self, color):
        rgb = self._htmlcolor_to_rgb(color)
        rgb = self._norm_rgb(rgb)
        h, s, v = colorsys.rgb_to_hsv(*rgb)

        text_v = .9 if v < .7 else .1
        text_v = self._ensure_range(text_v, 0, 1)

        rgb = colorsys.hsv_to_rgb(h, 0.2, text_v)
        rgb = self._denorm_rgb(rgb)
        return self._rgb_to_htmlcolor(rgb)

    def _norm_rgb(self, rgb):
        r, g, b = rgb
        r = r / 255.
        g = g / 255.
        b = b / 255.
        return r, g, b

    def _denorm_rgb(self, rgb):
        r, g, b = rgb
        r = r * 255
        g = g * 255
        b = b * 255
        return r, g, b

    def _get_lighter_color(self, htmlcolor, percent=.1):
        rgb = self._htmlcolor_to_rgb(htmlcolor)
        rgb = self._norm_rgb(rgb)
        h, s, v = colorsys.rgb_to_hsv(*rgb)
        v = v + v * percent
        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb = self._denorm_rgb(rgb)
        return self._rgb_to_htmlcolor(rgb)

    def _get_darker_color(self, htmlcolor, percent=.1):
        rgb = self._htmlcolor_to_rgb(htmlcolor)
        rgb = self._norm_rgb(rgb)
        h, s, v = colorsys.rgb_to_hsv(*rgb)
        v = v - v * percent
        rgb = colorsys.hsv_to_rgb(h, s, v)
        rgb = self._denorm_rgb(rgb)
        return self._rgb_to_htmlcolor(rgb)

    def _rgb_to_htmlcolor(self, rgb):
        r, g, b = [int(self._ensure_range(v, 0, 255)) for v in rgb]
        return '%s%s%s' % (hex(r)[2:], hex(g)[2:], hex(b)[2:])

    def _htmlcolor_to_rgb(self, htmlcolor):
        h = htmlcolor.strip(' #')
        r, g, b = h[:2], h[2:4], h[4:6]
        r = eval('0x' + r)
        g = eval('0x' + g)
        b = eval('0x' + b)
        return r, g, b

    def __init__(self, nodelist, link, kwargs):
        self.nodelist = nodelist
        self.link = link
        self.kwargs = kwargs

    def render(self, context):
        t = template.loader.get_template('ui/button_widget.html')

        button_text = self.nodelist.render(context)
        button_class = 'btncl_' + hashlib.md5(self.link).hexdigest()

        for k, v in self.kwargs.iteritems():
            self.kwargs[k] = template.Template(v).render(context)

        c = make_context(context)
        c['link'] = template.Template(self.link).render(context)
        c['buttontext'] = button_text
        c['button_class'] = button_class

        k = dict(self.kwargs)
        D = self.DEFAULTS

        k['title'] = k.get('title') or D['title']
        k['color'] = k.get('color') or D['color']
        k['hcolor'] = k.get('hcolor') or D['hcolor']
        k['borderwidth'] = k.get('borderwidth') or D['borderwidth']

        k['tcolor'] = k.get('tcolor') or self._get_text_color(k['color'])
        k['htcolor'] = k.get('htcolor') or self._get_text_color(k['hcolor'])

        k['blight'] = k.get('blight') or self._get_lighter_color(k['color'], .3)
        k['bdark'] = k.get('bdark') or self._get_darker_color(k['color'], .3)

        k['hblight'] = k.get('hblight') or self._get_lighter_color(k['hcolor'], .3)
        k['hbdark'] = k.get('hbdark') or self._get_darker_color(k['hcolor'], .3)

        kwargs = k

        for k, v in kwargs.iteritems():
            c[k] = v

        c = C(context, c)

        return t.render(c)

register.tag('button', button)

def thumbnail(obj, size='104x104'):

    square = False
    arg_size = size
    if size.startswith('S'):
        square = True
        size = size[1:]
        crop = True

    if isinstance(obj, FieldFile):
        file = obj
        path = file.path
        url = file.url

    else:
        return thumbnail(NO_IMAGE , size)

    # defining the size
    dimensions = [int(x) if x.isdigit() else None for x in size.lower().split('x')]

    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(path)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    filename = path
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(url)
    miniature_url = filehead + '/' + miniature

    if os.path.exists(miniature_filename) and os.path.getmtime(filename) > os.path.getmtime(miniature_filename):
        os.unlink(miniature_filename)

    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename):

        try:
            image = PIL.open(filename)
        except IOError:
            if isinstance(obj, AssociatedMedia):
                obj.delete()
            return thumbnail(NO_IMAGE , size)

        format = image.format

        if image.mode != 'RGBA' and format != 'BMP':
            image = image.convert('RGBA')

        if square:
            width, height = image.size
            side = min(width, height)
            x = (width - side) / 2
            y = (height - side) / 2
            image = image.crop((x, y, x+side, y+side))

        try:
            image.thumbnail(dimensions, PIL.ANTIALIAS)
            image.save(miniature_filename, format, quality=90)
        except:
            return thumbnail('/static/images/user.png', arg_size)

    return miniature_url

register.filter(thumbnail)


def crop(obj, size='104x104'):

    arg_size = size

    if isinstance(obj, FieldFile):
        file = obj
        path = file.path
        url = file.url

    else:
        return thumbnail(NO_IMAGE , size)

    # defining the size
    dimensions = [int(x) if x.isdigit() else None for x in size.lower().split('x')]

    # defining the filename and the miniature filename
    filehead, filetail = os.path.split(path)
    basename, format = os.path.splitext(filetail)
    miniature = basename + '_' + size + format
    filename = path
    miniature_filename = os.path.join(filehead, miniature)
    filehead, filetail = os.path.split(url)
    miniature_url = filehead + '/' + miniature

    if os.path.exists(miniature_filename) and os.path.getmtime(filename) > os.path.getmtime(miniature_filename):
        os.unlink(miniature_filename)

    # if the image wasn't already resized, resize it
    if not os.path.exists(miniature_filename):

        try:
            image = PIL.open(filename)
        except IOError:
            return None

        format = image.format

        # if image.mode != 'RGBA' and format != 'BMP':
        #     image = image.convert('RGBA')

        width, height = image.size
        _width, _height = dimensions
        x = (width - _width) / 2
        y = (height - _height) / 2
        #image = image.crop((x, y, x+_width, y+_height))
        image = image.resize((_width, _height), PIL.ANTIALIAS)

        try:
            #image.thumbnail(dimensions, PIL.ANTIALIAS)
            image.save(miniature_filename, format, quality=90)
        except:
            pass
            #return thumbnail('/static/images/user.png', arg_size)

    return miniature_url

register.filter(crop)

@register.filter
def increment_value(value):
    return value + 1


@register.filter()
def typeimg(value, key):
  """
    Returns the value turned into a list.
  """
  ext = value.split(key)[-1]
  if ext.lower() in ['png','jpeg','jpg','svg']:
      return True
  else:
    return False
#
# @register.filter
# def get_at_index(list, index):
#     print 'list',list,'index',index
#     return list[index]
#
@register.filter(name='split')
def split(value, key):
  """
    Returns the value turned into a list.
  """
  return [i.strip() for i in value.split(key)]


@register.filter()
def getuservalue(var,args):
    if args in var.keys():
        return var[args]
    else:
        return False


@register.filter(name='useritemvalue')
def useritemvalue(user,settingitem):
    try:
        usersettings = user.usersettings_set.get(settings_grp_items_id=settingitem.id,is_removed=False)
        return [i.strip() for i in usersettings.values.split(',')]
    except UserSettings.DoesNotExist:
        return []

@register.filter()
def roleitemvalue(role,settingitem):
    try:
        rolesettings = role.roledefaultsettings_set.get(settings_grp_items_id=settingitem.id,is_removed=False)
        return [i.strip() for i in rolesettings.values.split(',')]
    except RoleDefaultSettings.DoesNotExist:
        return []

@register.filter()
def listFilter(list1, list2):
    if isinstance(list1, list):
        list1.extend(list2)
    elif isinstance(list1, dict):
        list1.update(list2)
    return list1


@register.filter(name='usertimezonevalue')
def usertimezonevalue(user):
    try:
        usersettings = user.usersettings_set.get(settings_grp_items__settings_group__id=1,settings_grp_items__input_name__iexact='timezone',is_removed=False)
        return usersettings.values
    except UserSettings.DoesNotExist:
        return []

@register.filter(name='getAYOfCenter')
def getAYOfCenter(center):
    center_board = center.board
    if center_board == 'eVidyaloka ':
        return None
    else:
        try:
            current_ay = Ayfy.objects.get(start_date__year=datetime.datetime.now().year, board=center_board)
        except:
            last_year = (datetime.datetime.now() + relativedelta(years=-1)).year
            current_ay = Ayfy.objects.get(start_date__year=last_year, board=center_board)
        return current_ay.id

@register.filter(name='removespace')
def removespace(value):
  """
    Returns the value by removing all spaces init.
  """
  return value.replace(' ','')


@register.filter(name='getnames')
def getnames(roles):
    listroles = []
    for role in roles:
        listroles.append(str(role.name.replace(' ','')))
    return listroles


@register.filter(is_safe=True)
def getmyitem(data,id):
    if data and id:
        myobject = data.values().get(id=id)
        # display_data = {}
        # display_data['id'] = myobject.id
        # display_data['sticker_type'] = myobject.sticker_type
        # display_data['for_whom'] = myobject.for_whom
        # display_data['sticker_name'] = myobject.sticker_name
        # print myobject.sticker_path
        return json.dumps(myobject,cls=DjangoJSONEncoder)

@register.filter(is_safe=True)
def count_of_sticker(user):
    sticker_count = Recognition.objects.filter(object_id = user.id,content_type = ContentType.objects.get(model='user')).values('sticker__sticker_name', 'sticker__sticker_path').annotate(countofsticker=Count('sticker__sticker_name'))
    return sticker_count


@register.filter()
def vol_of_month_centerName(userid):
    offering=Offering.objects.filter(active_teacher_id=userid).exclude(center_id__isnull=True)
    if offering:
        center=Center.objects.get(id=offering[0].center_id)
    else:
        center=None
    return center

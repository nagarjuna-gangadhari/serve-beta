from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^roles/(?P<role_id>\d+)?/?$',list_roles),
    url(r'^role/settings/(?P<role_id>\d+)/?$',add_role_specific_settings),
    # url(r'^role/notifications/(?P<role_id>\d+)/?$',add_role_specific_notifications),
    # url(r'^user/notifications/(?P<user_id>\d+)/?$',add_user_specific_notifications),
    url(r'^user/settings/?$',user_settings),
    url(r'^user/save_profile/?$',userprofile_save),
    url(r'^user/add_consent_profile/?$',userprofile_add_consent),
    url(r'^user/save_preferences/?$',user_preferences_save),
    url(r'^save_skype_phone/?$',save_skype_phone),
    # url(r'^get_timezone/(?P<latitude>\d+\.\d+)/(?P<longitude>\d+\.\d+)/?$',get_timezone_by_location),
    url(r'^appreciationreason/add/(?P<reason_id>\d+)?/?$',add_appreciationReason),
    url(r'^appreciationreasons/?$',list_appreciationReasons),
    url(r'^sticker/add/(?P<sticker_id>\d+)?/?$',add_sticker),
    url(r'^stickers/?$',list_stickers),
    url(r'^generate_certificate/?$', GenerateCertificate.as_view()),
    url(r'^my_certificate/?$', get_my_certificate),
    url(r'^getsharableurl/?$', getDemandSharableLink),
    url(r'^getsharableDemandsInfo/?$', getDemandSharableLinkForFilters),
    url(r'^getsharableURLfor/?$', getsharableURLfor),
]
import copy
import json

from django.contrib.auth.models import User 
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from social_auth.models import UserSocialAuth

def get_active_user(users):
    #Generate to_validate with only users who are active
    #In this way we will perfom the checks below only for active accounts
    to_validate = [i for i in users if i.is_active]
    if len(to_validate) == 1:
        return to_validate[0]

    last_logged_in  = []
    users_weightage = {}

    while to_validate:
        user = to_validate[0]
        last_logged_in.append((user.last_login, user))
        to_validate.remove(user)
        user_weightage = 0

        if user.is_active:
            user_weightage += 10

        if user.userprofile.profile_completion_status:
            user_weightage += 10

        rolepreference_set = user.userprofile.rolepreference_set.all()
        if rolepreference_set:
            user_weightage += 10

        for rolepreference in rolepreference_set:
            if rolepreference.role_outcome == "Recommended":
                user_weightage += 100

            completed_steps = rolepreference.onboardingstepstatus_set.filter(status = True)
            for completed_step in completed_steps:
                user_weightage += completed_step.step.weightage

        #Check if active user from Offerings table
        active_classes_count = user.offering_set.all().count()
        user_weightage += 100 * active_classes_count

        users_weightage[user] = user_weightage

    active_user    = None
    inactive_users = []
    if len(set(users_weightage.values())) == 1:
        #Both the users have same profile weightage
        #So considering latest logged in user as active
        for i, login_tuple in enumerate(sorted(last_logged_in, reverse=True)):
            if i == 0:
                active_user = login_tuple[-1]
            else:
                inactive_users.append(login_tuple[-1])
    else:
        sorted_values = sorted(users_weightage.items(), key=lambda x: x[1], reverse=True)
        for i, weightage_tuple in enumerate(sorted_values):
            if i == 0:
                active_user = weightage_tuple[0]
            else:
                inactive_users.append(weightage_tuple[0])

    for inactive_user in inactive_users:
        socail_entries = inactive_user.social_auth.all()
        socail_accounts = []
        #Assigning Inactive user socail accounts to Active user.
        #So when user login's with socail accounts will be pointed to active account.
        for social_entry in socail_entries:
            socail_accounts.append(social_entry.provider)
            social_entry.user = active_user
            social_entry.save()

        au_socail_accounts = [i.provider for i in active_user.social_auth.all()]
        remarks_dict = {"message": "Duplicate Account", "active_user": int(active_user.id)}
        remarks_dict["active_user_profile_weightage"] = users_weightage.get(active_user, None)
        remarks_dict["profile_weightage"] = users_weightage.get(inactive_user, None)
        remarks_dict["active_user_last_login"] = active_user.last_login.strftime("%B %d %Y, %I:%M %p")
        remarks_dict["last_login"] = inactive_user.last_login.strftime("%B %d %Y, %I:%M %p")
        remarks_dict["socail_accounts"] = ",".join(socail_accounts)
        remarks_dict["active_user_socail_accounts"] = ",".join(au_socail_accounts)
        inactive_user.userprofile.remarks = json.dumps(remarks_dict)
        inactive_user.userprofile.save()

        #Marking user as inactive
        inactive_user.is_active = False
        inactive_user.save()

    return active_user

def associate_by_email(details, user, social_user, *args, **kwargs):
    old_user = user
    email    = details.get('email', '')
    if email:
        try:
            user = User.objects.get(email=email)
        except User.MultipleObjectsReturned:
            users = User.objects.filter(email=email)
            user = get_active_user(users)
        except User.DoesNotExist:
            return

        response_dict = {'user': user}
        if social_user and old_user != user:
            try:
                social_user = user.social_auth.get(id = social_user.id)
                response_dict['social_user'] = social_user
            except UserSocialAuth.DoesNotExist:
                pass
        return response_dict

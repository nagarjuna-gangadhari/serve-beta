from web.models import School,Center,UserProfile
from partner.models import Partner,MySchool
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError



class Command(BaseCommand):
    ''' Command for migrating all existing schools to partner_MySchool of respective partner and set parter_MySchool Id in place of School in Center table '''
    def handle(self,*args, **kwargs):
        partners = Partner.objects.all()
        schools = School.objects.all()
        for school in schools:
            print 'School ID',school.id
            try:
                partner = partners.get(contactperson=school.created_by)
                try:
                    partner_school = MySchool.objects.get(school_id=school.id,school__school_code=school.school_code)
                    print('School with school_code %s is already added to the partner_MySchool by %s.' %(school.school_code,partner.name))
                except MySchool.DoesNotExist:
                    partner_school = MySchool.objects.create(partner=partner,school=school,status='Eligible',added_by=school.created_by)
                    partner_school.save()
                    print('School with school_code %s is added to the partner_MySchool by %s.' %(school.school_code,partner.name))
                    centers = Center.objects.filter(school_id=school.id)
                    for center in centers:
                        center.parter_school = partner_school
                        center.save()
                        print('Center with school_code %s is updated with partner_MySchool.' %(str(school.school_code)))
                except MySchool.MultipleObjectsReturned:
                    print('School with school_code %s is multiple times added to the partner_MySchool by %s.' %(school.school_code,partner.name))
            except Partner.DoesNotExist:
                try:
                    usrp = UserProfile.objects.get(user=school.created_by)
                    if usrp.referencechannel_id:
                        if usrp.referencechannel.partner_id:
                            partner = partners.get(id=usrp.referencechannel.partner_id)
                            try:
                                partner_school = MySchool.objects.get(school_id=school.id,school__school_code=school.school_code)
                                print('School with school_code %s is already added to the partner_MySchool by %s.' %(str(school.school_code),partner.name))
                            except MySchool.DoesNotExist:
                                partner_school = MySchool.objects.create(partner=partner,school=school,status='Eligible',added_by=school.created_by)
                                partner_school.save()
                                print('School with school_code %s is added to the partner_MySchool by %s.' %(str(school.school_code),partner.name))
                                centers = Center.objects.filter(school_id=school.id)
                                for center in centers:
                                    center.parter_school = partner_school
                                    center.save()
                                    print('Center with school_code %s is updated with partner_MySchool.' %(str(school.school_code)))
                            except MySchool.MultipleObjectsReturned:
                                print('School with school_code %s is multiple times added to the partner_MySchool by %s.' %(str(school.school_code),partner.name))
                        else:
                            print 'partner not found in referrence channel of userprofile ID ', usrp.id
                    else:
                        print 'user preferrencechannel not found for the userprofile ID ', usrp.id
                except UserProfile.DoesNotExist:
                    print 'userprofile not found for the school id ',school.id


#
# class Command(BaseCommand):
#     ''' command for migrating all schools to Partner_MySchool and set partner as Dummy partner (Pratimac User) and set same MySchool_id in Center table school column'''
#     def handle(self,*args, **kwargs):
#         partner = Partner.objects.get(contactperson__username='pratimac@evidyaloka.org')
#         print('Im partner and my name is %s' %partner.name)
#         schools = School.objects.exclude(created_by = None)
#         for school in schools:
#             try:
#                 partner_school = MySchool.objects.get(school_id=school.id)
#                 print('School with school_code %s is already added to the partner_MySchool by %s.' %(school.school_code,partner.name))
#                 partner_school.partner=partner
#                 partner_school.save()
#                 centers = Center.objects.filter(school_id=school.id)
#                 for center in centers:
#                     center.school_id = partner_school.id
#                     center.parter_school_id = partner_school.id
#                     center.save()
#             except MySchool.DoesNotExist:
#                 partner_school = MySchool.objects.create(partner=partner,school=school,status='Eligible',added_by_id=partner.contactperson_id)
#                 partner_school.save()
#                 print('School with school_code %s is added to the partner_MySchool by %s.' %(school.school_code,partner.name))
#                 centers = Center.objects.filter(school_id=school.id)
#                 for center in centers:
#                     center.school_id = partner_school.id
#                     center.parter_school_id = partner_school.id
#                     center.save()
#                     print('Center with school_code %s is updated with partner_MySchool.' %school.school_code)
#             except MySchool.MultipleObjectsReturned:
#                 print('School with school_code %s is multiple times added to the partner_MySchool by %s.' %(school.school_code,partner.name))



# class Command(BaseCommand):
#     ''' Command for migrating all existing schools to partner_MySchool of respective partner and set parter_MySchool Id in place of School in Center table '''
#     def handle(self,*args, **kwargs):
#         partners = Partner.objects.all()
#         for partner in partners:
#             print('Im partner and my name is %s' %partner.name)
#             schools = School.objects.filter(created_by = partner.contactperson)
#             for school in schools:
#                 try:
#                     partner_school = MySchool.objects.get(school_id=school.id,school__school_code=school.school_code)
#                     print('School with school_code %s is already added to the partner_MySchool by %s.' %(school.school_code,partner.name))
#                 except MySchool.DoesNotExist:
#                     partner_school = MySchool.objects.create(partner=partner,school=school,status='Eligible',added_by_id=partner.contactperson_id)
#                     partner_school.save()
#                     print('School with school_code %s is added to the partner_MySchool by %s.' %(school.school_code,partner.name))
#                     centers = Center.objects.filter(school_id=school.id)
#                     for center in centers:
#                         center.school_id = partner_school.id
#                         center.save()
#                         print('Center with school_code %s is updated with partner_MySchool.' %(school.school_code,partner.name))
#                 except MySchool.MultipleObjectsReturned:
#                     print('School with school_code %s is multiple times added to the partner_MySchool by %s.' %(school.school_code,partner.name))
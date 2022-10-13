from django.db import models

from django.contrib.auth.models import User

class Partnertype(models.Model):
    name = models.CharField(max_length=30, blank=True)
    description = models.CharField(max_length=1024, null=True, blank=True)

    def __unicode__(self):
        return self.name

class Partner(models.Model):
    contactperson           = models.ForeignKey(User, null=True)
    name                    = models.CharField(max_length=50, db_index=True, blank=True)
    name_of_organization    = models.CharField(max_length=300, db_index=True)
    email                   = models.CharField(max_length=50, db_index=True)
    phone                   = models.CharField(max_length=50, blank=True)
    address                 = models.TextField(null=True, blank=True)
    partnertype             = models.ManyToManyField(Partnertype, related_name="partnertype", blank=True)
    status                  = models.CharField(max_length=50,
                            choices=(('New', 'New'), ('In Process', 'In Process'), ('Approved', 'Approved'), ('On Hold', 'On Hold'), ('Not Approved', 'Not Approved'),('Lead', 'Lead')), default = 'New')
    modified_by             = models.CharField(max_length=250, null = True, blank=True)
    dt_added                = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated              = models.DateTimeField(auto_now=True, null=True, blank=True)
    pam                     =models.ForeignKey(User,related_name="pamid", null=True)
    logo                    = models.FileField(upload_to='static/organisation/images', null=True, blank=True)
    role_id                 = models.CharField(max_length=11, null=True)
    teaching_software_id    = models.CharField(max_length=128, null=True, blank=True)
    is_test_user = models.BooleanField(default=False)
    source = models.CharField(max_length=10,null=True, choices=(('1', 'Web'), ('2', 'Mobile')), default="1")
    
    class Meta:
        unique_together = (('contactperson', 'email'),)

    def __unicode__(self):
        return self.name

class DeliveryPartnerOrgDetails(models.Model):
    partner                 = models.ForeignKey(Partner, null=True, related_name="delivery_partnerobj")
    type_of_org             = models.CharField(max_length=250, null = True, blank=True)
    website_address         = models.CharField(max_length=250, null = True, blank=True)
    office_phone            = models.CharField(max_length=250, null = True, blank=True)
    authorized_signatory    = models.CharField(max_length=250, null = True, blank=True)
    date_of_reg             = models.CharField(max_length=50, db_index=True,  blank=True)
    place_of_reg            = models.CharField(max_length=50, db_index=True,  blank=True)
    reg_number              = models.CharField(max_length=50, db_index=True,  blank=True)
    number                  = models.CharField(max_length=50, db_index=True,  blank=True)
    fcra_reg_number         = models.CharField(max_length=50, db_index=True,  blank=True)
    fcra_acc_number         = models.CharField(max_length=50, db_index=True,  blank=True)
    bank_name               = models.CharField(max_length=50, db_index=True,  blank=True)
    ifsc_code               = models.CharField(max_length=50, db_index=True,  blank=True)
    acc_holder_name         = models.CharField(max_length=50, db_index=True,  blank=True)
    acc_number              = models.CharField(max_length=50, db_index=True,  blank=True)
    type_of_acc             = models.CharField(max_length=50, db_index=True,  blank=True)
    dt_added                = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    dt_updated              = models.DateTimeField(auto_now=True, null=True, blank=True)


class MySchool(models.Model):
    partner = models.ForeignKey(Partner,null=True,related_name='partner_myschool')
    school = models.ForeignKey('web.School',null=True,related_name='partner_schoolmaster')
    status = models.CharField(max_length=64,choices=(('New','New'),('Verification in Progress','Verification in Progress'),('Verified','Verified'),('Eligible','Eligible'),('Not Eligible','Not Eligible')),default='New')
    added_by = models.ForeignKey(User,null=True,related_name='myschool_added_by')
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True, related_name='myschool_updated_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    remarks = models.CharField(max_length=1024,null=True) # Reason why Elegible/NotElebile to a partner by admin
    grades_in_school = models.CharField(max_length=256, null=True)
    teachers_available = models.CharField(max_length = 3, null=True)
    teachers_required = models.CharField(max_length = 3, null=True)
    electricity = models.BooleanField(default = True)
    computer = models.BooleanField(default = False)
    projector_or_led = models.BooleanField(default = False)
    internet = models.BooleanField(default = True)

    def __unicode__(self):
        return self.school.name

class MySchoolStatus(models.Model):
    myschool = models.ForeignKey(MySchool,null=True)
    verification_type = models.CharField(max_length=64,choices=(('Internet and Geo','Internet and Geo'),('eVidyaloka Verification','eVidyaloka Verification'),('Documents Verification','Documents Verification')))
    status = models.BooleanField()
    other_info = models.TextField(null=True,blank=True)  #Json meta info will be stored in the this table
    added_by = models.ForeignKey(User, null=True,related_name='myschool_status_added_by')
    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_by = models.ForeignKey(User, null=True,related_name='myschool_status_updated_by')
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)

class Partner_MOU(models.Model):
    partner = models.ForeignKey(User, null=True, related_name="partner_mou")
    partner_name=models.CharField(max_length=50, db_index=True,  blank=True)
    No_Of_schools =models.CharField(max_length=50, db_index=True,  blank=True)
    No_of_Coordinators =models.CharField(max_length=50, db_index=True,  blank=True)
    No_of_volunteer =models.CharField(max_length=50, db_index=True,  blank=True)
    estimated_cost=models.CharField(max_length=50, db_index=True,  blank=True)
    mou_value=models.CharField(max_length=50, db_index=True,  blank=True)
    Author_signature=models.CharField(max_length=50, db_index=True,  blank=True)
    Admin_signature=models.CharField(max_length=50, db_index=True,  blank=True)
    status=models.CharField(max_length=64,choices=(('partner_signed','partner_signed'),('complete','complete')),default='draft')
    Start_Date = models.DateTimeField( null=True, blank=True)

    added_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    updated_on = models.DateTimeField(auto_now=True, null=True, blank=True)
    No_Of_Months = models.CharField(max_length=50, null=True, blank=True)
    rate_of_coordinator = models.CharField(max_length=50, null=True, blank=True)
    rate_of_volunteer = models.CharField(max_length=50, null=True, blank=True)

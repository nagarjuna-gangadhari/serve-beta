from django.forms import ModelForm
from django.contrib.auth.models import User
from models import *
from django import forms
from web.models import Center

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('email', 'username')


class AddPartnerSchoolForm(forms.Form):
    pincode = forms.IntegerField(label='Pincode',min_value=100000,max_value=999999)
    schoolcode = forms.IntegerField(label='School Code')
    # omefield = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

class SavePartnerSchoolForm(forms.Form):
    partner = forms.IntegerField(label='',widget=forms.HiddenInput())
    school = forms.IntegerField(label='',widget=forms.HiddenInput())


class AddCenter(forms.Form):
    name = forms.CharField(label='Center Name',max_length=30,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    language = forms.ChoiceField(label='Language',choices=[x for x in Center._meta.get_field('language').choices],widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;height:32px; border-radius:4px;width: 100%;'}))
    board = forms.ChoiceField(label='Board',choices=[x for x in Center._meta.get_field('board').choices],widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;height:32px; border-radius:4px;'}))
    working_days = forms.CharField(label='Working Days',required=False,max_length=258,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    working_slots = forms.CharField(label='Working Slots',required=False,max_length=258,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    admin = forms.CharField(label='Admin',required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;'}))
    selected_admin = forms.CharField(required=False,widget=forms.HiddenInput())
    assistant = forms.CharField(label='Assistant',required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;'}))
    selected_assistant = forms.CharField(required=False, widget=forms.HiddenInput())
    photo = forms.ImageField(label='Center Photo',required=False,widget=forms.FileInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    description = forms.CharField(label="Description",max_length=2048,widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;','rows':3}))
    classlocation = forms.CharField(label='Class Location',max_length=250,required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    grades = forms.CharField(label='Grades',required=False,max_length=250,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    subjectscovered = forms.CharField(label='Subjects Covered',required=False,max_length=256,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    noofchildren = forms.IntegerField(label='Childrens',required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    status = forms.ChoiceField(label='Status',required=False,choices=[x for x in Center._meta.get_field('status').choices],widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;height:32px; border-radius:4px;'}))
    launchdate = forms.DateField(label='Launch Date',required=False,widget=forms.DateInput(format=('%Y-%m-%d'),attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    donor_name = forms.CharField(label='Donor Name',required=False,max_length='128',widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    skype_id = forms.CharField(label="Skype ID",required=False,max_length='128',widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    location_map = forms.CharField(label='Map Location',max_length=1024,widget=forms.Textarea(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;','rows':3}),required=False)
    ops_donor_name = forms.CharField(label='Ops Donar Name',required=False,max_length=256,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    funding_partner = forms.ModelChoiceField(label='Funding Partner',required=False,queryset=Partner.objects.filter(partnertype__id=Partnertype.objects.get(name='Funding Partner').id),empty_label="Select Funding Partner",widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;height:32px; border-radius:4px;'}))
    delivery_partner = forms.ModelChoiceField(label='Delivery Partner',queryset=Partner.objects.filter(partnertype__id=Partnertype.objects.get(name='Delivery Partner').id),empty_label="Select Delivery Partner",widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;width: 100%;height:32px; border-radius:4px;'}))
    field_coordinator =  forms.CharField(label='Field Co-ordinator',required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;'}))
    selected_field_coordinator = forms.CharField(required=False, widget=forms.HiddenInput())
    delivery_coordinator =  forms.CharField(label='Delivery Co-ordinator',required=False,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;'}))
    selected_delivery_coordinator = forms.CharField(required=False, widget=forms.HiddenInput())
    hm = forms.CharField(label='Head Master',required=False, max_length=128,widget=forms.TextInput(attrs={'class':'form-control','style':'display:inline !important;max-width: 57%;margin-bottom:unset;'}))
    partner_school = forms.ModelChoiceField(label='School',queryset=MySchool.objects.filter(status='Eligible'),empty_label="Select School",widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;height:32px; border-radius:4px;'}))
    orgunit_partner = forms.ModelChoiceField(label='Org Partner',queryset=Partner.objects.filter(partnertype__id=Partnertype.objects.get(name='Organization Unit').id),empty_label="Select Org Partner",widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;height:32px; border-radius:4px;'}),required=False)
    program_type = forms.ChoiceField(label='Program Type',choices=[x for x in Center._meta.get_field('program_type').choices],widget=forms.Select(attrs={'style':'display:inline !important;min-width: 160px;max-width: 57%;margin-bottom:unset;height:32px; border-radius:4px;width: 100%;'}))

def get_center_data(center):
    if center:
        data = {}
        data['name'] = center.name
        data['language'] = center.language
        data['board'] = center.board
        data['working_days'] = center.working_days
        data['working_slots'] = center.working_slots
        if center.admin:
            data['admin'] = center.admin.first_name + center.admin.last_name
            data['selected_admin'] = center.admin.id
        else:
            data['admin'] = None
            data['selected_admin'] = None
        if center.assistant:
            data['assistant'] = center.assistant.first_name + center.assistant.last_name
            data['selected_assistant'] = center.assistant.id
        else:
            data['assistant'] = None
            data['selected_assistant'] = None
        data['description'] = center.description
        data['classlocation'] = center.classlocation
        data['grades'] = center.grades
        data['subjectscovered'] = center.subjectscovered
        data['noofchildren'] = center.noofchildren
        data['status'] = center.status
        data['launchdate'] = center.launchdate
        data['skype_id'] = center.skype_id
        data['location_map'] = center.location_map
        data['funding_partner'] = center.funding_partner
        data['delivery_partner'] = center.delivery_partner
        data['orgunit_partner'] = center.orgunit_partner
        if center.field_coordinator:
            data['field_coordinator'] = center.field_coordinator.first_name + center.field_coordinator.last_name
            data['selected_field_coordinator'] = center.field_coordinator.id
        else:
            data['field_coordinator'] = None
            data['selected_field_coordinator'] = None
        if center.delivery_coordinator:
            data['delivery_coordinator'] = center.delivery_coordinator.first_name + center.delivery_coordinator.last_name
            data['selected_delivery_coordinator'] = center.delivery_coordinator.id
        else:
            data['delivery_coordinator'] = None
            data['selected_delivery_coordinator'] = None
        data['hm'] = center.HM
        data['partner_school'] = center.partner_school
        return data
    else:
        return None
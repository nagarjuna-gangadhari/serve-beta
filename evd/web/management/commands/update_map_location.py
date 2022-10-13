import xlrd
from web.models import Center
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    def handle(self, *args, **options):
        invalid_center=0
        valid_center=0
        list1=[]
        invalid_center_list=[]
        wb = xlrd.open_workbook(args[0])
        sheet = wb.sheet_by_index(0)
        for row in range(1,int(sheet.nrows)):
            dict1={
                "id":str(sheet.cell_value(row, 1)).strip(),
                "center_idtype":type(sheet.cell_value(row, 1)),
                "center_name":str(sheet.cell_value(row, 0)).strip(),
                "location_link":str(sheet.cell_value(row, 3)).strip()
                }
            list1.append(dict1);
        for each_dict in list1:
            try:
                existed_center=Center.objects.get(id=int(float(each_dict['id'])))
                if existed_center:
                    valid_center+=1
                    existed_center.location_map = each_dict['location_link']
                    existed_center.save()
            except:
                invalid_center+=1
                invalid_center_list.append(each_dict['center_name'])
        #print 'invalid_list',invalid_center_list


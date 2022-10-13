import csv
from django.core.management.base import BaseCommand, CommandError
from web.models import School

class Command(BaseCommand):
    def handle(self, *args,**kwargs):
        csv_file = args[0]
        fname = csv_file.split('/')[-1].split('.')[0]
        filename = fname + '_errors.csv'
        alldata = []
        print csv_file
        with open(csv_file,'rb') as csvf:
            data = csv.reader(csvf, delimiter=',', quotechar='|')
            next(data, None)
            for row in data:
                if row[0]=='':
                    print('ID is empty for ID '+row[0]+' School name :'+row[1])
                    alldata.append(row)
                elif row[2]=='':
                    print('school code is empty for ID '+row[0]+' School name :'+row[1])
                    alldata.append(row)
                elif row[3] =='':
                    print('pincode is empty for ID '+row[0]+' School name :'+row[1])
                    alldata.append(row)
                else:
                    try:
                        school = School.objects.only('id','name','school_code','pincode','village','district_details').get(id=int(row[0]))
                        school.school_code=int(row[2])
                        school.pincode=int(row[3])
                        school.save()
                        print('School is updated '+str(school.id)+' '+str(school.school_code)+' '+str(school.pincode))
                    except School.DoesNotExist:
                        print('Error Occured '+row[0]+' '+row[1] +' '+row[2] +' '+row[3])
                        alldata.append(row)
                        pass
        failcsvfile = open('errorfiles/' + filename, 'w')
        writer = csv.writer(failcsvfile)
        writer.writerows(alldata)
        failcsvfile.close()
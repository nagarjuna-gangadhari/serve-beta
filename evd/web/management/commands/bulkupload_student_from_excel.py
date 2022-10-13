from django.core.management.base import BaseCommand
from web.models import Student
import xlrd


class Command(BaseCommand):
    def handle(self, *args, **options):
        path = args[0]
        wb = xlrd.open_workbook(path)
        sheet = wb.sheet_by_index(0)
        for i in range(1,sheet.nrows):
            row = sheet.row_values(i)
            name = row[0].strip()
           
            # dob = row[1]
            center_id = row[2]
            gender=row[3]
            grade = int(row[4])
            father_occupation = row[5]
            mother_occupation = row[6]
            strengths=row[7]
            weakness=row[8]
            observation=row[9]
            photo=row[10]
            status=row[11]
            school_rollno=int(row[12])
            student = Student.objects.create(name=name,center_id=center_id,gender=gender,grade=grade,father_occupation=father_occupation,mother_occupation=mother_occupation,strengths=strengths,weakness=weakness,observation=observation,school_rollno=school_rollno)
            
        

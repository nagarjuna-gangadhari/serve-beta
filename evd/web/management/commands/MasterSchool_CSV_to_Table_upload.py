from django.core.management.base import BaseCommand, CommandError
import pandas as pd
import numpy as np
from web.models import School
import math
import csv

def conv(val,obtype='float'):
    if obtype=='int':
        if not val:
            return 0
        if isinstance(val, basestring):
            if ',' in val:
                val = val.replace(',','')
            if '(' in val:
                val = val.replace('(','')
            if ')' in val:
                val = val.replace(')','')

        try:
            if math.isnan(float(val)):
                return np.int32(0)
            return np.int32(val)
        except:
            return np.int32(0)
    else:
        if not val:
            return 0.0
        if isinstance(val, basestring):
            if ',' in val:
                val = val.replace(',','')
            if '(' in val:
                val = val.replace('(','')
            if ')' in val:
                val = val.replace(')','')

        try:
            if math.isnan(float(val)):
                return np.float64(0)
            return np.float64(val)
        except:
            return np.float64(0)


class Command(BaseCommand):
    def handle(self,*args, **kwargs):
        # print(args[0].split('/')[-1].split('.'))
        for csvfile in args:
            fname = csvfile.split('/')[-1].split('.')[0]
            filename = fname + '_errors.csv'
            print('file path name',csvfile)
            alldata = []
            failcsvfile = open('errorfiles/'+filename,'w')
            with open(csvfile) as f:
                csv_data = pd.read_csv(f,error_bad_lines=False,keep_default_na=False, na_values=[""])
                for row in csv_data.values:
                    if (row[2] != 'nan' or row[2] != None or row[2] != '' or row[2] != float('NaN') or math.isnan(float(row[2])) != True) and (row[11] != 'nan' or row[11] != None or row[11] != '' or row[11] != float('NaN') or math.isnan(float(row[11])) != True):
                        try:
                            # print('school_code',row[2],'type:',type(row[2]),'pincode',row[11],'type:',type(row[11]))
                            myschool = School.objects.only('id','name','school_code','pincode').get(school_code=row[2],pincode=int(row[11]))
                            # write row information into the file
                            # failed_file.write(str(row) + '\n' + '\n')
                            row1 = row.tolist()
                            row1.insert(0,'already added')
                            alldata.append(row1)
                            print('object added already','school_code:',row[2],'pincode:',row[11])
                        except School.DoesNotExist:
                            myschool = School.objects.create(ref_url=row[0],school_academic_year=row[1],school_code=row[2],name=str(row[3]),state=row[4],district_details=row[5],block=row[6],cluster=str(row[7]),village=row[8],principal=row[9],\
                                                             location=row[10],pincode=row[11],school_category=str(row[12]),type_of_school=row[15],management=str(row[16]),approachable_by_all_weather_road=row[17], \
                                                             special_school_for_cwsn=row[21],shift_school=row[22],residential_school=row[23],type_of_residential_school=row[24],pre_primary_section=row[25], \
                                                             head_master=row[41],medium_one=row[49],medium_two=row[50],medium_three=row[51],status_of_school_building=row[52],boundary_wall=row[53],furniture_for_students=row[55], \
                                                             separate_room_for_HM=row[60],electricity_connection=row[61],cwsn_friendly_toilet=row[66],drinking_water_facility=row[67],drinking_water_functional=row[68],library_facility=row[69], \
                                                             computer_aided_learning_lab=str(row[71]),playground_facility=str(row[72]),land_available_for_playground=str(row[73]),no_of_computers_functional=str(row[75]),medical_check=str(row[76]),ramp_for_disabled_needed=str(row[77]),ramp_available=str(row[78]),hand_rails_for_ramp=str(row[79]))

                            lowest_class = conv(row[13],'int')
                            highest_class = conv(row[14],'int')
                            year_of_establishment = conv(row[18],'int')
                            year_of_recognition = conv(row[19],'int')
                            year_of_upgradation_p_to_up = conv(row[20],'int')
                            total_students_pre_primary = conv(row[26],'int')
                            total_teachers_pre_primary = conv(row[27],'int')
                            academic_inspections = conv(row[28],'int')
                            no_of_visits_by_crc_coordinator = conv(row[29],'int')
                            no_of_visits_by_block_level_officer = conv(row[30],'int')
                            school_development_grant_receipt = conv(row[31],'int')
                            school_development_grant_expenditure = conv(row[32],'int')
                            school_maintenance_grant_receipt = conv(row[33],'int')
                            school_maintenance_grant_expenditure = conv(row[34],'int')
                            regular_Teachers = conv(row[35],'int')
                            contract_teachers = conv(row[36],'int')
                            graduate_or_above = conv(row[37],'int')
                            teachers_male = conv(row[38],'int')
                            teachers_female = conv(row[39],'int')
                            teachers_aged_above = conv(row[40],'int')
                            trained_for_teaching_cwsn = conv(row[42],'int')
                            trained_in_use_of_computer = conv(row[43],'int')
                            part_time_instructor = conv(row[44],'int')
                            teachers_involved_in_non_teaching_assignments = conv(row[45],'int')
                            avg_working_days_spent_on_Non_tch_assignments = conv(row[46],'int')
                            teachers_with_professional_qualification = conv(row[47],'int')
                            teachers_received_inservice_training = conv(row[48],'int')
                            classrooms_for_teaching = conv(row[54],'int')
                            number_of_other_rooms = conv(row[56],'int')
                            classrooms_in_good_condition = conv(row[57],'int')
                            classrooms_require_minor_repair = conv(row[58],'int')
                            classrooms_require_major_repair = conv(row[59],'int')
                            boys_toilet_seats_total = conv(row[62],'int')
                            boys_toilet_seats_functional = conv(row[63],'int')
                            girls_toilet_seats_total = conv(row[64],'int')
                            girls_toilet_seats_functional = conv(row[65],'int')



                            no_of_books_in_school_library = conv(row[70],'int')
                            no_of_computers_available = conv(row[74],'int')
                            classroom_required_major_repair = conv(row[80])
                            teachers_with_prof_qualification = conv(row[81])
                            muslim_girls_to_muslim_enrolment = conv(row[82])
                            repeaters_to_total_enrolment = conv(row[83])
                            change_in_enrolment_over_previous_year = conv(row[84])
                            sc_girls_to_sc_enrolment = conv(row[85])
                            st_girls_to_st_enrolment = conv(row[86])
                            pupil_teacher_ratio = conv(row[87])
                            student_classroom_ratio = conv(row[88])
                            girls_enrolment = conv(row[89])

                            muslim_students = conv(row[90])
                            sc_students = conv(row[91])
                            st_students = conv(row[92])
                            obc_enrolment = conv(row[93])

                            myschool.lowest_class = lowest_class
                            myschool.highest_class = highest_class
                            myschool.year_of_establishment = year_of_establishment
                            myschool.year_of_recognition = year_of_recognition
                            myschool.year_of_upgradation_p_to_up = year_of_upgradation_p_to_up
                            myschool.total_students_pre_primary = total_students_pre_primary
                            myschool.total_teachers_pre_primary = total_teachers_pre_primary
                            myschool.academic_inspections = academic_inspections
                            myschool.no_of_visits_by_crc_coordinator = no_of_visits_by_crc_coordinator
                            myschool.no_of_visits_by_block_level_officer = no_of_visits_by_block_level_officer
                            myschool.school_development_grant_receipt = school_development_grant_receipt
                            myschool.school_development_grant_expenditure = school_development_grant_expenditure
                            myschool.regular_Teachers = regular_Teachers
                            myschool.contract_teachers = contract_teachers
                            myschool.graduate_or_above = graduate_or_above
                            myschool.teachers_male = teachers_male
                            myschool.teachers_female = teachers_female
                            myschool.teachers_aged_above = teachers_aged_above
                            myschool.trained_for_teaching_cwsn = trained_for_teaching_cwsn
                            myschool.trained_in_use_of_computer = trained_in_use_of_computer
                            myschool.part_time_instructor = part_time_instructor
                            myschool.teachers_involved_in_non_teaching_assignments = teachers_involved_in_non_teaching_assignments
                            myschool.avg_working_days_spent_on_Non_tch_assignments = avg_working_days_spent_on_Non_tch_assignments
                            myschool.teachers_with_professional_qualification = teachers_with_professional_qualification
                            myschool.teachers_received_inservice_training = teachers_received_inservice_training
                            myschool.classrooms_for_teaching = classrooms_for_teaching
                            myschool.number_of_other_rooms = number_of_other_rooms
                            myschool.classrooms_in_good_condition = classrooms_in_good_condition
                            myschool.classrooms_require_minor_repair = classrooms_require_minor_repair
                            myschool.classrooms_require_major_repair = classrooms_require_major_repair
                            myschool.boys_toilet_seats_total = boys_toilet_seats_total
                            myschool.boys_toilet_seats_functional = boys_toilet_seats_functional
                            myschool.girls_toilet_seats_total = girls_toilet_seats_total
                            myschool.girls_toilet_seats_functional = girls_toilet_seats_functional
                            myschool.muslim_students = muslim_students
                            myschool.sc_students = sc_students
                            myschool.st_students = st_students
                            myschool.obc_enrolment = obc_enrolment
                            myschool.classroom_required_major_repair = classroom_required_major_repair
                            myschool.teachers_with_prof_qualification = teachers_with_prof_qualification
                            myschool.muslim_girls_to_muslim_enrolment = muslim_girls_to_muslim_enrolment
                            myschool.repeaters_to_total_enrolment = repeaters_to_total_enrolment
                            myschool.change_in_enrolment_over_previous_year = change_in_enrolment_over_previous_year
                            myschool.sc_girls_to_sc_enrolment = sc_girls_to_sc_enrolment
                            myschool.st_girls_to_st_enrolment = st_girls_to_st_enrolment
                            myschool.pupil_teacher_ratio = pupil_teacher_ratio
                            myschool.student_classroom_ratio = student_classroom_ratio
                            myschool.girls_enrolment = girls_enrolment
                            myschool.no_of_books_in_school_library = no_of_books_in_school_library
                            myschool.no_of_computers_available = no_of_computers_available
                            myschool.school_maintenance_grant_receipt = school_maintenance_grant_receipt
                            myschool.school_maintenance_grant_expenditure = school_maintenance_grant_expenditure
                            myschool.save()
                            print ('data saved successfully', 'school_code:', row[2])
                        except School.MultipleObjectsReturned:
                            print('multiple objects returned','school_code:',row[2],'pincode:',row[11])
                            # write row information into the file
                            # failed_file.write(str(row) + '\n' + '\n')
                            row1 = row.tolist()
                            row1.insert(0, 'Multiple Objects')
                            alldata.append(row1)
                            continue
                        except ValueError:
                            print('value error occured','school_code:',row[2],'pincode:',row[11])
                            # write row information into the file
                            # failed_file.write(str(row) + '\n' + '\n')
                            row1 = row.tolist()
                            row1.insert(0, 'Value Error')
                            alldata.append(row1)
                            continue
                        except pd.errors.ParserError:
                            print('pandas ParserError occured','school_code:',row[2],'pincode:',row[11])
                            # write row information into the file
                            # failed_file.write(str(row) + '\n' + '\n')
                            row1 = row.tolist()
                            row1.insert(0, 'Parse Error')
                            alldata.append(row1)
                            continue
                        except Exception as e:
                            errortype = e.message.split('.')[0].strip()
                            if errortype == 'Error tokenizing data':
                                print('pandas ParserError occured', 'school_code:', row[2], 'pincode:', row[11])
                                # failed_file.write(str(row) + '\n' + '\n')
                                row1 = row.tolist()
                                row1.insert(0, 'Exception')
                                alldata.append(row1)
                                continue
                            else:
                                print('Unknown Error occured', 'school_code:', row[2], 'pincode:', row[11])
                                # failed_file.write(str(row) + '\n' + '\n')
                                row1 = row.tolist()
                                row1.insert(0, 'Exception')
                                alldata.append(row1)
                                continue
                    else:
                        print('value is not a number','school_code:', row[2], 'pincode:', row[11])
                        # write row information into the file
                        # failed_file.write('Failed due to NaN in Schoolcode or Pincode. ' + str(row) + '\n' + '\n')
                        row1 = row.tolist()
                        row1.insert(0, 'failed in if test')
                        alldata.append(row1)
                        continue
            # failed_file.close()
            # alld = [[d if d=='nan' for d in dat] for dat in alldata ]
            writer = csv.writer(failcsvfile)
            writer.writerows(alldata)
            failcsvfile.close()



# class Command(BaseCommand):
#     def handle(self,*args, **kwargs):
#         print('im printing arguments:',args)
#         print(args[0].split('/')[-1].split('.'))
#         print('im printing Keyword arguments',kwargs)
#         failed_file = open('failed.txt','w')
#         with open(args[0]) as f:
#             csv_data = pd.read_csv(f)
#             i=0
#             for row in csv_data.values:
#                 if (row[2] != 'nan' or row[2] != None or row[2] != '' or row[2] != float('NaN')) and (row[11] != 'nan' or row[11] != None or row[11] != '' or row[11] != float('NaN')):
#                     try:
#                         # print('school_code',row[2],'type:',type(row[2]),'pincode',row[11],'type:',type(row[11]))
#                         myschool = School.objects.only('id','name','school_code','pincode').get(school_code=row[2],pincode=int(row[11]))
#                         # write row information into the file
#                         failed_file.write(str(row))
#                         # print('object added already',row)
#                     except School.DoesNotExist:
#                         print 'data saved successfully'
#                         # myschool = School.objects.create()
#                         # myschool.save()
#                     except School.MultipleObjectsReturned:
#                         # print('multiple objects returned',row)
#                         # write row information into the file
#                         failed_file.write(str(row))
#                     except ValueError:
#                         # print('value error occured',row)
#                         # write row information into the file
#                         failed_file.write(str(row))
#                 else:
#                     # print('value is not a number',row)
#                     # write row information into the file
#                     failed_file.write(str(row))
#                 i+=1
#             # for chunk in csv_data:
#             #     print (chunk)
#         #     for row in csv_data.iterrows():
#         #         print(row)
#         #         failed_file.write(str(row[1]))
#         # failed_fi
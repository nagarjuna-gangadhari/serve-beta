from django.core.management.base import BaseCommand, CommandError
from web.models import School

class Command(BaseCommand):
    def handle(self, *args,**kwargs):
        schools = School.objects.exclude(school_code=0)
        old_schools = schools.filter(created_by_id__isnull = False)
        # print 'old school count',old_schools.count()
        new_schools = schools.exclude(created_by_id__isnull = False)
        # print 'count of new schools', new_schools.count()
        del_schools = []
        for osc in old_schools:
            try:
                dup_schools = new_schools.get(school_code=osc.school_code,pincode=osc.pincode)
                if int(dup_schools.id) not in del_schools:
                    del_schools.append(int(dup_schools.id))
                # osc.name = dup_schools.name
                osc.district_details = dup_schools.district_details
                osc.ref_url = dup_schools.ref_url
                osc.school_academic_year = dup_schools.school_academic_year
                osc.state = dup_schools.state
                osc.block = dup_schools.block
                osc.cluster = dup_schools.cluster
                osc.village = dup_schools.village
                if dup_schools.principal != 'nan':
                    osc.principal = dup_schools.principal
                osc.location = dup_schools.location
                osc.school_category = dup_schools.school_category
                osc.lowest_class = dup_schools.lowest_class
                osc.highest_class = dup_schools.highest_class
                osc.type_of_school = dup_schools.type_of_school
                osc.management = dup_schools.management
                osc.approachable_by_all_weather_road = dup_schools.approachable_by_all_weather_road
                osc.year_of_establishment = dup_schools.year_of_establishment
                osc.year_of_recognition = dup_schools.year_of_recognition
                osc.year_of_upgradation_p_to_up = dup_schools.year_of_upgradation_p_to_up
                osc.special_school_for_cwsn = dup_schools.special_school_for_cwsn
                osc.shift_school = dup_schools.shift_school
                osc.residential_school = dup_schools.residential_school
                if dup_schools.type_of_residential_school != 'nan':
                    osc.type_of_residential_school = dup_schools.type_of_residential_school
                osc.pre_primary_section = dup_schools.pre_primary_section
                osc.total_students_pre_primary = dup_schools.total_students_pre_primary
                osc.total_teachers_pre_primary = dup_schools.total_teachers_pre_primary
                osc.academic_inspections = dup_schools.academic_inspections
                osc.no_of_visits_by_crc_coordinator = dup_schools.no_of_visits_by_crc_coordinator
                osc.no_of_visits_by_block_level_officer = dup_schools.no_of_visits_by_block_level_officer
                osc.school_development_grant_receipt = dup_schools.school_development_grant_receipt
                osc.school_development_grant_expenditure = dup_schools.school_development_grant_expenditure
                osc.school_maintenance_grant_receipt = dup_schools.school_maintenance_grant_receipt
                osc.school_maintenance_grant_expenditure = dup_schools.school_maintenance_grant_expenditure
                osc.regular_Teachers = dup_schools.regular_Teachers
                osc.contract_teachers = dup_schools.contract_teachers
                osc.graduate_or_above = dup_schools.graduate_or_above
                osc.teachers_male = dup_schools.teachers_male
                osc.teachers_female = dup_schools.teachers_female
                osc.teachers_aged_above = dup_schools.teachers_aged_above
                osc.head_master = dup_schools.head_master
                osc.trained_for_teaching_cwsn = dup_schools.trained_for_teaching_cwsn
                osc.trained_in_use_of_computer = dup_schools.trained_in_use_of_computer
                osc.part_time_instructor = dup_schools.part_time_instructor
                osc.teachers_involved_in_non_teaching_assignments = dup_schools.teachers_involved_in_non_teaching_assignments
                osc.avg_working_days_spent_on_Non_tch_assignments = dup_schools.avg_working_days_spent_on_Non_tch_assignments
                osc.teachers_with_professional_qualification = dup_schools.teachers_with_professional_qualification
                osc.teachers_received_inservice_training = dup_schools.teachers_received_inservice_training
                if dup_schools.medium_one != 'nan':
                    osc.medium_one = dup_schools.medium_one
                if dup_schools.medium_two != 'nan':
                    osc.medium_two = dup_schools.medium_two
                if dup_schools.medium_three != 'nan':
                    osc.medium_three = dup_schools.medium_three
                osc.status_of_school_building = dup_schools.status_of_school_building
                osc.boundary_wall = dup_schools.boundary_wall
                osc.classrooms_for_teaching = dup_schools.classrooms_for_teaching
                osc.furniture_for_students = dup_schools.furniture_for_students
                osc.number_of_other_rooms = dup_schools.number_of_other_rooms
                osc.classrooms_in_good_condition = dup_schools.classrooms_in_good_condition
                osc.classrooms_require_minor_repair = dup_schools.classrooms_require_minor_repair
                osc.classrooms_require_major_repair = dup_schools.classrooms_require_major_repair
                osc.separate_room_for_HM = dup_schools.separate_room_for_HM
                osc.electricity_connection = dup_schools.electricity_connection
                osc.boys_toilet_seats_total = dup_schools.boys_toilet_seats_total
                osc.boys_toilet_seats_functional = dup_schools.boys_toilet_seats_functional
                osc.girls_toilet_seats_total = dup_schools.girls_toilet_seats_total
                osc.girls_toilet_seats_functional = dup_schools.girls_toilet_seats_functional
                osc.cwsn_friendly_toilet = dup_schools.cwsn_friendly_toilet
                osc.drinking_water_facility = dup_schools.drinking_water_facility
                osc.drinking_water_functional = dup_schools.drinking_water_functional
                osc.library_facility = dup_schools.library_facility
                osc.no_of_books_in_school_library = dup_schools.no_of_books_in_school_library
                osc.computer_aided_learning_lab = dup_schools.computer_aided_learning_lab
                osc.playground_facility = dup_schools.playground_facility
                osc.land_available_for_playground = dup_schools.land_available_for_playground
                osc.no_of_computers_available = dup_schools.no_of_computers_available
                osc.no_of_computers_functional = dup_schools.no_of_computers_functional
                osc.medical_check = dup_schools.medical_check
                osc.ramp_for_disabled_needed = dup_schools.ramp_for_disabled_needed
                osc.ramp_available = dup_schools.ramp_available
                osc.hand_rails_for_ramp = dup_schools.hand_rails_for_ramp
                osc.classroom_required_major_repair = dup_schools.classroom_required_major_repair
                osc.teachers_with_prof_qualification = dup_schools.teachers_with_prof_qualification
                osc.muslim_girls_to_muslim_enrolment = dup_schools.muslim_girls_to_muslim_enrolment
                osc.repeaters_to_total_enrolment = dup_schools.repeaters_to_total_enrolment
                osc.change_in_enrolment_over_previous_year = dup_schools.change_in_enrolment_over_previous_year
                osc.sc_girls_to_sc_enrolment = dup_schools.sc_girls_to_sc_enrolment
                osc.st_girls_to_st_enrolment = dup_schools.st_girls_to_st_enrolment
                osc.pupil_teacher_ratio = dup_schools.pupil_teacher_ratio
                osc.student_classroom_ratio = dup_schools.student_classroom_ratio
                osc.girls_enrolment = dup_schools.girls_enrolment
                osc.muslim_students = dup_schools.muslim_students
                osc.sc_students = dup_schools.sc_students
                osc.st_students = dup_schools.st_students
                osc.obc_enrolment = dup_schools.obc_enrolment
                osc.save()


                # print 'count of duplicate schools', dup_schools,'school_code',osc.school_code, 'pincode', osc.pincode
                # for ds in dup_schools:
                #     print ds.id,ds.name,ds.school_code
            except School.DoesNotExist:
                # print 'no school found with school_code',osc.school_code
                pass
        # print del_schools
        for id in del_schools:
            delsc = School.objects.get(id=id)
            # print 'school is going to delete: ',delsc.name
            delsc.delete()

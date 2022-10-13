from django.core.management.base import BaseCommand, CommandError
from web.models import *
from evd import settings
import datetime
from django.core.exceptions import ObjectDoesNotExist

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('board_to_center_script.log', 'a+') as lg:

            center_objs = Center.objects.all()
            count = 0
            for center_obj in center_objs:
                state = center_obj.state.lower()
                count += 1
                if state == 'tamil nadu':
                    board = 'TNSB'
                elif state == 'andhra pradesh':
                    board = 'APSB'
                elif state == 'jharkhand':
                    board = 'NCERT'
                elif state == 'karnataka':
                    board = 'DSERT'
                elif state == 'assam':
                    board = 'NCERT'
                elif state == 'west bengal':
                    board = 'WBSED'
                elif state == 'maharashtra':
                    board = 'MHSB'
                elif state == 'telengana':
                    board = 'APSB'

                center_obj.board = board
                center_obj.save()
                lg.write(state + "\n")
                print state + " ::::: " + board + "\n\n"
            lg.write("\n\ntotal ::: " + str(count))
            print "total :::: " + str(count)

        return "success"

__author__ = 'Administrator'
import csv
from question.models import TestCaseSet,TestCase

class TestCaseDataImporter(object):
    def __init__(self,source):
        """
        :param source: a file object
        :return:
        """
        self.source=source

    def import_to_database(self,question):
        """
        :return: (successful:boolean)
        """
        reader=csv.DictReader(self.source)
        current_test_case_set=None
        try:
            for row in reader:
                row_copy=row.copy()
                for key in row_copy.keys():
                    row_copy[key]=row_copy[key].replace("\\n","\n")
                if (len(row_copy["title"])>0):
                    # this is creating test case sets along with test cases
                    tcs=TestCaseSet()
                    tcs.__dict__.update(row_copy)
                    tcs.question=question
                    tcs.save()
                    current_test_case_set=tcs
                if (current_test_case_set):
                    tc=TestCase()
                    tc.__dict__.update(row_copy)
                    tc.testcase_set=current_test_case_set
                    tc.save()
        except:
            return False

        return True

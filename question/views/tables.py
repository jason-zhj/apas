__author__ = 'Administrator'

from appglobal.tables import BaseTable
from django.core.urlresolvers import reverse

class TestCaseSetTable(BaseTable):
    def get_delete_url(self,item):
        return reverse("test_case_set_delete_selected",args=[item.question.slug])
from abc import ABCMeta,abstractmethod
import csv

__all__=('CsvImporter',)

class CsvImporter(object):
    __metaclass__=ABCMeta
    # to indicate result importing one row
    _UPDATED=0
    _CREATED=1
    _FAILED=2
    # required field names for the csv file
    field_names=[]

    def __init__(self,source):
        """
        :param source: a file object
        :return:
        """
        self.source=source

    def import_to_database(self):
        """
        :return: (successful:boolean,result:string)
        """
        reader=csv.DictReader(self.source)
        if (not self._is_fields_valid(reader.fieldnames)):
            return False,"Some required fields are missing"

        update_counter=create_counter=failed_counter=0
        for row in reader:
            result=self._handle_row(row)
            if (result==self._FAILED):
                failed_counter +=1
            elif(reader==self._UPDATED):
                update_counter +=1
            else:
                create_counter +=1
        msg="{} items created, {} items updated, {} items failed to be imported".format(create_counter,update_counter,failed_counter)
        return (True,msg) if (update_counter>0 or create_counter>0) else (False,msg)

    @abstractmethod
    def _handle_row(self,row):
        return self._FAILED

    def _is_fields_valid(self,fields):
        for item in self.field_names:
            if (item not in fields):
                return False
        return True

class CSVFieldNotValidException(Exception):
    pass
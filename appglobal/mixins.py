class NameFormatMixin(object):
    def _format_field_name(self,name):
        # strip off the "get"
        pos=name.find("get_")
        if (pos !=-1):
            name=name[pos+4:]
        # replace underscores
        name=name.replace("_"," ")
        # capitalize first letter
        return name.title()

    def _get_normalized_class_name(self,datum):
        # get normalized class name
        class_name=datum.__class__.__name__
        normalized_class_name=class_name[0].lower()
        for i in range(1,len(class_name)):
            if (class_name[i].isupper()):
                normalized_class_name += "_"
            normalized_class_name+=class_name[i].lower()
        return normalized_class_name

    def _normalized_field_names(self,field_names):
        return [self._format_field_name(name) for name in field_names]


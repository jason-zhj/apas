import os
import uuid
import importlib
from apassite.settings import DEFAULT_SUMMARIZER_CLASS

def call_or_none(obj,method_name):
    if (hasattr(obj,method_name)):
        return getattr(obj,method_name)()
    return None

def get_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def save_uploaded_file(file,filedir,filename):
    """
    :param file: request.FILES
    :param filename: not including complete path
    :return: the complete path of the saved file
    """
    path=os.path.join(filedir,filename)
    with open(path, 'w') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return path

def generate_unique_file_name(extension="txt"):
    return str(uuid.getnode()) + "." + extension

def get_class_from_string(class_str):
    """
    :param class_str: a complete class string (including module name)
    :return: the class
    """
    tokens=class_str.split(".")
    module_name=".".join(tokens[:-1])
    class_name=tokens[-1]
    module = importlib.import_module(module_name)
    class_=getattr(module, class_name)
    return class_

def get_summary(source,fields):
    summarizer_class=get_class_from_string(DEFAULT_SUMMARIZER_CLASS)
    summarizer=summarizer_class(source=source,
                                fields=fields)
    return summarizer.get_summary()


def normalize_score(score):
    """
    :param score: score in double
    :return: score in int
    """
    if (score>98):
        return 100
    else:
        return int(score)
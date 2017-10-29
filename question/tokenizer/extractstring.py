class StringConstantExtractor(object):

    def __init__(self,code):
        self.code=code

    def get_string_constant_list(self):
        constant_list=[]
        temp=""
        in_quote=False
        in_escape=False
        #---------------process the code--------------------
        for c in self.code:
            if (not in_quote):
                if (c=='"'):
                    in_quote=True
            else:
                # in quote
                if (not in_escape):
                    if (c=='"'):
                        if (temp.strip()):
                            constant_list.append(temp.strip())
                            temp=""
                        in_quote=False
                    elif(c=="%"):
                        in_escape=True
                        if (temp.strip()):
                            constant_list.append(temp.strip())
                            temp=""
                    else:
                        temp +=c
                else:
                    # in quote and also in escape
                    if (c=='"'):
                        in_escape=False
                        in_quote=False
                    elif(c.isalpha()):
                        in_escape=False
        #-------------------------end process the code------------------------
        return list(set(constant_list))

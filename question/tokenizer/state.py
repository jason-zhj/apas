from abc import ABCMeta,abstractmethod
"""
State classes to be used in code tokenization
"""

class State(object):
    """
    Abstract class for creating State
    """
    __metaclass__=ABCMeta

    def __init__(self,machine):
        self.machine=machine

    @abstractmethod
    def get_name(self):
        return "State"

    @abstractmethod
    def process_input(self,input):
        pass


"""
Here we assume that the language only allows using double quote to enclose a string
"""
class QuoteState(State):
    def get_name(self):
        return "Quote State"

    def process_input(self,input):

        if (input=='"'):
            # end of the quote
            self.machine.set_current_state(self.machine.whitespace_state)


class AlphaNumbericState(State):
    def get_name(self):
        return "Alpha Numberic State"

    def process_input(self,input_char):

        if (input_char.isalnum()):
            self.machine.set_temp(self.machine.get_temp()+input_char)

        elif(input_char in self.machine.get_operand_character_list()):
            # end of alpha_numeric word
            alpha_numeric_str=self.machine.get_temp()
            if (alpha_numeric_str in self.machine.get_keyword_list()):
                self.machine.add_operator(alpha_numeric_str)
            else:
                self.machine.add_operand(alpha_numeric_str)
            self.machine.set_temp(input_char)
            self.machine.set_current_state(self.machine.operand_state)
        else:
            # assume it to be a white space
            alpha_numeric_str=self.machine.get_temp()
            self.machine.add_operand(alpha_numeric_str)
            self.machine.set_temp("")
            self.machine.set_current_state(self.machine.whitespace_state)



class OperandState(State):
    def get_name(self):
        return "Operand State"

    def process_input(self,input_char):
        if (input_char in self.machine.get_operand_character_list()):
            self.machine.set_temp(self.machine.get_temp()+input_char)

        elif(input_char.isalnum()):
            # end of alpha_numeric word
            operator_str=self.machine.get_temp()
            self.machine.add_operator(operator_str)
            self.machine.set_temp(input_char)
            self.machine.set_current_state(self.machine.alphanumeric_state)
        else:
            # assume it to be a white space
            operator_str=self.machine.get_temp()
            self.machine.add_operator(operator_str)
            self.machine.set_temp("")
            self.machine.set_current_state(self.machine.whitespace_state)


class WhiteSpaceState(State):
    def get_name(self):
        return "White Space State"

    def process_input(self,input_char):
        if (input_char in self.machine.get_operand_character_list()):
            self.machine.set_temp(input_char)
            self.machine.set_current_state(self.machine.operand_state)

        elif(input_char.isalnum()):
            self.machine.set_temp(input_char)
            self.machine.set_current_state(self.machine.alphanumeric_state)
        else:
            # assume it to be a white space
            pass
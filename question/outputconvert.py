__author__ = 'Administrator'

START_OUTPUT_BLOCK_TAG="[{("
END_OUTPUT_BLOCK_TAG=")}]"

def output_from_list_to_str(outputs):
    output_str=""
    for i in range(len(outputs)):
        cur_output=outputs[i]
        if (len(cur_output.split("\n"))==1):
            output_str+=cur_output
        else:
            output_str += START_OUTPUT_BLOCK_TAG + "\n" +cur_output + "\n" + END_OUTPUT_BLOCK_TAG
        if (i!=len(outputs)-1):
            output_str +="\n"
    return output_str

def output_from_str_to_list(output):
    output_lines=output.split("\n")
    in_block=False
    output_list=[]
    cur_output="" # for recording output blocks
    for i in range(len(output_lines)):
        cur_line=output_lines[i]
        if (not in_block):
            if (cur_line.find(START_OUTPUT_BLOCK_TAG)==-1):
                output_list.append(cur_line)
            else:
                in_block=True
        else:
            if (cur_line.find(END_OUTPUT_BLOCK_TAG)==-1):
                cur_output += output_lines[i] + "\n"
            else:
                in_block=False
                output_list.append(cur_output[:-1])
                cur_output=""

    return output_list
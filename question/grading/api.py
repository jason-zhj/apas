from question.codestore import get_abs_code_path_from_relativepath

from question.tokenizer.extractstring import StringConstantExtractor
from constants import C_LANGUAGE_NAME
from graders import *
from outputanalyzers import *
from programtesters import *
from compilers import *

__all__=('grade_question_submission','do_compilation',)

grader_class=TestCaseSetGrader

program_tester_classes={JAVA_LANGUAGE_NAME:JavaProgramTester,
                 C_LANGUAGE_NAME:CProgramTester}

compiler_classes={
    JAVA_LANGUAGE_NAME:JavaCompiler,
    C_LANGUAGE_NAME:CCompiler
}

def _get_grader(q_submission):
    question=q_submission.question
    # build output analyzer
    output_ignore_list=StringConstantExtractor(q_submission.get_source_code()).get_string_constant_list() if question.is_ignore_string_constants_in_output() else []
    output_analyzer_class=KeyMatchOutputAnalyzer if question.is_use_partial_output_matching() else EqualityOutputAnalyzer
    output_analyzer=output_analyzer_class(output_ignore_list=output_ignore_list)
    # build programtester
    tester_class=program_tester_classes[question.required_language]
    exe_file_path=get_abs_code_path_from_relativepath(q_submission.exe_file_path)
    if (not os.path.exists(exe_file_path)):
        exe_file_path= do_compilation(code_file_path=get_abs_code_path_from_relativepath(q_submission.src_file_path),language=q_submission.question.required_language)['executable_path']
    program_tester=tester_class(program_path=exe_file_path,output_analyzer=output_analyzer)
    # build grader
    return grader_class(testcase_data=question.get_test_case_data(),program_tester=program_tester)


# return grade and test results for the submission
def grade_question_submission(q_submission):
    # return score, test_case_results, test_case_set_results
    if (not q_submission.compilation_okay):
        q_submission.is_grading_finished=True
        return {'score':0,'test_results':[]}
    grader=_get_grader(q_submission=q_submission)
    grading_result=grader.do_grading()
    test_results=grading_result["test_results"]
    score=grading_result["score"]
    return {'score':score,'test_results':test_results}


def do_compilation(code_file_path,language):
    # a dict {is_successful:boolean,error_message:String,executable_path:String or None}
    compiler_class=compiler_classes[language]
    compiler=compiler_class(code_file_path=code_file_path)
    return compiler.do_compilation()
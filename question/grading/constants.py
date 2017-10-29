from decouple import config
from question.constants import JAVA_LANGUAGE_NAME,C_LANGUAGE_NAME
import os

BASE_DIR=os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

TESTER_CLASS={
    JAVA_LANGUAGE_NAME:'question.grading.programtesters.JavaProgramTester',
    C_LANGUAGE_NAME:'question.grading.programtesters.CProgramTester'
}

EXECUTER_PATH={
    JAVA_LANGUAGE_NAME:config("JAVA_EXECUTER_PATH",os.path.join(BASE_DIR,"compilers/java/bin/java.exe")),
}

COMPILER_PATH={
    JAVA_LANGUAGE_NAME:config("JAVA_COMPILER_PATH",default=os.path.join(BASE_DIR,"compilers/java/bin/javac.exe")),
    # you may change this to the path of your own compiler
    # e.g. 'C':"C:/MingW/bin/gcc.exe"
    C_LANGUAGE_NAME:config("C_COMPILER_PATH",default=os.path.join(BASE_DIR,"compilers/c/bin/gcc.exe"))
}

COMPILER_CLASS={
    JAVA_LANGUAGE_NAME:'question.grading.compilers.JavaCompiler',
    C_LANGUAGE_NAME:'question.grading.compilers.CCompiler'
}

RUN_PROGRAM_TIME_LIMIT=config("RUN_PROGRAM_TIME_LIMIT",cast=int,default=5)
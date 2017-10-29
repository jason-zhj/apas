import os

BASE_DIR=os.path.dirname(
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

CODE_ROOT=os.path.join(BASE_DIR,"uploaded_code")
# path to store the uploaded source code
TEMP_CODE_ROOT=os.path.join(CODE_ROOT,"temp")

DEFAULT_C_FILE_NAME='main.c'
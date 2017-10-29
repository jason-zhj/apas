from decouple import config


MIN_SCORE_TO_CHECK_STRANGE_CODE=config("MIN_SCORE_TO_CHECK_STRANGE_CODE",cast=int,default=50)

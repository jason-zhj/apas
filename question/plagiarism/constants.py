from decouple import config

SIMILARITY_THRESHOLD=config("SIMILARITY_THRESHOLD",default=5,cast=int) # used for Halstead Plagiarism Checking

import datetime

# date de reference UTC retenue pour SmartFramework
REF_EPOCK = datetime.date(1900, 1, 1)

# dates de reference UTC pour differentes bibliotheques
PYTHON_EPOCH = datetime.date(1970, 1, 1)  # datetime.date(*time.gmtime(0)[0:3])
WINDOWS_EPOCH = datetime.date(1601, 1, 1)
NTP_EPOCH = datetime.date(1900, 1, 1)

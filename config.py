# ------------- Active Directory Configuration ----------------



AD_SERVER = 'ldap://xxxxxxx'


AD_DOMAIN = 'xxxxxx'


AD_ADMIN = 'xxxx@xxxx.xxm\\vxxx'


AD_PASSWORD = 'xxxx@xxxx.xxm'


AD_BASE_DN = 'DC=cccxxt,DC=local'



# ---------------- Azure AD App Credentials ----------------------



AZURE_CLIENT_ID = 'xxxx@xxxx.xxm'


AZURE_CLIENT_SECRET = 'gxxxx@xxxx.xxm'


AZURE_TENANT_ID = 'exxxx@xxxx.xxm'


AZURE_DOMAIN = 'xxxx@xxxx.xxm'



# ---------------- Updated Group Object IDs (Microsoft 365-compatible groups) ----------------



OTTAWA_GROUP_ID = 'xxxx@xxxx.xxm'


DALLAS_GROUP_ID = 'bxxxx@xxxx.xxm'


ALL_EMPLOYEES_GROUP_ID = 'xxxx@xxxx.xxm'



GROUP_CHOICES = {


    "Ottawa": OTTAWA_GROUP_ID,


    "Dallas": DALLAS_GROUP_ID,


    "All Employees": ALL_EMPLOYEES_GROUP_ID


}


SMTP_SERVER = "smtp.office365.com"

SMTP_PORT = 587

SMTP_USE_TLS = True

SMTP_USERNAME = "xxxx@xxxx.xxm"

SMTP_PASSWORD = "xxxx@xxxx.xxm"

SMTP_SENDER = "xxxx@xxxx.xxm"

SMTP_RECIPIENTS = ["xxxx@xxxx.xxm", "xxxx@xxxx.xxm"]
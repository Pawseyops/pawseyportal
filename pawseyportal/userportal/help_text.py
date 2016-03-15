# Help text for all models in one file for easy updating.

# Email Template Model
emailtemplate_name = """The name of your email template"""
emailtemplate_subject = """The subject header for emails sent using this template"""
emailtemplate_template = """Your email template body in Django templating syntax"""

# Service Type Model
servicetype_name = """The name of your service type"""
servicetype_help_email = """The email address users should send help requests to"""

# Service Model
service_name = """The name of your service"""
service_type = """The type of service this is (defined in the Service Type Model"""

# Institution Model
institution_name = """The name of the institution"""
institution_partner = """Tick if the institution is a partner organisation"""

# Person Account Model
personaccount_uid = """The user id of the account"""
personaccount_uidnumber = """The uid number of the account"""
personaccount_gidnumber = """The gid number of the account"""
personaccount_passwordhash = """The hashed initial password of the account (not the current password in most cases, should have been changed)"""

# Person Status Model
personstatus_name = """The name of the status that can be assigned to a person"""
personstatus_description = """Description of this status and what it is used for"""

# Person Model
person_firstname = """The first name of the person"""
person_surname = """The surname of the person"""
person_institution = """The institution that the person belongs to"""
person_institution_email = """The instituion based email address of the person"""
person_alternate_email = """The alternate email address of the person"""
person_phone = """The phone number of the person"""
person_mobilephone = """The mobile phone number of the person"""
person_student = """Tick if the person is a student"""
person_personaccount = """The account information for the person"""
person_accountemailhash = """The uuid used to identify the account in the email sent out for requesting details"""
person_status = """The status of the person"""
person_accountemailon = """The date that the email was sent out to request details for account creation"""
person_accountcreatedon = """The date that the account was created"""
person_accountcreatedemailon = """The date the person was emailed to tell them their account was ready"""

# Project Model
project_code = """Project code of the project for use on systems"""
project_title = """Title of the project"""
project_pi = """Principal Investigator of the project"""
project_summary = """Summary of the project as provided in the proposal"""
project_people = """The people taking part in the project"""

# Priority Area Model
priorityarea_name = """The name of the priority area"""
priorityarea_code = """The code of the priority area, used by systems"""

# Allocation Round Model
allocationround_system = """The service that the allocation round provides"""
allocationround_start_date = """The start date of the allocation round"""
allocationround_end_date = """The end date of the allocation round"""
allocationround_name = """The name given to the allocation round"""
allocationround_priority_area = """The priority areas served by this allocation round"""

# Allocation Model
allocation_name = """Name of the allocation"""
allocation_project = """The project that this allocation is for"""
allocation_start = """The start date of this allocation"""
allocation_end = """The end date of this allocation"""
allocation_permanent = """Tick if this allocation is perpetual"""
allocation_priorityarea = """Priority area that this allocation comes under"""
allocation_serviceunits = """Number of service units that were awarded to this allocation (to be interpreted by the systems)"""
allocation_service = """Service which this allocation is for"""
allocation_suspend = """Tick to suspend allocation"""
allocation_allocation_round = """Allocation round that this allocation comes under"""

# Partition Model
partition_name = """Name of the partition (exactly as on system)"""

# Allocation Partition Model
allocationpartition_partition = """Partition that this applies to"""
allocationpartition_allocation = """Allocation that this applies to"""

# Filesystem Model
filesystem_name = """Name of the filesystem (exactly as on system)"""
filesystem_quotad = """Tick if this filesystem has a quota on it"""

# Allocation Filesystem Model
allocationfilesystem_filesystem = """Filesystem that this applies to"""
allocationfilesystem_allocation = """Allocation this applies to"""
allocationfilesystem_quota = "Quota of this allocation on this filesystem"""

# Comment Model
comment_comment = """Internal Comment about the Project or Allocation"""

# Yaml File Defaults
yamldefaults_defaults = """YAML File defaults in correct YAML format for activate account. The last one will be used."""

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
import datetime

# 3rd party apps
from smart_selects.db_fields import ChainedForeignKey

#=================
# Util Functions
#=================
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
    
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except(TypeError, ValueError):
        pass
    
    return False

#=================
# Look-up tables
#=================
BOOL_CHOICES = ((1,'Yes'),(0,'No'))
GOAL_CHOICES = ((1,'Yes'),(0,'No'),(-1,'Not Reported'),(-99,'TBD'))
#DEADLINE_CHOICES = (
#    (0,'Ongoing'),
#    (1,'Q1'),
#    (2,'Q2'),
#    (3,'Q3'),
#    (4,'Q4'),
#    (-1,'No Deadline')
#)

#=================
# Util Functions
#=================
TIMEWINDOW_DAYS = 15
CURRENT_YEAR = (datetime.date.today()-datetime.timedelta(days=TIMEWINDOW_DAYS)).year
QUARTER_START_END = (
    (datetime.date(CURRENT_YEAR,1,1)+datetime.timedelta(days=TIMEWINDOW_DAYS),
    datetime.date(CURRENT_YEAR,3,31)+datetime.timedelta(days=TIMEWINDOW_DAYS)),
    (datetime.date(CURRENT_YEAR,4,1)+datetime.timedelta(days=TIMEWINDOW_DAYS),
    datetime.date(CURRENT_YEAR,6,30)+datetime.timedelta(days=TIMEWINDOW_DAYS)),
    (datetime.date(CURRENT_YEAR,7,1)+datetime.timedelta(days=TIMEWINDOW_DAYS),
    datetime.date(CURRENT_YEAR,9,30)+datetime.timedelta(days=TIMEWINDOW_DAYS)),
    (datetime.date(CURRENT_YEAR,10,1)+datetime.timedelta(days=TIMEWINDOW_DAYS),
    datetime.date(CURRENT_YEAR,12,31)+datetime.timedelta(days=TIMEWINDOW_DAYS)))

def report_quarter():
    report_quarter = 0
    for quarter,start_end_dates in enumerate(QUARTER_START_END):
        if start_end_dates[0] <= datetime.date.today() <= start_end_dates[1]:
            report_quarter = quarter + 1
    return report_quarter

#=================
# Core Models
#=================
class Indicator(models.Model):
#    id = models.IntegerField(primary_key=True)
    description = models.TextField(max_length=500,null=True,blank=True)
    workplan_area = models.ManyToManyField('WorkplanArea',null=True,blank=True)
    
    def __unicode__(self):
        return str(self.id)
            
#    def _get_workplan_areas(self):
#        try:
#            workplan_areas = WorkplanArea.objects.filter(indicator=self)
#            return ",".join([wa.str_id for wa in workplan_ares])
#        except:
#            return ""
#    _get_workplan_areas.short_description = "Workplan Areas"
    
    def previous(self):
        try:
            previous_records = Indicator.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return Indicator.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = Indicator.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return Indicator.objects.get(id=next_id)
        except:
            return None

    class Meta:
        db_table = u'indicator'
        ordering = ['id']
        
class Descriptor(models.Model):
#    id = models.IntegerField(primary_key=True)
    indicator = models.ForeignKey('Indicator')
    description = models.TextField(max_length=500,null=True,blank=True)
    value = models.CharField(max_length=100,null=True,blank=True)
    algorithm = models.TextField(max_length=500,null=True,blank=True)
    
    def previous(self):
        try:
            previous_records = Descriptor.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return Descriptor.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = Descriptor.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return Descriptor.objects.get(id=next_id)
        except:
            return None
    
    class Meta:
        db_table = u'descriptor'

class Organization(models.Model):
#    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100,verbose_name='Organization')
    abbreviation = models.CharField(max_length=100,null=True,blank=True)
    mission = models.TextField(null=True,blank=True)

    def __unicode__(self):
        return self.abbreviation
    
    def _get_activity_quarters(self):
        org_acts = OrganizationActivity.objects.filter(organization=self)
        active_quarters = []
        for org_act in org_acts:
            outputs = Output.objects.filter(orgnization_activity=org_act)
            for output in outputs:
                if output.active_quarter:
                    if not ("Q%d" % output.active_quarter.quarter) in active_quarters:
                        active_quarters.append("Q%d" % output.active_quarter.quarter)
        if not active_quarters:
            active_quarters = "No active quarters reporting on"
        else:
            active_quarters = ",".join(active_quarters)
        return active_quarters
    _get_activity_quarters.short_description = "Active Quarters"
    
    def _get_quarter_performance_comment(self):
        org_qt_summary = {
            "all":{"Q1":0,"Q2":0,"Q3":0,"Q4":0},
            "goal":{"Q1":0,"Q2":0,"Q3":0,"Q4":0}
        }
        org_outputs = Output.objects.filter(orgnization_activity__organization=self)
        for org_output in org_outputs:
            if org_output.active_quarter is not None:
                org_qt_summary["all"]["Q%d" % org_output.active_quarter.quarter] += 1
                if org_output.is_goal==1:
                    org_qt_summary["goal"]["Q%d" % org_output.active_quarter.quarter] += 1
        org_pf_summary = "Q1:%d/%d; Q2:%d/%d; Q3:%d/%d; Q4:%d/%d" % (org_qt_summary["goal"]["Q1"],org_qt_summary["all"]["Q1"],
        org_qt_summary["goal"]["Q2"],org_qt_summary["all"]["Q2"],
        org_qt_summary["goal"]["Q3"],org_qt_summary["all"]["Q3"],
        org_qt_summary["goal"]["Q4"],org_qt_summary["all"]["Q4"],)
        return org_pf_summary
    _get_quarter_performance_comment.short_description = "Quarter Performance (goals achieved)"    

    def previous(self):
        try:
            previous_records = Organization.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return Organization.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = Organization.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return Organization.objects.get(id=next_id)
        except:
            return None

    class Meta:
        db_table = u'organization'
        ordering = ['name']

class MyUser(models.Model):
#    id =  models.IntegerField(primary_key=True)
    user = models.ForeignKey(User)
    organization = models.ForeignKey(Organization)
    
    def __unicode__(self):
        return "%s %s" % (self.user.first_name,self.user.last_name)
    
    def _get_user_first_name(self):
        if self.user.first_name:
            return self.user.first_name
        else:
            return ""
    _get_user_first_name.short_description = "First Name"
        
    def _get_user_last_name(self):
        if self.user.last_name:
            return self.user.last_name
        else:
            return ""
    _get_user_last_name.short_description = "Last Name"
    
    def _get_user_email(self):
        if self.user.email:
            return self.user.email
        else:
            return ""
    _get_user_email.short_description = "Email Address"
    
    class Meta:
        db_table = u'app_user'

class ActiveQuarter(models.Model):
#    id = models.IntegerField(primary_key=True)
    quarter = models.IntegerField()

    def __unicode__(self):
        return unicode(self.quarter)

    class Meta:
        db_table = u'active_quarter'

# Model Workplan Domain
class WorkplanDirection(models.Model):
#    id = models.IntegerField(primary_key=True)
    str_id = models.CharField(max_length=1,verbose_name='Workplan Direction ID')
    description = models.TextField(max_length=500)
    
    def __unicode__(self):
        return self.str_id
    
    def previous(self):
        try:
            previous_records = WorkplanDirection.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return WorkplanDirection.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = WorkplanDirection.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return WorkplanDirection.objects.get(id=next_id)
        except:
            return None
    
    class Meta:
        verbose_name = 'Workplan Direction'
        db_table = u'workplan_direction'
        ordering = ['str_id']

# Model Workplan Area
class WorkplanArea(models.Model):
#    id = models.IntegerField(primary_key=True)
    str_id = models.CharField(max_length=2,verbose_name='Workplan Area ID')
    description = models.TextField(max_length=500)
    workplan_direction = models.ForeignKey('WorkplanDirection',null=True)
    year = models.IntegerField(default=datetime.datetime.now().year)
  
    def __unicode__(self):
        return "%s: %s" % (self.str_id,self.description)
    
    def previous(self):
        try:
            previous_records = WorkplanArea.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return WorkplanArea.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = WorkplanArea.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return WorkplanArea.objects.get(id=next_id)
        except:
            return None

    class Meta:
        verbose_name = 'Workplan Area'
        db_table = u'workplan_area'
        ordering = ['str_id']
        
# Model MHC Activity
class MHCActivity(models.Model):
#    id = models.IntegerField(primary_key=True)
    str_id = models.CharField(max_length=10,null=True,verbose_name='MHC Activity ID')
    workplan_area = models.ForeignKey('WorkplanArea',verbose_name='Workplan Area')
    description = models.TextField(max_length=500)
    year = models.IntegerField(default=datetime.datetime.now().year)
  
    def __unicode__(self):
        return "%s: %s" % (self.str_id,self.description)
    
    def save(self, *args, **kwargs):
        if not self.str_id:
            mhcacts = MHCActivity.objects.filter(workplan_area=self.workplan_area)
            mhcact_ids = []
            for mhcact in mhcacts:
                mhcact_ids.append(mhcact.id)
            mhcact_ids.sort()
            if self.id in mhcact_ids:
                mhcactivity_id = mhcact_ids.index(self.id) + 1
            else:
                mhcactivity_id = len(mhcact_ids) + 1
            self.str_id = "%s.%d" % (self.workplan_area.str_id, mhcactivity_id)
        super(MHCActivity, self).save(*args, **kwargs)
            
    def previous(self):
       try:
           previous_records = MHCActivity.objects.filter(id__lt=self.id)
           previous_id = previous_records.order_by('-id')[0].id
           return MHCActivity.objects.get(id=previous_id)
       except:
           return None
       
    def next(self):
       try:
           next_records = MHCActivity.objects.filter(id__gt=self.id)
           next_id = next_records.order_by('id')[0].id
           return MHCActivity.objects.get(id=next_id)
       except:
           return None   

    class Meta:
        verbose_name = 'MHC Activity'
        db_table = u'mhc_activity'
        ordering = ['str_id']
        
# Model Organization Activity
class OrganizationActivity(models.Model):
#    id = models.IntegerField(primary_key=True)
    str_id = models.CharField(max_length=20,null=True,verbose_name='Organization Activity ID')
    workplan_area = models.ForeignKey('WorkplanArea',verbose_name='Workplan Area')
#    mhc_activity = models.ForeignKey('MHCActivity',verbose_name='MHC Activity')
    mhc_activity = ChainedForeignKey(
        MHCActivity,
        verbose_name = 'MHC Activity',
        chained_field = 'workplan_area',
        chained_model_field = 'workplan_area',
        show_all = False,
        auto_choose = True
    )    
    organization = models.ForeignKey('Organization',verbose_name='Organization')
    description = models.TextField(max_length=500)
    q1_comment = models.CharField(max_length=5000,null=True,blank=True)
    q2_comment = models.CharField(max_length=5000,null=True,blank=True)
    q3_comment = models.CharField(max_length=5000,null=True,blank=True)
    q4_comment = models.CharField(max_length=5000,null=True,blank=True)
    other_comment = models.CharField(max_length=500,null=True,blank=True,verbose_name='Other Comment')
    origin_strid = models.CharField(max_length=50,null=True,blank=True)
    year = models.IntegerField(default=-1)
    
    def __unicode__(self):
        return "%s: %s" % (self.str_id,self.description)
    
    def save(self, *args, **kwargs):
        if not self.str_id:
            orgacts = OrganizationActivity.objects.filter(mhc_activity=self.mhc_activity)
            orgact_ids = []
            for orgact in orgacts:
                orgact_ids.append(orgact.id)
            orgact_ids.sort()
            if self.id in orgact_ids:
                organization_activity_id = orgact_ids.index(self.id) + 1
            else:
                organization_activity_id = len(orgact_ids) + 1
            self.str_id = "%s.%d" % (self.mhc_activity.str_id, organization_activity_id)
        super(OrganizationActivity, self).save(*args, **kwargs)    
    
    def _get_all_comments(self):
        return "Q1: %s\n\r Q2: %s\n\r Q3: %s\n\r Q4: %s\n\r Other Comment: %s" % (self.q1_comment,self.q2_comment,self.q3_comment,self.q4_comment,self.other_comment)
    _get_all_comments.short_description = "Organization Activity Comment Summary"
    
    def previous(self):
        try:
            previous_records = OrganizationActivity.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return OrganizationActivity.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = OrganizationActivity.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return OrganizationActivity.objects.get(id=next_id)
        except:
            return None
    
    class Meta:
        verbose_name = 'Organization Activity'
        db_table = u'organization_activity'
        ordering = ['str_id']
    
## Model Output Activity
#class OutputActivity(models.Model):
##    id = models.IntegerField(primary_key=True)
#    str_id = models.CharField(max_length=30,null=True,verbose_name='Output Activity ID')
#    orgnization_activity = models.ForeignKey('OrganizationActivity',verbose_name='Organization Activity')
#    description = models.CharField(max_length=500)
#    deadline = models.IntegerField(choices=DEADLINE_CHOICES,default=-1,verbose_name='Deadline')
#    
#    def __unicode__(self):
#            return self.str_id
#        
#    def save(self, *args, **kwargs):
#        opacts = OutputActivity.objects.filter(orgnization_activity=self.orgnization_activity)
#        opact_ids = []
#        for opact in opacts:
#            opact_ids.append(opact.id)
#        opact_ids.sort()
#        if self.id in opact_ids:
#            output_activity_id = opact_ids.index(self.id) + 1
#        else:
#            output_activity_id = len(opact_ids) + 1
#        self.str_id = "%s.%d" % (self.orgnization_activity.str_id, output_activity_id)
#        super(OutputActivity, self).save(*args, **kwargs)    
#    
#    class Meta:
#        verbose_name = 'Output Activity'
#        db_table = u'output_activity'
#        ordering = ['str_id']    

# Model Output
class Output(models.Model):
#    id = models.IntegerField(primary_key=True)
    orgnization_activity = models.ForeignKey('OrganizationActivity',verbose_name='Organization Activity')
#    output_activity = models.ForeignKey('OutputActivity',verbose_name='Output Activity')
    active_quarter = models.ForeignKey('ActiveQuarter',verbose_name='Reporting Quarter',default=report_quarter(),null=True)
    description = models.CharField(max_length=500)
    location = models.CharField(max_length=500,null=True,blank=True)
#    is_shortterm_outcomes = models.IntegerField(choices=BOOL_CHOICES,default=0,verbose_name='Shor Term Outcome?')
    is_goal = models.IntegerField(choices=GOAL_CHOICES,default=-1,verbose_name='Goals Reached?')
    output_value = models.CharField(max_length=500,null=True,blank=True,verbose_name='Output Value')
    comment = models.TextField(max_length=500,null=True,blank=True)

    def save(self, *args, **kwargs):       
        # determin if the goal is reached by the output value
        if (not self.output_value) or (self.output_value == "None"):
            if self.comment and self.comment != "None":
                self.is_goal = -99
            else:
                self.is_goal = -1
        else:
            if (self.output_value.strip().lower() == "yes") or (self.output_value.strip().lower() == "y"):
                self.is_goal = 1         
            else:
                if is_number(self.output_value):
                    numbers_in_description = [n for n in self.description.split() if is_number(n)]
                    if len(numbers_in_description) > 0:
                        if "." in numbers_in_description[0]:
                            goal_number = float(numbers_in_description[0])
                        else:
                            goal_number = int(numbers_in_description[0])
                        if "." in self.output_value:
                            output_value = float(self.output_value)
                        else:
                            output_value = int(self.output_value)
                        if output_value >= goal_number:
                            self.is_goal = 1
                        else:
                            self.is_goal = 0
#                    else:
#                        self.is_goal = -99
#                else:
#                    self.is_goal = -99
        
            
        # update organization activity by summarizing output comments
        comment = self.comment
        if comment:
            comment = comment.strip()
            org_activity = self.orgnization_activity
            outputs = Output.objects.filter(orgnization_activity=org_activity).filter(active_quarter=self.active_quarter)
            org_activity_comment = ". ".join(op.comment for op in outputs if op.comment)
            if org_activity_comment:
                org_activity_comment = org_activity_comment + ". " + comment
            else:
                org_activity_comment = comment
            exec("org_activity.q%d_comment = org_activity_comment" % self.active_quarter.quarter)
            org_activity.save()            
        self.comment = comment
        super(Output, self).save(*args, **kwargs)
    
    def previous(self):
        try:
            previous_records = Output.objects.filter(id__lt=self.id)
            previous_id = previous_records.order_by('-id')[0].id
            return Output.objects.get(id=previous_id)
        except:
            return None
        
    def next(self):
        try:
            next_records = Output.objects.filter(id__gt=self.id)
            next_id = next_records.order_by('id')[0].id
            return Output.objects.get(id=next_id)
        except:
            return None

    class Meta:
        verbose_name = 'Output'
        db_table = u'output'
        
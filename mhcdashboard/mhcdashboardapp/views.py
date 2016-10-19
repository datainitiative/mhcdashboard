from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.template import RequestContext
from django.db import models
from django.db.models.loading import get_model
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import csv
import base64
from zipfile import *
import collections # for OrderedDict

# Import from general utilities
from util import *
from mhcdashboard.settings import SOTRAGE_ROOTPATH

# Import from app
from mhcdashboard.settings import ROOT_APP_URL, SOTRAGE_ROOTPATH, STATIC_URL
from mhcdashboardapp.models import *
from mhcdashboardapp.forms import *

# ------------------------------------
# ReportLab Imports
# - ReportLab open source PDF toolkit
#   A Python-based PDF library
# ------------------------------------
from reportlab.pdfgen import canvas
# page size unit: point = 1/72 inch
# size for letter: 612 * 792
# size for A4: 595.28~ * 841.89~
from reportlab.lib.pagesizes import letter, A4
from reportlab.rl_config import defaultPageSize
# import unit inch: 1 inch = 72 points
from reportlab.lib.units import inch

# Platypus imports
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

# Graphic imports
# Image File Reader
from reportlab.lib.utils import ImageReader
#import drawing
from reportlab.graphics.shapes import Drawing
#import renderpdf
from reportlab.graphics import renderPDF
#import color
from reportlab.lib.colors import Color,HexColor
#import Pie chart
from reportlab.graphics.charts.piecharts import Pie


'''-----------------------
Home Page
-----------------------'''
# Home page
@login_required
@render_to("mhcdashboardapp/home.html")
def home(request):
    workplanareas = WorkplanArea.objects.filter(year=datetime.datetime.now().year)
    mhcactivities = MHCActivity.objects.filter(year=datetime.datetime.now().year)
    orgactivities = OrganizationActivity.objects.filter(year=datetime.datetime.now().year)
    organizations = []
    orgs = Organization.objects.all()
    for org in orgs:
        if org._get_activity_quarters() != "No active quarters reporting on":
            organizations.append(org)
    indicators = Indicator.objects.all()
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_goal_no = Output.objects.filter(is_goal=0,orgnization_activity__year=datetime.datetime.now().year)
    org_qt_summary_all = []
    org_qt_summary_goal = []
    org_pf_summary = []
    org_pf_summary_q1 = []
    org_pf_summary_q2 = []
    org_pf_summary_q3 = []
    org_pf_summary_q4 = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for org in organizations:
        tmp_org = Organization.objects.get(id=org.id)
        tmp_org_qt_summary_all = collections.OrderedDict([("Org",org.abbreviation),("quarter",collections.OrderedDict([("Q1",0),("Q2",0),("Q3",0),("Q4",0)]))])
        tmp_org_qt_summary_goal = collections.OrderedDict([("Org",org.abbreviation),("quarter",collections.OrderedDict([("Q1",0),("Q2",0),("Q3",0),("Q4",0)]))])
        tmp_org_pf_summary = collections.OrderedDict([("Org",org.abbreviation),("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))])
        tmp_org_pf_summary_q1 = collections.OrderedDict([("Org",org.abbreviation),("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))])
        tmp_org_pf_summary_q2 = collections.OrderedDict([("Org",org.abbreviation),("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))])
        tmp_org_pf_summary_q3 = collections.OrderedDict([("Org",org.abbreviation),("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))])
        tmp_org_pf_summary_q4 = collections.OrderedDict([("Org",org.abbreviation),("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))])
        org_outputs = Output.objects.filter(orgnization_activity__organization=tmp_org,orgnization_activity__year=datetime.datetime.now().year)
        for org_output in org_outputs:
            if org_output.active_quarter is not None:
                tmp_org_qt_summary_all["quarter"]["Q%d" % org_output.active_quarter.quarter] += 1
                if org_output.is_goal==1:
                    tmp_org_qt_summary_goal["quarter"]["Q%d" % org_output.active_quarter.quarter] += 1
            if org_output.is_goal is not None:
                tmp_org_pf_summary["perform"][goal_choices[org_output.is_goal]] += 1
                if org_output.active_quarter:
                    if org_output.active_quarter.quarter == 1:
                        tmp_org_pf_summary_q1["perform"][goal_choices[org_output.is_goal]] += 1
                    elif org_output.active_quarter.quarter == 2:
                        tmp_org_pf_summary_q2["perform"][goal_choices[org_output.is_goal]] += 1
                    elif org_output.active_quarter.quarter == 3:
                        tmp_org_pf_summary_q3["perform"][goal_choices[org_output.is_goal]] += 1
                    elif org_output.active_quarter.quarter == 4:
                        tmp_org_pf_summary_q4["perform"][goal_choices[org_output.is_goal]] += 1                
        org_qt_summary_all.append(tmp_org_qt_summary_all)
        org_qt_summary_goal.append(tmp_org_qt_summary_goal)
        org_pf_summary.append(tmp_org_pf_summary)
        org_pf_summary_q1.append(tmp_org_pf_summary_q1)
        org_pf_summary_q2.append(tmp_org_pf_summary_q2)
        org_pf_summary_q3.append(tmp_org_pf_summary_q3)
        org_pf_summary_q4.append(tmp_org_pf_summary_q4)
    org_qt_summary_all_json = json.dumps(org_qt_summary_all)
    org_qt_summary_goal_json = json.dumps(org_qt_summary_goal)
    org_pf_summary_json = json.dumps(org_pf_summary)
    org_pf_summary_q1_json = json.dumps(org_pf_summary_q1)
    org_pf_summary_q2_json = json.dumps(org_pf_summary_q2)
    org_pf_summary_q3_json = json.dumps(org_pf_summary_q3)
    org_pf_summary_q4_json = json.dumps(org_pf_summary_q4)
    workplanarea_goals = {}
    workplanarea_num_orgact = {}
    for wpa in workplanareas:
        workplanarea_goals[wpa.str_id] = 0
        workplanarea_num_orgact[wpa.str_id] = len(OrganizationActivity.objects.filter(workplan_area=wpa.id,year=datetime.datetime.now().year))
    orgact_summary = []
    for orgact in orgactivities:
        outputs_num = len(Output.objects.filter(orgnization_activity=orgact.id))
        outputs_num_goal_yes = len(Output.objects.filter(orgnization_activity=orgact.id,is_goal=1))
        outputs_num_goal_no = len(Output.objects.filter(orgnization_activity=orgact.id,is_goal=0))
        outputs_num_goal_nr = len(Output.objects.filter(orgnization_activity=orgact.id,is_goal=-1))
        orgact_summary.append({
            "str_id": orgact.str_id,
            "workplan_area": orgact.workplan_area.str_id,
            "goals": (outputs_num,outputs_num_goal_yes,outputs_num_goal_no,outputs_num_goal_nr)
        })
        if (outputs_num_goal_yes == outputs_num) and (outputs_num_goal_yes > 0):
            workplanarea_goals[orgact.workplan_area.str_id] += 1
    piechart_data = []
    for key,value in workplanarea_goals.iteritems():
        if value > 0:
            piechart_data.append({
                "label": key,
                "data": float(value)/workplanarea_num_orgact[key] if workplanarea_num_orgact[key] != 0 else 0
            })
    piechart_data_json = json.dumps(piechart_data)
    return {"num_workplanarea":len(workplanareas),
            "num_mhcactivity":len(mhcactivities),
            "num_orgactivity":len(orgactivities),
            "num_organization":len(organizations),
            "num_indicator":len(indicators),
            "num_output":len(outputs),
            "piechart_data":piechart_data_json,
            "barpiechart_data_1_all":org_qt_summary_all_json,
            "barpiechart_data_1_goal":org_qt_summary_goal_json,
            "barpiechart_data_2":org_pf_summary_json,
            "barpiechart_data_2_q1":org_pf_summary_q1_json,
            "barpiechart_data_2_q2":org_pf_summary_q2_json,
            "barpiechart_data_2_q3":org_pf_summary_q3_json,
            "barpiechart_data_2_q4":org_pf_summary_q4_json,
            "outputs_goal_no":outputs_goal_no,
    }


'''-----------------------
Indicators Page
-----------------------'''
# Indicators page
@login_required
@render_to("mhcdashboardapp/indicator_index.html")
def indicator_index(request):
    return {
    }
    
'''-----------------------
Report Ouput Page
-----------------------'''
@login_required
@render_to("mhcdashboardapp/report_output.html")
def report_output(request):
    error_msg = ""
    save_msg = ""
    login_user = MyUser.objects.get(user=request.user)
    org_id = login_user.organization.id
    report_q = report_quarter()
    select_options = None
    organization = Organization.objects.get(id=org_id)
    workplan_areas = []
    mhc_activities = []
    mhc_activitie_ids = []
    org_activities = []
    org_activitie_ids = []
    outputs_current = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')

    for op in outputs_current:
        if not (op.orgnization_activity.workplan_area in workplan_areas):
            workplan_areas.append(op.orgnization_activity.workplan_area)
        if not (op.orgnization_activity.mhc_activity in mhc_activities):
            mhc_activities.append(op.orgnization_activity.mhc_activity)
            mhc_activitie_ids.append(op.orgnization_activity.mhc_activity.id)
        if not (op.orgnization_activity in org_activities):
            org_activities.append(op.orgnization_activity)
            org_activitie_ids.append(op.orgnization_activity.id)       
    if report_q > 1:
        outputs_previous = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter__lt=report_q).filter(orgnization_activity__organization__id=org_id)
    else:
        outputs_previous = None
    
    outputs_report = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')
    if request.method == 'POST':
        # pre-select Workplan Area, MHC Activity, Org Activity as filters
        if request.POST["OrgActID"]:
            select_org_act_id = int(request.POST["OrgActID"])
            select_org = OrganizationActivity.objects.get(id=select_org_act_id)
            select_mhc_act_id = select_org.mhc_activity.id
            select_wp_area_id = select_org.workplan_area.id
            select_options = {
                "select_org_act_id":select_org_act_id,
                "select_mhc_act_id":select_mhc_act_id,
                "select_wp_area_id":select_wp_area_id
            }
            outputs_report = Output.objects.filter(active_quarter__quarter=report_q).filter(orgnization_activity=select_org)
        # update reported outputs
        for op in outputs_report:
            op_id = op.id
            
            op_location = request.POST.get("id_output_set-%d-location" % op_id)
            if op_location:
                op.location = op_location
            
            op_comment = request.POST.get("id_output_set-%d-comment" % op_id)
            if op_comment:
                op.comment = op_comment
            else:
                op.comment = None
            
            op_output_value = request.POST.get("id_output_set-%d-output_value" % op_id)

            op.output_value = op_output_value
            if (not op_output_value) or (op_output_value == "None"):
                if op_comment and op_comment != "None":
                    op.is_goal = -99
                else:
                    op.is_goal = -1
            else:
                if (op_output_value.strip().lower() == "yes") or (op_output_value.strip().lower() == "y"):
                    op.is_goal = 1
                else:
                    if is_number(op_output_value):
                        numbers_in_description = [n for n in op.description.split() if is_number(n)]
                        if len(numbers_in_description) > 0:
                            if "." in numbers_in_description[0]:
                                goal_number = float(numbers_in_description[0])
                            else:
                                goal_number = int(numbers_in_description[0])
                            if "." in op_output_value:
                                output_value = float(op_output_value)
                            else:
                                output_value = int(op_output_value)
                            if output_value >= goal_number:
                                op.is_goal = 1
                            else:
                                op.is_goal = 0
                        else:
                            op.is_goal = -99
                    else:
                        op.is_goal = -99
            try:
                op.save()
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                error_type = exc_type.__name__
                error_info = exc_obj
                error_msg = "%s: %s. Please try again!" % (error_type,error_info)
        if error_msg == "":
            outputs_current = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')
            save_msg = "Changes to Output have been saved!"
    
    return {
        "report_quarter":report_q,
        "report_year":datetime.datetime.now().year,
        "organization":organization,
        "select_options":select_options,
        "workplan_areas":workplan_areas,
        "mhc_activities":mhc_activities,
        "mhc_activitie_ids":mhc_activitie_ids,
        "org_activities":org_activities,
        "org_activitie_ids":org_activitie_ids,
        "outputs_current":outputs_current,
        "outputs_previous":outputs_previous,
        "current_year":datetime.datetime.now().year,
        "error_msg":error_msg,
        "save_msg":save_msg
    }

@login_required
@render_to("mhcdashboardapp/report_output_temp.html")
def report_output_temp(request,qid):
    tmp_username_list = ["Admin","admin","NMahajan","DGagne"]
    error_msg = ""
    save_msg = ""
    login_user = MyUser.objects.get(user=request.user)
    org_id = login_user.organization.id
    report_q = qid
    select_options = None
    organization = Organization.objects.get(id=org_id)
    workplan_areas = []
    mhc_activities = []
    mhc_activitie_ids = []
    org_activities = []
    org_activitie_ids = []
    outputs_current = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')

    for op in outputs_current:
        if not (op.orgnization_activity.workplan_area in workplan_areas):
            workplan_areas.append(op.orgnization_activity.workplan_area)
        if not (op.orgnization_activity.mhc_activity in mhc_activities):
            mhc_activities.append(op.orgnization_activity.mhc_activity)
            mhc_activitie_ids.append(op.orgnization_activity.mhc_activity.id)
        if not (op.orgnization_activity in org_activities):
            org_activities.append(op.orgnization_activity)
            org_activitie_ids.append(op.orgnization_activity.id)       
    if report_q > 1:
        outputs_previous = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter__lt=report_q).filter(orgnization_activity__organization__id=org_id)
    else:
        outputs_previous = None

    outputs_report = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')
    if request.method == 'POST':
        # pre-select Workplan Area, MHC Activity, Org Activity as filters
        if request.POST["OrgActID"]:
            select_org_act_id = int(request.POST["OrgActID"])
            select_org = OrganizationActivity.objects.get(id=select_org_act_id)
            select_mhc_act_id = select_org.mhc_activity.id
            select_wp_area_id = select_org.workplan_area.id
            select_options = {
                "select_org_act_id":select_org_act_id,
                "select_mhc_act_id":select_mhc_act_id,
                "select_wp_area_id":select_wp_area_id
            }
            outputs_report = Output.objects.filter(active_quarter__quarter=report_q).filter(orgnization_activity=select_org)
        # update reported outputs
        for op in outputs_report:
            op_id = op.id
            
            op_location = request.POST.get("id_output_set-%d-location" % op_id)
            if op_location:
                op.location = op_location
            
            op_comment = request.POST.get("id_output_set-%d-comment" % op_id)
            if op_comment:
                op.comment = op_comment
            else:
                op.comment = None
            
            op_output_value = request.POST.get("id_output_set-%d-output_value" % op_id)

            op.output_value = op_output_value
            if (not op_output_value) or (op_output_value == "None"):
                if op_comment and op_comment != "None":
                    op.is_goal = -99
                else:
                    op.is_goal = -1
            else:
                if (op_output_value.strip().lower() == "yes") or (op_output_value.strip().lower() == "y"):
                    op.is_goal = 1
                else:
                    if is_number(op_output_value):
                        numbers_in_description = [n for n in op.description.split() if is_number(n)]
                        if len(numbers_in_description) > 0:
                            if "." in numbers_in_description[0]:
                                goal_number = float(numbers_in_description[0])
                            else:
                                goal_number = int(numbers_in_description[0])
                            if "." in op_output_value:
                                output_value = float(op_output_value)
                            else:
                                output_value = int(op_output_value)
                            if output_value >= goal_number:
                                op.is_goal = 1
                            else:
                                op.is_goal = 0
                        else:
                            op.is_goal = -99
                    else:
                        op.is_goal = -99
            try:
                op.save()
            except Exception, e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                error_type = exc_type.__name__
                error_info = exc_obj
                error_msg = "%s: %s. Please try again!" % (error_type,error_info)
        if error_msg == "":
            outputs_current = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(active_quarter__quarter=report_q).filter(orgnization_activity__organization__id=org_id).order_by('id')
            save_msg = "Changes to Output have been saved!"

    return {
        "report_quarter":report_q,
        "report_year":datetime.datetime.now().year,
        "organization":organization,
        "select_options":select_options,
        "workplan_areas":workplan_areas,
        "mhc_activities":mhc_activities,
        "mhc_activitie_ids":mhc_activitie_ids,
        "org_activities":org_activities,
        "org_activitie_ids":org_activitie_ids,
        "outputs_current":outputs_current,
        "outputs_previous":outputs_previous,
        "current_year":datetime.datetime.now().year,
        "error_msg":error_msg,
        "save_msg":save_msg,
        "tmp_username_list":tmp_username_list
    }

'''-----------------------
Output Report Page
-----------------------'''
# Report Template 1 - Liquid Fill Gauge
@login_required
@render_to("mhcdashboardapp/output_report_page_1.html")
def output_reportpage_1(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.all()
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "report_year":datetime.datetime.now().year,
    }

# Report Template 2 - Bullet Bar
@login_required
@render_to("mhcdashboardapp/output_report_page_2.html")
def output_reportpage_2(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.all()
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "report_year":datetime.datetime.now().year,
    }
    
# Report Builder with Template 1
@login_required
@render_to("mhcdashboardapp/output_reportpage_builder.html")
def output_reportpage_builder(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd,year=datetime.datetime.now().year)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "report_year":datetime.datetime.now().year,        
    }

# Report Builder with Template 2
@login_required
@render_to("mhcdashboardapp/output_reportpage_2_builder.html")
def output_reportpage_2_builder(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.all()
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "report_year":datetime.datetime.now().year,        
    }
    
@login_required
def output_create_customreport(request):
    if request.method == 'POST':
        for i in range(0,5):
            ikey = "data[%d][]" % i
            if ikey in request.POST and len(request.POST[ikey])>0:
                print request.POST[ikey]
    return HttpResponse('')

# Display customized report generated from report builder (template 1)
@login_required
@render_to("mhcdashboardapp/output_customreport.html")
def output_customreport(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd,year=datetime.datetime.now().year)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    highlight_text = []
    if request.method == 'POST':
        highlight_text.append({"A":request.POST["A"]})
        highlight_text.append({"B":request.POST["B"]})
        highlight_text.append({"C":request.POST["C"]})
        highlight_text.append({"D":request.POST["D"]})
        highlight_text.append({"E":request.POST["E"]})
    highlight_text_json = json.dumps(highlight_text)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "highlight_text":highlight_text_json
    }
    
# Display customized report generated from report builder (template 2)
@login_required
@render_to("mhcdashboardapp/output_customreport_2.html")
def output_customreport_2(request):
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Q1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", Q%d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd,year=datetime.datetime.now().year)
        outputs_pf_summary = []
        for wpa in workplan_areas:
            tmp_outputs_pf_summary = collections.OrderedDict([
            ("WPA",wpa.str_id),   
            ("WPA_name",wpa.description),
            ("perform",collections.OrderedDict([("Yes",0),("No",0),("NotReported",0),("TBD",0)]))
            ])
            wpa_outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                if wpa_output.is_goal is not None:
                    tmp_outputs_pf_summary["perform"][goal_choices[wpa_output.is_goal]] += 1
            outputs_pf_summary.append(tmp_outputs_pf_summary)
        outputs_summary.append({"name":wpd.description,"data":outputs_pf_summary})
    outputs_summary_json = json.dumps(outputs_summary)
    workplan_directions_json = json.dumps(wpds)
    highlight_text = []
    if request.method == 'POST':
        highlight_text.append({"A":request.POST["A"]})
        highlight_text.append({"B":request.POST["B"]})
        highlight_text.append({"C":request.POST["C"]})
        highlight_text.append({"D":request.POST["D"]})
        highlight_text.append({"E":request.POST["E"]})
    highlight_text_json = json.dumps(highlight_text)
    return {
        "closed_reporting_quarters":closed_reporting_quarters,
        "workplan_directions":workplan_directions_json,
        "barpiechart_data":outputs_summary_json,
        "highlight_text":highlight_text_json,
        "report_year":datetime.datetime.now().year,
    }

# Export report as PDF
@login_required
def output_customreport_pdf_2015(request):
    # Prepare data
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Quarter 1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", %d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd,year=datetime.datetime.now().year)
        tmp_wpd_pf_summary = {"total":0,"Yes":0,"No":0,"NotReported":0,"TBD":0}
        wpa_list = []
        for wpa in workplan_areas:
            wpa_list.append({wpa.str_id:wpa.description})
            wpa_outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                tmp_wpd_pf_summary["total"] += 1
                if wpa_output.is_goal is not None:
                    tmp_wpd_pf_summary[goal_choices[wpa_output.is_goal]] += 1
        outputs_summary.append({"name":"%s: %s"% (wpd.str_id,wpd.description),"wpa":wpa_list,"perform":tmp_wpd_pf_summary})
    
    # Generate PDF report
    ## Prepare HttpResponse for downloading PDF file
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"]="attachment; filename=\"report_%s.pdf\"" % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    ## PDF canvas config
    p_pagesize = letter # use letter as PDF page size
    p_isbottomup = 0 # place the origin (0,0) at the top left
    p_margin = 0.4 * inch # set page margin to 0.4 inch
    p_pagewidth = defaultPageSize[0]
    p_pageheight = defaultPageSize[1]
    styles = getSampleStyleSheet()
    p_width, p_height = p_pagesize # get width and height of pagesize
    
    ## Initiate pdf canvas
    p = canvas.Canvas(response,pagesize=p_pagesize,bottomup=p_isbottomup)
    
    # set page margin by moving origin point to the top left margin point
#    p.translate(p_margin,p_margin)
    
    ## Page 1
    ### Report Title
    p_title = "Report Summary"
    txtobj = p.beginText()
    txtobj.setTextOrigin(40,60)
    txtobj.setFont("Helvetica-BoldOblique",20)
    txtobj.textLine(p_title)
    p.setFillColor(HexColor("#08426A"))
    p.drawText(txtobj)
    #### Report Sub-title
    p_title = "Outputs in 2015 %s" % closed_reporting_quarters
    txtobj = p.beginText()
    txtobj.setTextOrigin(140,100)
    txtobj.setFont("Helvetica-BoldOblique",18)
    txtobj.textLine(p_title)
    p.setFillColor(HexColor("#08426A"))
    p.drawText(txtobj)
    p.rect(30,120,552,3,stroke=0,fill=1)
    #### MHC logo
    p.saveState()
    p.translate(430,115)
    p.scale(1,-1)
    mhc_logoimg_path = SOTRAGE_ROOTPATH.replace("data","img") + "mhc_logo.png"
    p.drawImage(mhc_logoimg_path,0,0,130,90,mask='auto')
    p.restoreState()
    
    ### WPD A
    #### WPD A heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[0]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,160)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD A body
    
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[0]["perform"]["Yes"],outputs_summary[0]["perform"]["No"],outputs_summary[0]["perform"]["NotReported"],outputs_summary[0]["perform"]["TBD"]]
#    pc.labels = ["Yes","Not reported"] # pie chart label
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
#    #popout pie slice
#    pc.slices[0].popout = 10
#    pc.slices[0].labelRadius = 1.75
#    r,g,b = rgb_to_scale(221,118,54)
#    pc.slices[0].fontColor = Color(r,g,b,1)
    d.add(pc)
    renderPDF.draw(d,p,40,175)
    
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,275,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,279,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,286,"Yes")
    p.drawString(115,286,str(outputs_summary[0]["perform"]["Yes"]))
    p.drawString(135,286,"%d%%" % round(outputs_summary[0]["perform"]["Yes"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,290,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,294,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,301,"No")
    p.drawString(115,301,str(outputs_summary[0]["perform"]["No"]))
    p.drawString(135,301,"%d%%" % round(outputs_summary[0]["perform"]["No"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,305,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,309,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,316,"Not reported")
    p.drawString(115,316,str(outputs_summary[0]["perform"]["NotReported"]))
    p.drawString(135,316,"%d%%" % round(outputs_summary[0]["perform"]["NotReported"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,320,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,324,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,331,"TBD")
    p.drawString(115,331,str(outputs_summary[0]["perform"]["TBD"]))
    p.drawString(135,331,"%d%%" % round(outputs_summary[0]["perform"]["TBD"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,335,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    
    ###### WPA A1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    # temporarily change the canvas by changing origin point and change scale to flip the image
    p.saveState()
    p.translate(180,240)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()# restore previous canvas settings
    ####### Paragraph
    p_wpa = "A1: Preservation of affordable housing and critical community facilities near transit"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,215-h-h/10)  
    ###### WPA A2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,240)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "A2: Development of new affordable housing and community facilities near transit"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,215-h-h/10)    
    ###### WPA A3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,320)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "A3: Increase and Align Financial Resources for Affordable Housing and Community Facilities"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,295-h-h/10)
    ###### WPA A4
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,320)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A4"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()# restore previous canvas settings
    ####### Paragraph
    p_wpa = "A4: Supporting Policy Environment: Promote Adoption of Equitable Regional Housing Strategy"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,295-h-h/10)
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-A"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 372
    if h == 12: # one row text
        parag_y += 0
    elif h == 24: # two rows
        parag_y -= 15
    elif h == 36: # three rows
        parag_y -= 35  
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,400,530,1.5,stroke=0,fill=1)    
    
    ### WPD B
    
    #### WPD B heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[1]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,440)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD B body
    
    #### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[1]["perform"]["Yes"],outputs_summary[1]["perform"]["No"],outputs_summary[1]["perform"]["NotReported"],outputs_summary[1]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,475)
    
    #### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,575,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,579,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,586,"Yes")
    p.drawString(115,586,str(outputs_summary[1]["perform"]["Yes"]))
    p.drawString(135,586,"%d%%" % round(outputs_summary[1]["perform"]["Yes"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,590,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,594,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,601,"No")
    p.drawString(115,601,str(outputs_summary[1]["perform"]["No"]))
    p.drawString(135,601,"%d%%" % round(outputs_summary[1]["perform"]["No"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,605,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,609,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,616,"Not reported")
    p.drawString(115,616,str(outputs_summary[1]["perform"]["NotReported"]))
    p.drawString(135,616,"%d%%" % round(outputs_summary[1]["perform"]["NotReported"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,620,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,624,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,631,"TBD")
    p.drawString(115,631,str(outputs_summary[1]["perform"]["TBD"]))
    p.drawString(135,631,"%d%%" % round(outputs_summary[1]["perform"]["TBD"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,635,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA B1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,510)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B1: Sun Valley Pilot: Connecting residents to good jobs in a redeveloping transit area"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,485-h-h/10)
    ###### WPA B2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,510)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B2: Park Hill Village West Project: Connecting residents to good jobs in a newly developing transit area"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,485-h-h/10)    
    ###### WPA B3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,580)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
   ####### Paragraph
    p_wpa = "B3: Anschutz Campus Project: Connecting residents to good jobs via anchor institution"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,555-h-h/10)
    ###### WPA B4
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,580)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B4"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
   ####### Paragraph
    p_wpa = "B4: Supporting Policy Environment: Equitable Regional Economic Strategy"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,555-h-h/10)
    ###### WPA B5
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,650)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B5"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B5: Supporting Policy Environment: Incentivize Businesses Providing Good Jobs to Locate Near Transit"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,625-h-h/10)
    ###### WPA B6
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,650)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B6"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B6: Increase and Align Financial Resources for Commercial Facilities and Tenants Near Transit"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,625-h-h/10)
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-B"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 690
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    #### Page footer
    p.setFillColor(HexColor("#777777"))
    p.rect(35,750,540,0.5,stroke=0,fill=1)
    p.setFont("Helvetica",8)
    p.drawString(50,760,"* No output to report in current quarter.")
    p.setFont("Helvetica",9)
    p.drawString(520,763,"Page 1 of 2")
    
    ## Print Page 1
    p.showPage()
    
    ## Page 2
    
    ### WPD C
    #### WPD C heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[2]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,60)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD C body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[2]["perform"]["Yes"],outputs_summary[2]["perform"]["No"],outputs_summary[2]["perform"]["NotReported"],outputs_summary[2]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,65)
    
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,165,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,169,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,176,"Yes")
    p.drawString(115,176,str(outputs_summary[2]["perform"]["Yes"]))
    p.drawString(135,176,"%d%%" % round(outputs_summary[2]["perform"]["Yes"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,180,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,184,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,191,"No")
    p.drawString(115,191,str(outputs_summary[2]["perform"]["No"]))
    p.drawString(135,191,"%d%%" % round(outputs_summary[2]["perform"]["No"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,195,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,199,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,206,"Not reported")
    p.drawString(115,206,str(outputs_summary[2]["perform"]["NotReported"]))
    p.drawString(135,206,"%d%%" % round(outputs_summary[2]["perform"]["NotReported"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,210,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,214,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,221,"TBD")
    p.drawString(115,221,str(outputs_summary[2]["perform"]["TBD"]))
    p.drawString(135,221,"%d%%" % round(outputs_summary[2]["perform"]["TBD"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,225,120,0.5,stroke=0,fill=1)
    
    #### WPA
    ###### WPA C1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,140)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph   
    p_wpa = "C1: Affordable Bus and Light Rail Fares for Low-Income Riders and Commuters"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,115-h-h/10)    
    ###### WPA C2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,140)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "C2: Affordable Bus and Light Rail Fares for Students: My Denver Card"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,115-h-h/10)    
    ###### WPA C3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,210)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "C3: Ensuring Accessible Bus Service Routes for Low-Income Communities"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,185-h-h/10)
    
    #### Narratives
    p_wpd_narratives = request.POST["TEXT-C"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 240
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,270,530,1.5,stroke=0,fill=1)    
    
    ### WPD D
    #### WPD D heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[3]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,300)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)

    #### WPD D body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[3]["perform"]["Yes"],outputs_summary[3]["perform"]["No"],outputs_summary[3]["perform"]["NotReported"],outputs_summary[3]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,305)

    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,405,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,409,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,416,"Yes")
    p.drawString(115,416,str(outputs_summary[3]["perform"]["Yes"]))
    p.drawString(135,416,"%d%%" % round(outputs_summary[3]["perform"]["Yes"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,420,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,424,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,431,"No")
    p.drawString(115,431,str(outputs_summary[3]["perform"]["No"]))
    p.drawString(135,431,"%d%%" % round(outputs_summary[3]["perform"]["No"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,435,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,439,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,446,"Not reported")
    p.drawString(115,446,str(outputs_summary[3]["perform"]["NotReported"]))
    p.drawString(135,446,"%d%%" % round(outputs_summary[3]["perform"]["NotReported"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,450,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,454,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,461,"TBD")
    p.drawString(115,461,str(outputs_summary[3]["perform"]["TBD"]))
    p.drawString(135,461,"%d%%" % round(outputs_summary[3]["perform"]["TBD"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,465,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA D1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,380)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["D1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "D1: Identify Resources and Strategies to Fund First and Last Mile Connections Solutions"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,355-h-h/10)    
    ###### WPA D2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,380)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["D2"].decode('base64'))),0,0,width=50,height=50)
    # restore previous canvas settings
    p.restoreState()
    ####### Paragraph
    p_wpa = "D2: Improving First and Last Mile Connections in Neighborhoods and Job Centers"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,355-h-h/10)
    
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-D"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 480
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,510,530,1.5,stroke=0,fill=1)    

    ### WPD E
    #### WPD E heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[4]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,540)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)

    #### WPD E body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[4]["perform"]["Yes"],outputs_summary[4]["perform"]["No"],outputs_summary[4]["perform"]["NotReported"],outputs_summary[4]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,545)
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,645,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,649,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,656,"Yes")
    p.drawString(115,656,str(outputs_summary[4]["perform"]["Yes"]))
    p.drawString(135,656,"%d%%" % round(outputs_summary[4]["perform"]["Yes"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,660,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,664,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,671,"No")
    p.drawString(115,671,str(outputs_summary[4]["perform"]["No"]))
    p.drawString(135,671,"%d%%" % round(outputs_summary[4]["perform"]["No"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,675,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,679,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,686,"Not reported")
    p.drawString(115,686,str(outputs_summary[4]["perform"]["NotReported"]))
    p.drawString(135,686,"%d%%" % round(outputs_summary[4]["perform"]["NotReported"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,690,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,694,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,701,"TBD")
    p.drawString(115,701,str(outputs_summary[4]["perform"]["TBD"]))
    p.drawString(135,701,"%d%%" % round(outputs_summary[4]["perform"]["TBD"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,705,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA E1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,620)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E1: Communications and Outreach"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,595-h-h/10)    
    ###### WPA E2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,620)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E2: Funder Cultivation, Fundraising, Responsive and Directed Grantmaking"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,595-h-h/10)
    ###### WPA E3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,690)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E3: Partner and staff engagement, management and support"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,665-h-h/10)    
    ###### WPA E4
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,620)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E4"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E4: Operational systems and policies"
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,665-h-h/10)

    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-E"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 720
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    #### Page footer
    p.setFillColor(HexColor("#777777"))
    p.rect(35,750,540,0.5,stroke=0,fill=1)    
    p.setFont("Helvetica",8)
    p.drawString(50,760,"* No output to report in current quarter.")
    p.setFont("Helvetica",9)    
    p.drawString(520,763,"Page 2 of 2")    

    ## Print Page 2
    p.showPage()
    
    # Save Canvas
    p.save()

    return response

@login_required
def output_customreport_pdf_2016(request):
    # Prepare data
    previous_report_quarter = report_quarter() - 1
    closed_reporting_quarters = "Quarter 1"
    if previous_report_quarter < 1:
        previous_report_quarter =  1
    else:
        closed_reporting_quarters += "".join((", %d" % q for q in range(2,previous_report_quarter+1)))
    outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year)
    outputs_summary = []
    workplan_directions = WorkplanDirection.objects.all()
    wpds = []
    wpa_text = {}
    goal_choices = {1:"Yes",0:"No",-1:"NotReported",-99:"TBD"}
    for wpd in workplan_directions:
        wpds.append({"str_id":wpd.str_id,"description":wpd.description})
        workplan_areas = WorkplanArea.objects.filter(workplan_direction=wpd,year=datetime.datetime.now().year)
        tmp_wpd_pf_summary = {"total":0,"Yes":0,"No":0,"NotReported":0,"TBD":0}
        wpa_list = []
        for wpa in workplan_areas:
            wpa_list.append({wpa.str_id:wpa.description})
            wpa_text[wpa.str_id] = wpa.description
            wpa_outputs = Output.objects.filter(orgnization_activity__year=datetime.datetime.now().year).filter(orgnization_activity__workplan_area=wpa).filter(active_quarter__quarter__lte=previous_report_quarter)
            for wpa_output in wpa_outputs:
                tmp_wpd_pf_summary["total"] += 1
                if wpa_output.is_goal is not None:
                    tmp_wpd_pf_summary[goal_choices[wpa_output.is_goal]] += 1
        outputs_summary.append({"name":"%s: %s"% (wpd.str_id,wpd.description),"wpa":wpa_list,"perform":tmp_wpd_pf_summary})
    
    # Generate PDF report
    ## Prepare HttpResponse for downloading PDF file
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"]="attachment; filename=\"report_%s.pdf\"" % datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    ## PDF canvas config
    p_pagesize = letter # use letter as PDF page size
    p_isbottomup = 0 # place the origin (0,0) at the top left
    p_margin = 0.4 * inch # set page margin to 0.4 inch
    p_pagewidth = defaultPageSize[0]
    p_pageheight = defaultPageSize[1]
    styles = getSampleStyleSheet()
    p_width, p_height = p_pagesize # get width and height of pagesize
    
    ## Initiate pdf canvas
    p = canvas.Canvas(response,pagesize=p_pagesize,bottomup=p_isbottomup)
    
    # set page margin by moving origin point to the top left margin point
#    p.translate(p_margin,p_margin)
    
    ## Page 1
    ### Report Title
    p_title = "Report Summary"
    txtobj = p.beginText()
    txtobj.setTextOrigin(40,60)
    txtobj.setFont("Helvetica-BoldOblique",20)
    txtobj.textLine(p_title)
    p.setFillColor(HexColor("#08426A"))
    p.drawText(txtobj)
    #### Report Sub-title
    p_title = "Outputs in 2016 %s" % closed_reporting_quarters
    txtobj = p.beginText()
    txtobj.setTextOrigin(140,100)
    txtobj.setFont("Helvetica-BoldOblique",18)
    txtobj.textLine(p_title)
    p.setFillColor(HexColor("#08426A"))
    p.drawText(txtobj)
    p.rect(30,120,552,3,stroke=0,fill=1)
    #### MHC logo
    p.saveState()
    p.translate(430,115)
    p.scale(1,-1)
    mhc_logoimg_path = SOTRAGE_ROOTPATH.replace("data","img") + "mhc_logo.png"
    p.drawImage(mhc_logoimg_path,0,0,130,90,mask='auto')
    p.restoreState()
    
    ### WPD A
    #### WPD A heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[0]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,160)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD A body
    
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[0]["perform"]["Yes"],outputs_summary[0]["perform"]["No"],outputs_summary[0]["perform"]["NotReported"],outputs_summary[0]["perform"]["TBD"]]
#    pc.labels = ["Yes","Not reported"] # pie chart label
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
#    #popout pie slice
#    pc.slices[0].popout = 10
#    pc.slices[0].labelRadius = 1.75
#    r,g,b = rgb_to_scale(221,118,54)
#    pc.slices[0].fontColor = Color(r,g,b,1)
    d.add(pc)
    renderPDF.draw(d,p,40,195)
    
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,295,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,299,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,306,"Yes")
    p.drawString(115,306,str(outputs_summary[0]["perform"]["Yes"]))
    p.drawString(135,306,"%d%%" % round(outputs_summary[0]["perform"]["Yes"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,310,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,314,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,321,"No")
    p.drawString(115,321,str(outputs_summary[0]["perform"]["No"]))
    p.drawString(135,321,"%d%%" % round(outputs_summary[0]["perform"]["No"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,325,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,329,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,336,"Not reported")
    p.drawString(115,336,str(outputs_summary[0]["perform"]["NotReported"]))
    p.drawString(135,336,"%d%%" % round(outputs_summary[0]["perform"]["NotReported"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,340,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,344,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,351,"TBD")
    p.drawString(115,351,str(outputs_summary[0]["perform"]["TBD"]))
    p.drawString(135,351,"%d%%" % round(outputs_summary[0]["perform"]["TBD"]*1.0/outputs_summary[0]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,355,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    
    ###### WPA A1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    # temporarily change the canvas by changing origin point and change scale to flip the image
    p.saveState()
    p.translate(180,240)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()# restore previous canvas settings
    ####### Paragraph
    p_wpa = "A1: %s" % wpa_text["A1"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(300,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,215-h-h/10)  
    ###### WPA A2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,330)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "A2: %s" % wpa_text["A2"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(130,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,300-h-h/10)    
    ###### WPA A3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,330)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "A3: %s" % wpa_text["A3"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,300-h-h/10)
#    ###### WPA A4
#    p.setStrokeColor(HexColor("#178BCA"))
#    p.setFillColor(HexColor("#178BCA"))
#    ####### Water Bubble
#    p.saveState()
#    p.translate(380,320)
#    p.scale(1,-1)
#    p.drawImage(ImageReader(StringIO.StringIO(request.POST["A4"].decode('base64'))),0,0,width=50,height=50)
#    p.restoreState()# restore previous canvas settings
#    ####### Paragraph
#    p_wpa = "A4: Supporting Policy Environment: Promote Adoption of Equitable Regional Housing Strategy"
#    para_style = styles["Heading4"]
#    para_style.fontName = "Helvetica"
#    para_style.fontSize = 11
#    para_style.textColor = HexColor("#777777")
#    parag = Paragraph(p_wpa,para_style)
#    w,h = parag.wrap(120,80)
#    p.setFillColor(HexColor("#DD7636"))
#    parag.drawOn(p,445,295-h-h/10)
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-A"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 392
    if h == 12: # one row text
        parag_y += 0
    elif h == 24: # two rows
        parag_y -= 15
    elif h == 36: # three rows
        parag_y -= 35  
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,430,530,1.5,stroke=0,fill=1)    
    
    ### WPD B
    
    #### WPD B heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[1]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,470)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD B body
    
    #### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[1]["perform"]["Yes"],outputs_summary[1]["perform"]["No"],outputs_summary[1]["perform"]["NotReported"],outputs_summary[1]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,505)
    
    #### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,605,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,609,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,616,"Yes")
    p.drawString(115,616,str(outputs_summary[1]["perform"]["Yes"]))
    p.drawString(135,616,"%d%%" % round(outputs_summary[1]["perform"]["Yes"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,620,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,624,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,631,"No")
    p.drawString(115,631,str(outputs_summary[1]["perform"]["No"]))
    p.drawString(135,631,"%d%%" % round(outputs_summary[1]["perform"]["No"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,635,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,639,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,646,"Not reported")
    p.drawString(115,646,str(outputs_summary[1]["perform"]["NotReported"]))
    p.drawString(135,646,"%d%%" % round(outputs_summary[1]["perform"]["NotReported"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,650,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,654,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,661,"TBD")
    p.drawString(115,661,str(outputs_summary[1]["perform"]["TBD"]))
    p.drawString(135,661,"%d%%" % round(outputs_summary[1]["perform"]["TBD"]*1.0/outputs_summary[1]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,665,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA B1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,565)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B1: %s" % wpa_text["B1"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,545-h-h/10)
    ###### WPA B2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,565)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
    ####### Paragraph
    p_wpa = "B2: %s" % wpa_text["B2"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,545-h-h/10)    
    ###### WPA B3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,645)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
   ####### Paragraph
    p_wpa = "B3: %s" % wpa_text["B3"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,625-h-h/10)
    ###### WPA B4
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,645)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B4"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState() # restore previous canvas settings
   ####### Paragraph
    p_wpa = "B4: %s" % wpa_text["B4"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,445,625-h-h/10)
#    ###### WPA B5
#    p.setStrokeColor(HexColor("#178BCA"))
#    p.setFillColor(HexColor("#178BCA"))
#    ####### Water Bubble
#    p.saveState()
#    p.translate(180,650)
#    p.scale(1,-1)
#    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B5"].decode('base64'))),0,0,width=50,height=50)
#    p.restoreState() # restore previous canvas settings
#    ####### Paragraph
#    p_wpa = "B5: Supporting Policy Environment: Incentivize Businesses Providing Good Jobs to Locate Near Transit"
#    para_style = styles["Heading4"]
#    para_style.fontName = "Helvetica"
#    para_style.fontSize = 11
#    para_style.textColor = HexColor("#777777")
#    parag = Paragraph(p_wpa,para_style)
#    w,h = parag.wrap(120,80)
#    p.setFillColor(HexColor("#DD7636"))
#    parag.drawOn(p,245,625-h-h/10)
#    ###### WPA B6
#    p.setStrokeColor(HexColor("#178BCA"))
#    p.setFillColor(HexColor("#178BCA"))
#    ####### Water Bubble
#    p.saveState()
#    p.translate(380,650)
#    p.scale(1,-1)
#    p.drawImage(ImageReader(StringIO.StringIO(request.POST["B6"].decode('base64'))),0,0,width=50,height=50)
#    p.restoreState() # restore previous canvas settings
#    ####### Paragraph
#    p_wpa = "B6: Increase and Align Financial Resources for Commercial Facilities and Tenants Near Transit"
#    para_style = styles["Heading4"]
#    para_style.fontName = "Helvetica"
#    para_style.fontSize = 11
#    para_style.textColor = HexColor("#777777")
#    parag = Paragraph(p_wpa,para_style)
#    w,h = parag.wrap(120,80)
#    p.setFillColor(HexColor("#DD7636"))
#    parag.drawOn(p,445,625-h-h/10)
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-B"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 700
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    #### Page footer
    p.setFillColor(HexColor("#777777"))
    p.rect(35,750,540,0.5,stroke=0,fill=1)
    p.setFont("Helvetica",8)
    p.drawString(50,760,"* No output to report in current quarter.")
    p.setFont("Helvetica",9)
    p.drawString(520,763,"Page 1 of 2")
    
    ## Print Page 1
    p.showPage()
    
    ## Page 2
    
    ### WPD C
    #### WPD C heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[2]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,60)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)
    
    #### WPD C body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[2]["perform"]["Yes"],outputs_summary[2]["perform"]["No"],outputs_summary[2]["perform"]["NotReported"],outputs_summary[2]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,65)
    
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,165,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,169,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,176,"Yes")
    p.drawString(115,176,str(outputs_summary[2]["perform"]["Yes"]))
    p.drawString(135,176,"%d%%" % round(outputs_summary[2]["perform"]["Yes"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,180,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,184,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,191,"No")
    p.drawString(115,191,str(outputs_summary[2]["perform"]["No"]))
    p.drawString(135,191,"%d%%" % round(outputs_summary[2]["perform"]["No"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,195,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,199,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,206,"Not reported")
    p.drawString(115,206,str(outputs_summary[2]["perform"]["NotReported"]))
    p.drawString(135,206,"%d%%" % round(outputs_summary[2]["perform"]["NotReported"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,210,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,214,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,221,"TBD")
    p.drawString(115,221,str(outputs_summary[2]["perform"]["TBD"]))
    p.drawString(135,221,"%d%%" % round(outputs_summary[2]["perform"]["TBD"]*1.0/outputs_summary[2]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,225,120,0.5,stroke=0,fill=1)
    
    #### WPA
    ###### WPA C1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,150)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph   
    p_wpa = "C1: %s" % wpa_text["C1"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,125-h-h/10)    
    ###### WPA C2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,150)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "C2: %s" % wpa_text["C2"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,125-h-h/10)    
#    ###### WPA C3
#    p.setStrokeColor(HexColor("#178BCA"))
#    p.setFillColor(HexColor("#178BCA"))
#    ####### Water Bubble
#    p.saveState()
#    p.translate(180,210)
#    p.scale(1,-1)
#    p.drawImage(ImageReader(StringIO.StringIO(request.POST["C3"].decode('base64'))),0,0,width=50,height=50)
#    p.restoreState()
#    ####### Paragraph
#    p_wpa = "C3: Ensuring Accessible Bus Service Routes for Low-Income Communities"
#    para_style = styles["Heading4"]
#    para_style.fontName = "Helvetica"
#    para_style.fontSize = 11
#    para_style.textColor = HexColor("#777777")
#    parag = Paragraph(p_wpa,para_style)
#    w,h = parag.wrap(120,80)
#    p.setFillColor(HexColor("#DD7636"))
#    parag.drawOn(p,245,185-h-h/10)
    
    #### Narratives
    p_wpd_narratives = request.POST["TEXT-C"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 240
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,270,530,1.5,stroke=0,fill=1)    
    
    ### WPD D
    #### WPD D heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[3]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,300)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)

    #### WPD D body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[3]["perform"]["Yes"],outputs_summary[3]["perform"]["No"],outputs_summary[3]["perform"]["NotReported"],outputs_summary[3]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,305)

    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,405,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,409,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,416,"Yes")
    p.drawString(115,416,str(outputs_summary[3]["perform"]["Yes"]))
    p.drawString(135,416,"%d%%" % round(outputs_summary[3]["perform"]["Yes"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,420,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,424,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,431,"No")
    p.drawString(115,431,str(outputs_summary[3]["perform"]["No"]))
    p.drawString(135,431,"%d%%" % round(outputs_summary[3]["perform"]["No"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,435,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,439,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,446,"Not reported")
    p.drawString(115,446,str(outputs_summary[3]["perform"]["NotReported"]))
    p.drawString(135,446,"%d%%" % round(outputs_summary[3]["perform"]["NotReported"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,450,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,454,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,461,"TBD")
    p.drawString(115,461,str(outputs_summary[3]["perform"]["TBD"]))
    p.drawString(135,461,"%d%%" % round(outputs_summary[3]["perform"]["TBD"]*1.0/outputs_summary[3]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,465,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA D1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,380)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["D1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "D1: %s" % wpa_text["D1"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,355-h-h/10)    
    ###### WPA D2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,380)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["D2"].decode('base64'))),0,0,width=50,height=50)
    # restore previous canvas settings
    p.restoreState()
    ####### Paragraph
    p_wpa = "D2: %s" % wpa_text["D2"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,355-h-h/10)
    ###### WPA D3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,460)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["D2"].decode('base64'))),0,0,width=50,height=50)
    # restore previous canvas settings
    p.restoreState()
    ####### Paragraph
    p_wpa = "D3: %s" % wpa_text["D3"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(160,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,440-h-h/10)    
    
    
    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-D"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 480
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    ##### Break Line
    p.setStrokeColor(HexColor("#C0C0C0"))
    p.setFillColor(HexColor("#C0C0C0"))
    p.rect(40,510,530,1.5,stroke=0,fill=1)    

    ### WPD E
    #### WPD E heading
    p_title_wpd = "Work Plan Direction %s" % outputs_summary[4]["name"]
    txtobj = p.beginText()
    txtobj.setTextOrigin(60,540)
    txtobj.setFont("Helvetica-Bold",14)
    txtobj.textLine(p_title_wpd)
    p.setFillColor(HexColor("#333333"))
    p.drawText(txtobj)

    #### WPD E body
    ##### Pie chart
    d = Drawing(190,190)
    pc = Pie()
    pc.x = 10
    pc.y = 0
    pc.width = 95
    pc.height = 95
    pc.data = [outputs_summary[4]["perform"]["Yes"],outputs_summary[4]["perform"]["No"],outputs_summary[4]["perform"]["NotReported"],outputs_summary[4]["perform"]["TBD"]]
    pc.slices.strokeWidth = 1
    pc.slices.strokeColor = HexColor("#FFFFFF")
    pc.slices[0].fillColor = HexColor("#41AB5D")
    pc.slices[1].fillColor = HexColor("#E08214")
    pc.slices[2].fillColor = HexColor("#807DBA")
    pc.slices[3].fillColor = HexColor("#307DBA")
    d.add(pc)
    renderPDF.draw(d,p,40,545)
    ##### Pie chart legend
    ###### Row 1 "Yes"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,645,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#41AB5D"))
    p.rect(45,649,9,9,stroke=0,fill=1)
    p.setFont("Helvetica",9)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,656,"Yes")
    p.drawString(115,656,str(outputs_summary[4]["perform"]["Yes"]))
    p.drawString(135,656,"%d%%" % round(outputs_summary[4]["perform"]["Yes"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))
    ###### Row 2 "No"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,660,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#E08214"))
    p.rect(45,664,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,671,"No")
    p.drawString(115,671,str(outputs_summary[4]["perform"]["No"]))
    p.drawString(135,671,"%d%%" % round(outputs_summary[4]["perform"]["No"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))
    ###### Row 3 "Not reported"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,675,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#807DBA"))
    p.rect(45,679,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,686,"Not reported")
    p.drawString(115,686,str(outputs_summary[4]["perform"]["NotReported"]))
    p.drawString(135,686,"%d%%" % round(outputs_summary[4]["perform"]["NotReported"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))    
    ###### Row 4 "TBD"
    p.setFillColor(HexColor("#808080"))
    p.rect(40,690,120,0.5,stroke=0,fill=1)
    p.setFillColor(HexColor("#307DBA"))
    p.rect(45,694,9,9,stroke=0,fill=1)
    p.setFillColor(HexColor("#333333"))
    p.drawString(60,701,"TBD")
    p.drawString(115,701,str(outputs_summary[4]["perform"]["TBD"]))
    p.drawString(135,701,"%d%%" % round(outputs_summary[4]["perform"]["TBD"]*1.0/outputs_summary[4]["perform"]["total"]*100,0))    
    p.setFillColor(HexColor("#808080"))
    p.rect(40,705,120,0.5,stroke=0,fill=1)
    
    ##### WPA
    ###### WPA E1
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,620)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E1"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E1: %s" % wpa_text["E1"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,595-h-h/10)    
    ###### WPA E2
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,620)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E2"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E2: %s" % wpa_text["E2"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,595-h-h/10)
    ###### WPA E3
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(180,690)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E3"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E3: %s" % wpa_text["E3"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,245,665-h-h/10)    
    ###### WPA E4
    p.setStrokeColor(HexColor("#178BCA"))
    p.setFillColor(HexColor("#178BCA"))
    ####### Water Bubble
    p.saveState()
    p.translate(380,690)
    p.scale(1,-1)
    p.drawImage(ImageReader(StringIO.StringIO(request.POST["E4"].decode('base64'))),0,0,width=50,height=50)
    p.restoreState()
    ####### Paragraph
    p_wpa = "E4: %s" % wpa_text["E4"]
    para_style = styles["Heading4"]
    para_style.fontName = "Helvetica"
    para_style.fontSize = 11
    para_style.textColor = HexColor("#777777")
    parag = Paragraph(p_wpa,para_style)
    w,h = parag.wrap(120,80)
    p.setFillColor(HexColor("#DD7636"))
    parag.drawOn(p,450,670-h-h/10)

    ##### Narratives
    p_wpd_narratives = request.POST["TEXT-E"]
    para_style = styles["BodyText"]
    para_style.fontName = "Helvetica-Oblique"
    para_style.textColor = HexColor("#DD7636")
    parag = Paragraph(p_wpd_narratives,para_style)
    w,h = parag.wrap(500,60)
    p.setFillColor(HexColor("#DD7636"))
    parag_y = 720
    if h == 12:
        parag_y += 10
    elif h == 24:
        parag_y -= 10
    elif h == 36:
        parag_y -= 25    
    parag.drawOn(p,50,parag_y)
    
    #### Page footer
    p.setFillColor(HexColor("#777777"))
    p.rect(35,750,540,0.5,stroke=0,fill=1)    
    p.setFont("Helvetica",8)
    p.drawString(50,760,"* No output to report in current quarter.")
    p.setFont("Helvetica",9)    
    p.drawString(520,763,"Page 2 of 2")    

    ## Print Page 2
    p.showPage()
    
    # Save Canvas
    p.save()

    return response


'''-----------------------
Export CSV
-----------------------'''
# Export Builder
@login_required
@render_to("mhcdashboardapp/output_report_exportcsv.html")
def output_exportbuilder(request):
    reportingquarters = ActiveQuarter.objects.all()
    organizations = []
    orgs = Organization.objects.all()
    # get only organizations that have outputs
    for org in orgs:
        if org._get_activity_quarters() != "No active quarters reporting on":
            organizations.append(org)    
    wpdirections = WorkplanDirection.objects.all()
    error_msg = None
    download_file = None
    if request.method == 'GET' and request.GET:
        if "error" in request.GET and request.GET["error"] == "true":
            if "org" in request.GET and request.GET["org"] != "":
                org_name = Organization.objects.get(id=int(request.GET["org"])).name
                if "wpd" in request.GET and request.GET["wpd"] != "":
                    wpd_description = WorkplanDirection.objects.get(id=int(request.GET["wpd"])).description
                    if "q" in request.GET and request.GET["q"] != "":
                        q = request.GET["q"]
                        error_msg = "Organization %s has no outputs in work plan direction %s in 2016 Quarter %s." % (org_name,wpd_description,q)
                    else:
                        error_msg = "Organization %s has no outputs in work plan direction %s." % (org_name,wpd_description)
                else:
                    error_msg = "There is no outputs for organization %s." % org_name
            else:
                if "wpd" in request.GET and request.GET["wpd"] != "":
                    wpd_description = WorkplanDirection.objects.get(id=int(request.GET["wpd"])).description
                    if "q" in request.GET and request.GET["q"] != "":
                        q = request.GET["q"]
                        error_msg = "There is no outputs in work plan direction %s in 2016 Quarter %s." % (wpd_description,q)
                    else:                    
                        error_msg = "There is no outputs in work plan direction %s." % wpd_description
                else:
                    if "q" in request.GET and request.GET["q"] != "":
                        q = request.GET["q"]
                        error_msg = "There is no outputs in 2016 Quarter %s." % q
        elif "file" in request.GET and request.GET["file"] != "":
            download_file = request.GET["file"]
    years = range(2015,datetime.datetime.now().year+1)
    years.reverse()
    return {
            "error_msg":error_msg,
            "download_file":download_file,
            "organizations":organizations,
            "wpdirections":wpdirections,
            "years":years,
            "reportingquarters":reportingquarters,
            }

class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

# Export Output as CSV file
def exportcsv_output(request,org_id,wpd_id,y_id,q_id):
    # get all outputs
    outputs = Output.objects.filter(orgnization_activity__year=y_id)
    redirect_url = ""
    
    if org_id and int(org_id) > 0:
        outputs = outputs.filter(orgnization_activity__organization__id=org_id)
        if wpd_id and int(wpd_id) > 0:
            outputs = outputs.filter(orgnization_activity__workplan_area__workplan_direction__id=wpd_id)
            if q_id and int(q_id) > 0:
                outputs = outputs.filter(active_quarter__id=q_id)
                redirect_url = "%s/output/report/exportbuilder?org=%s&wpd=%s&q=%s" % (ROOT_APP_URL,org_id,wpd_id,q_id)
            else:
                redirect_url = "%s/output/report/exportbuilder?org=%s&wpd=%s" % (ROOT_APP_URL,org_id,wpd_id)
    else:
        if wpd_id and int(wpd_id) > 0:
            outputs = outputs.filter(orgnization_activity__workplan_area__workplan_direction__id=wpd_id)
            if q_id and int(q_id) > 0:
                outputs = outputs.filter(active_quarter__id=q_id)
                redirect_url = "%s/output/report/exportbuilder?wpd=%s&q=%s" % (ROOT_APP_URL,wpd_id,q_id)
            else:
                redirect_url = "%s/output/report/exportbuilder?wpd=%s" % (ROOT_APP_URL,wpd_id)
        else:
            if q_id and int(q_id) > 0:
                outputs = outputs.filter(active_quarter__id=q_id)
                redirect_url = "%s/output/report/exportbuilder?q=%s" % (ROOT_APP_URL,q_id)
        
    if len(outputs) > 0:
        # headers
        headers = (
                    "Work Plan Area ID","Work Plan Area Description",
                    "MHC Activity ID","MHC Activity Description",
                    "Organization",
                    "Organization Activity ID","Organization Activity Description",
                    "Reporting Quarter",
                    "Output Description","Output Location",
                    "Goals Reached?","Output Value","Comment"
        )
        download_data = []
        for output in outputs:
            row_data = (
                        output.orgnization_activity.workplan_area.str_id,
                        output.orgnization_activity.workplan_area.description,
                        output.orgnization_activity.mhc_activity.str_id,
                        output.orgnization_activity.mhc_activity.description,
                        output.orgnization_activity.organization.abbreviation,
                        output.orgnization_activity.str_id,
                        output.orgnization_activity.description,
                        output.active_quarter.quarter if output.active_quarter else "",
                        smart_str(output.description),
                        smart_str(output.location),
                        output.get_is_goal_display(),
                        smart_str(output.output_value),
                        smart_str(output.comment)
            )
            download_data.append(row_data)

        # sort download content by work plan area string id
        download_data.sort(key=lambda row:row[0])
        
        # export as CSV
        tmp_name = "%d_MHC_Dashboard_Outputs_MasterDownload_%s" % (int(y_id),datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        csvfile_name = "%s.csv" % tmp_name
        #response = HttpResponse(content_type='text/csv')
        #response['Content-Disposition'] = 'attachment; filename="%s.csv"' % file_name
        #writer = csv.writer(response)
        # write headers
        #writer.writerow(headers)
        # write rows
#        for row in download_data:
#            writer.writerow([unicode(field).encode("utf-8") for field in row])
#        return response
#        pseudo_buffer = Echo()
#        writer = csv.writer(pseudo_buffer)
#        response = StreamingHttpResponse((writer.writerow(row) for row in download_data),content_type="text/csv")
#        response['Content-disposition'] = 'attachment; filename="%s.csv"' % file_name       
        
        # zip csv file
        zipfile_name = "%s.zip" % tmp_name     
        with ZipFile(SOTRAGE_ROOTPATH+zipfile_name,'w',ZIP_DEFLATED) as zipfile:
            output_table = StringIO.StringIO()
            csvwriter = csv.writer(output_table,delimiter=",",quotechar='"')
            csvwriter.writerow(headers)
            for row in download_data:
                csvwriter.writerow(row)
            zipfile.writestr(csvfile_name,output_table.getvalue())
        
        redirect_url = "%s/output/report/exportbuilder?file=%sdata/%s" % (ROOT_APP_URL,STATIC_URL,zipfile_name)
        response = redirect(redirect_url)
        response.set_cookie('fileDownload','True',path='/')
    else:
        redirect_url += "&error=true"
        response = redirect(redirect_url)
        
    return response


'''-----------------------
Login Instruction Page
-----------------------'''
# Indicators page
@render_to("mhcdashboardapp/login_instruction.html")
def login_instruction(request):
    return {
    }

'''------------------
Import data from CSV
------------------'''
MHC_DASHBOARD_DATA_PATH = "C:/QLiu/MileHighConnectsApp/Data/csv/" # use this for localhost
#MHC_DASHBOARD_DATA_PATH = '/home/admin/data/csv/' # use this for server
# Import Workplan Area
def importcsv_workplan_area(request):
    try:
        with open(MHC_DASHBOARD_DATA_PATH+"workplan_area_%d.csv" % datetime.datetime.now().year,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                workplan_area = WorkplanArea(
                    str_id = row[0].replace(" ",""),
                    description = row[1].strip(),
                    workplan_direction = WorkplanDirection.objects.get(str_id=row[2].strip()),
                    year = datetime.datetime.now().year
                )
                workplan_area.save()
        return HttpResponse("Workplan Area - Import complete!")
    except Exception as e:
        print e
        return HttpResponse("Workplan Area - Import Failed! Error: %s" % e)
    
# Import Organization
def importcsv_organization(request):
    try:
        with open(MHC_DASHBOARD_DATA_PATH+"organization.csv",'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                organization = Organization(
                    name=row[0].strip(),
                    abbreviation=row[1].strip(),
                    mission=row[2].strip()
                )
                organization.save()
        return HttpResponse("Organization - Import complete!")
    except Exception as e:
        print e
        return HttpResponse("Organization - Import Failed! Error: %s" % e)

# Import MHC Activity
def importcsv_mhc_activity(request):
    try:
        with open(MHC_DASHBOARD_DATA_PATH+"mhc_activity_%d.csv" % datetime.datetime.now().year,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                workplan_area_strid = row[0].replace(" ","")[:2]
                mhc_activity = MHCActivity(
                    str_id=row[0].replace(" ",""),
                    workplan_area=WorkplanArea.objects.get(str_id=workplan_area_strid,year=datetime.datetime.now().year) if workplan_area_strid != "" else None,
                    description=row[1].strip(),
                    year = datetime.datetime.now().year
                )
                mhc_activity.save()
        return HttpResponse("MHC Activity - Import complete!")
    except Exception as e:
        print e
        return HttpResponse("MHC Activity - Import Failed! Error: %s" % e)

# Import Organization Activity
def importcsv_org_activity(request):
    try:
        with open(MHC_DASHBOARD_DATA_PATH+"organization_activity_%d.csv" % datetime.datetime.now().year,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                str_ids = row[1].replace(" ","").split('.')
                workplan_area_str_id = str_ids[0]
                mhc_activity_str_id = "%s.%s" % (str_ids[0],str_ids[1])
                str_id_int = ord(str_ids[-1][-1])-96
                str_id = "%s.%d" % (mhc_activity_str_id,str_id_int)
                org_activity = OrganizationActivity(
#                    str_id=str_id,
                    workplan_area=WorkplanArea.objects.get(str_id=workplan_area_str_id,year=datetime.datetime.now().year) if workplan_area_str_id != "" else None,
                    mhc_activity=MHCActivity.objects.get(str_id=mhc_activity_str_id,year=datetime.datetime.now().year) if mhc_activity_str_id != "" else None,
                    organization=Organization.objects.get(abbreviation=row[0].strip()) if row[0] != "" else None,
                    description=row[2].strip(),
                    origin_strid=row[1].replace(" ",""),
                    year = datetime.datetime.now().year
                )
                org_activity.save()
        return HttpResponse("Organization Activity - Import complete!")
    except Exception as e:
        print e
        return HttpResponse("Organization Activity - Import Failed! Error: %s" % e)

# Import Output
def importcsv_output(request):
    try:
        with open(MHC_DASHBOARD_DATA_PATH+"output_%d.csv" % datetime.datetime.now().year,'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                str_ids = row[0].replace(" ","").split('.')
                workplan_area_str_id = str_ids[0]
                mhc_activity_str_id = "%s.%s" % (str_ids[0],str_ids[1])
                org_activity_str_id_int = ord(str_ids[-1][-1])-96
                org_activity_str_id = "%s.%d" % (mhc_activity_str_id,org_activity_str_id_int)
                output = Output(
                    orgnization_activity=OrganizationActivity.objects.get(origin_strid=row[0].replace(" ",""),year=datetime.datetime.now().year) if row[0] != "" else None,
                    active_quarter=ActiveQuarter.objects.get(quarter=int(row[1].replace(" ",""))) if row[1] != "" else None,
                    description=row[2].strip().replace(",",""),
                    #output_value=row[3].strip().replace(",",""),
                )
                output.save()
        return HttpResponse("Output - Import complete!")
    except Exception as e:
        print e
        return HttpResponse("Output - Import Failed! Error: %s" % e)

'''-----------------------
User functions
-----------------------'''   
# Register
@render_to("mhcdashboardapp/register.html")
def register(request):
    if request.method == 'POST':
        signup_form = UserCreationForm(request.POST)
        if signup_form.is_valid():
            new_user = signup_form.save()
            user = authenticate(username=signup_form.cleaned_data["username"], password=signup_form.cleaned_data["password2"])
            login(request, user)
            if "next" in request.GET:
                app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                return HttpResponseRedirect(request.GET["next"])
            else:
                url = request.META["HTTP_REFERER"]
                if url.partition("/?next=/")[1] == "":
                    if APP_SERVER_URL == "":
                        # a trick for localhost
                        app_name = url.partition("http://")[2].replace(SERVER_URL,"").partition("/")[2].partition("/")[0]
                    else:
                        app_name = url.partition("http://")[2].replace(SERVER_URL,"").replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                else:
                    app_name = url.partition("/?next=/")[2].partition("/")[0]
                return HttpResponseRedirect('%s/%s/home/' % (APP_SERVER_URL,app_name))            
        else:
            error_msg = "Please check your register information."
            return {'title':"Sign up",'error_msg':error_msg,'signup_form':signup_form}
    else:
        signup_form = UserCreationForm()
    return {'title':"Sign up",'signup_form':signup_form}


# User Profile
@login_required
@render_to("mhcdashboardapp/user_profile.html")
def user_profile(request):
    user = request.user
    if request.method == 'GET':
        user_profile_form = UserProfileForm(instance=user)
    elif request.method == 'POST':
        user_profile_form = UserProfileForm(data=request.POST, instance=user)
        if user_profile_form.is_valid():
            user_profile_form.save()
            messages.info(request, "User profile was changed successfully.")
            if 'save' in request.POST:
                if "next" in request.GET:
                    #app_name = request.GET["next"].replace(APP_SERVER_URL,"").partition("/")[2].partition("/")[0]
                    return HttpResponseRedirect(request.GET["next"])
                else:
                    return HttpResponseRedirect('%s/home/' % ROOT_APP_URL)                
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_profile_form':user_profile_form}

# User Change Password
@login_required
@render_to("mhcdashboardapp/user_password.html")
def user_change_password(request):
    user = request.user
    if request.method == 'GET':
        user_password_form = PasswordChangeForm(user)
    elif request.method == 'POST':
        user_password_form = PasswordChangeForm(user,request.POST)
        if user_password_form.is_valid():
            user_password_form.save()
            messages.info(request, "User password was changed successfully.")
            return HttpResponseRedirect('%s/user/profile/' % ROOT_APP_URL)
        else:
            messages.error(request, "Please correct the errors below.")
    return {'user_name':user.username,'user_password_form':user_password_form}

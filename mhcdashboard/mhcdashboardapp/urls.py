from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib.auth.views import logout

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('mhcdashboardapp.views',
	# Home page URL
	url(r'^home/$','home'),
	url(r'^indicator/$','indicator_index'),
	url(r'^login_instruction/$','login_instruction'),
	
	# Customized Admin Pages
#	url(r'^output/$','output_index'),
	url(r'^output/report/$','report_output'),
	url(r'^output/report/temporary/(?P<qid>\d+)/$','report_output_temp'),
	
	# Login,Logout,Register,User
	url(r'^logout/$',logout,{'template_name': 'registration/logged_out.html'}),
	url(r'^register/$','register'),
	url(r'^user/profile/$','user_profile'),
	url(r'^user/password/$','user_change_password'),	
	
	# Output Report Page
	url(r'output/report/reportpage1$','output_reportpage_1'),
	url(r'output/report/reportpage2$','output_reportpage_2'),
	# Report Builder
	url(r'output/report/report_builder/$','output_reportpage_builder'),
	url(r'output/report/reportpage1_builder$','output_reportpage_builder'),
	url(r'output/report/reportpage2_builder$','output_reportpage_2_builder'),
	url(r'output/report/createcustomreport/$','output_create_customreport'),
	url(r'output/report/customreport/$','output_customreport'),
	url(r'output/report/customreport2/$','output_customreport_2'),
	# PDF Report
	url(r'output/report/customreport/pdf/$','output_customreport_pdf_2016'),	
	
	# Export Data as CSV
	url(r'output/report/exportbuilder$','output_exportbuilder'),
	url(r'output/report/exportcsv/(?P<org_id>\d+)/(?P<wpd_id>\d+)/(?P<q_id>\d+)/$','exportcsv_output'),

	# Import Data from CSV
	url(r'dataimport/csv/workplan_area$','importcsv_workplan_area'),
	url(r'dataimport/csv/organization$','importcsv_organization'),
	url(r'dataimport/csv/mhc_activity$','importcsv_mhc_activity'),
	url(r'dataimport/csv/org_activity$','importcsv_org_activity'),
	url(r'dataimport/csv/output$','importcsv_output'),
)
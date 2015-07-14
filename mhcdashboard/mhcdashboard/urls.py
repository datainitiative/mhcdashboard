from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mhcdashboard.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    
    # MHC Dashboard App URLs
    url(r'^mhcdashboard/',include('mhcdashboardapp.urls')),    
    
    # 3rd party app url
    url(r'^chaining/', include('smart_selects.urls')),
)

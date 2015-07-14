from django.contrib import admin

from mhcdashboardapp.models import *

LIST_PER_PAGE = 10

class MyUserAdmin(admin.ModelAdmin):
    fields = ['user','organization']
    list_display = ('user','_get_user_first_name','_get_user_first_name','organization','_get_user_email')
    search_fields = ['user','_get_user_first_name','_get_user_first_name','organization','_get_user_email']
admin.site.register(MyUser,MyUserAdmin)

class DescriptorInline(admin.StackedInline):
    model = Descriptor
    extra = 1

class IndicatorAdmin(admin.ModelAdmin):
    fields = ['description','workplan_area']
    filter_horizontal = ['workplan_area']
    inlines = [DescriptorInline]
    list_display = ('id','description',)
    search_fields = ['description']
    list_per_page = LIST_PER_PAGE
    save_on_top = True
admin.site.register(Indicator,IndicatorAdmin)

class DescriptorAdmin(admin.ModelAdmin):
    fields = ['indicator','description','value','algorithm']
    list_display = ('indicator','description','value')
    search_fields = ['description']
admin.site.register(Descriptor,DescriptorAdmin)

class OrganizationAdmin(admin.ModelAdmin):
    fields = ['name','abbreviation','mission']
    list_display = ('name','abbreviation','_get_activity_quarters','_get_quarter_performance_comment')
    search_fields = ['name','abbreviation']
admin.site.register(Organization,OrganizationAdmin)

class ActiveQuarterAdmin(admin.ModelAdmin):
    fields = ['quarter']
admin.site.register(ActiveQuarter,ActiveQuarterAdmin)

class MHCActivityInline(admin.TabularInline):
    model = MHCActivity
    extra = 0
    exclude = ('str_id',)
    
class WorkplanDirectionAdmin(admin.ModelAdmin):
    fields = ['str_id','description']
    list_display = ('str_id','description')
    search_fields = ['description']
    list_per_page = LIST_PER_PAGE
admin.site.register(WorkplanDirection,WorkplanDirectionAdmin)

class WorkplanAreaAdmin(admin.ModelAdmin):
#    fieldsets = [
#        (None, {'fields':['str_id']}),
#        ('More Information', {'fields':['description'],'classes':['collapse']}),
#    ]
    fields = ['str_id','description','workplan_direction']
    inlines = [MHCActivityInline]
    list_display = ('str_id','description','workplan_direction')
    search_fields = ['str_id','description']
    list_filter = ['workplan_direction']
    list_per_page = LIST_PER_PAGE
    save_on_top = True
admin.site.register(WorkplanArea,WorkplanAreaAdmin)

class OrganizationActivityInline(admin.TabularInline):
    model = OrganizationActivity
    extra = 0
    readonly_fields = ('str_id',)
    exclude = ('q1_comment','q2_comment','q3_comment','q4_comment')

class MHCActivityAdmin(admin.ModelAdmin):
    fields = ['str_id','workplan_area','description']
    inlines = [OrganizationActivityInline]
    readonly_fields = ('str_id',)
    list_display = ('str_id','description','workplan_area')
    list_filter = ['workplan_area']
    search_fields = ['str_id','description']
    list_per_page = LIST_PER_PAGE
admin.site.register(MHCActivity,MHCActivityAdmin)

#class OutputActivityInline(admin.TabularInline):
#    model = OutputActivity
#    extra = 0
#    readonly_fields = ('str_id',)
    
#class OutputInline(admin.TabularInline):
#    model = Output
#    extra = 0
#    def formfield_for_foreignkey(self,db_field,request,**kwargs):
#        if db_field.name == 'output_activity':
#            if not "add" in request.path:
#                org_activity_id = int(request.path[request.path.index("/organizationactivity/")+len("/organizationactivity/"):-1])
#                kwargs['queryset'] = OutputActivity.objects.filter(orgnization_activity=org_activity_id)
#        return super(OutputInline,self).formfield_for_foreignkey(db_field,request,**kwargs)

class OutputInline(admin.TabularInline):
    model = Output
    fields = ['orgnization_activity','active_quarter','description','location','is_goal','output_value','comment']
    extra = 0

class OrganizationActivityAdmin(admin.ModelAdmin):
    fields = ['str_id','workplan_area','mhc_activity','organization','description','other_comment','q1_comment','q2_comment','q3_comment','q4_comment','_get_all_comments']
    inlines = [OutputInline]
    readonly_fields = ('str_id','q1_comment','q2_comment','q3_comment','q4_comment','_get_all_comments')
    list_display = ('str_id','workplan_area','mhc_activity','organization','description')
    search_fields = ['str_id','description']
    list_filter = ['workplan_area','mhc_activity','organization']
    list_per_page = LIST_PER_PAGE
admin.site.register(OrganizationActivity,OrganizationActivityAdmin)

#class OutputInline(admin.TabularInline):
#    model = Output
#    extra = 0

#class OutputActivityAdmin(admin.ModelAdmin):
#    fields = ['str_id','orgnization_activity','description','deadline']
##    inlines = [OutputInlineForOutputAct]
#    readonly_fields = ('str_id',)
#    list_display = ('str_id','orgnization_activity','description','deadline')
#    list_filter = ['orgnization_activity','deadline']
#    list_per_page = LIST_PER_PAGE
#admin.site.register(OutputActivity,OutputActivityAdmin)

class OutputAdmin(admin.ModelAdmin):
    fields = ['orgnization_activity','active_quarter','description','location','is_goal','output_value','comment']
    list_display = ('orgnization_activity','active_quarter','description','location','is_goal','output_value')
    search_fields = ['description']
    list_filter = ['orgnization_activity__organization','orgnization_activity','active_quarter','is_goal']
    list_per_page = LIST_PER_PAGE
admin.site.register(Output,OutputAdmin)
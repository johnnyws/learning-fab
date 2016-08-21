from flask import render_template, redirect, g
from flask.ext.appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.models.sqla.filters import FilterStartsWith, FilterEqualFunction
from flask.ext.appbuilder import ModelView, BaseView, AppBuilder, expose, has_access, SimpleFormView, MultipleView, MasterDetailView, action
from flask.ext.appbuilder.charts.views import DirectByChartView
from app import appbuilder, db
from flask.ext.babel import lazy_gettext as _, gettext

from wtforms import Form, StringField, TextField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, EqualTo
from flask.ext.appbuilder.fieldwidgets import BS3TextFieldWidget, Select2Widget
from flask.ext.appbuilder.forms import DynamicForm

from flask.ext.appbuilder.models.sqla.interface import SQLAInterface

from .models import ContactGroup, Contact, CountryStats, Employee, Department, Function, Benefit, EmployeeHistory

"""
    Create your Views::


    class MyModelView(ModelView):
        datamodel = SQLAInterface(MyModel)


    Next, register your Views::


    appbuilder.add_view(MyModelView, "My View", icon="fa-folder-open-o", category="My Category", category_icon='fa-envelope')
"""

"""
	Basic Views
"""
class MyView(BaseView):
    # route_base can be inferred?
    #route_base = "/myview"
    default_view = 'method1'

    @expose('/method1/')
    @has_access
    def method1(self):
        # do something with param1
        # and return it
        return 'Hello'

    @expose('/method2/<string:param1>')
    @has_access
    def method2(self, param1):
        # do something with param1
        # and render it
        param1 = 'Goodbye %s' % (param1)
        return param1

    @expose('/method3/<string:param1>')
    @has_access
    def method3(self, param1):
        # do something with param1
        # and render template with param
        param1 = 'Goodbye %s' % (param1)
        self.update_redirect()
        return self.render_template('method3.html',
                               param1 = param1)

class MyForm(DynamicForm):
    field1 = StringField(('Field1'),
        description=('Your field number one!'),
        validators = [DataRequired()], widget=BS3TextFieldWidget())
    field2 = StringField(('Field2'),
        description=('Your field number two!'), widget=BS3TextFieldWidget())

class MyFormView(SimpleFormView):
    form = MyForm
    form_title = 'This is my first form view'
    message = 'My form submitted'

    def form_get(self, form):
        form.field1.data = 'This was prefilled'

    def form_post(self, form):
        # post process form
        flash(self.message, 'info')

#appbuilder.add_view_no_menu(MyView())
appbuilder.add_view(MyView, "Method1", category='My View')
appbuilder.add_link("Method2", href='/myview/method2/john', category='My View')
appbuilder.add_link("Method3", href='/myview/method3/john', category='My View')
appbuilder.add_view(MyFormView, "My form View", icon="fa-group", label=_('My form View'),
                     category="My Forms", category_icon="fa-cogs")

class BS3TextFieldROWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs['readonly'] = 'true'
        return super(BS3TextFieldROWidget, self).__call__(field, **kwargs)

"""
	Model Views
"""
class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)

    base_order = ('name', 'desc')
    # pass extra args to Jinja2 template
    #extra_args = {'my_extra_arg':'SOMEVALUE'}
    #show_template = 'my_show_template.html'

    # filter the fields in the adding form
    # {add,edit,search}_form_query_rel_fields
    add_form_query_rel_fields = {'contact_group': [['name',FilterStartsWith,'W']]}
    #add_form = AddFormWTF  # customize add/edit forms
    #add_columns = ['my_field1', my_field2]  # customize add/edit form fields

    label_columns = {'contact_group':'Contacts Group'}  # define lables of columns

	# use {add,edit,list,show}_columns properties to customize what columns are displayed and orders
    list_columns = ['name','personal_celphone','birthday','contact_group']

    # add an extra field: e.g. confirmation field
    # TODO doesn't work...
    #add_form_extra_fields = {'some_col':BooleanField('Some Col', default=False)}
    add_form_extra_fields = {'confirm_name': TextField(gettext('Confirm Name'),
                    description=gettext('Confirm Name'),
                    widget=BS3TextFieldWidget())}
    #edit_form_extra_fields = {'field2': TextField('field2',
    #                            widget=BS3TextFieldROWidget())}
    validators_columns = {'my_field1':[EqualTo('my_field2',
                                        message=gettext('fields must match'))
                                      ]
    }

    # show_fieldsets, add_fieldsets, edit_fieldsets to customize show, add and edit views
    show_fieldsets = [
        ('Summary',{'fields':['name','address','contact_group']}),
        ('Personal Info',{'fields':['birthday','personal_phone','personal_celphone'],'expanded':False}),
        ]

	# use search_columns to control which columns are searchable
	# use list_widget to control the view

def get_user():
    return g.user

class GroupModelView(ModelView):
    base_permissions = ['can_add', 'can_delete', 'can_list', 'can_show']  # can_edit
    base_filters = [#['created_by', FilterEqualFunction, get_user],
                    ['name', FilterStartsWith, 'F']]
    list_columns = ['name', 'my_name']

    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]  # create a master/detail view on the show and edit

	# action will be shown in both list & show: can be used to implement request approval / rejection
    @action("myaction","Do something on this record","Do you really want to?","fa-rocket")
    def myaction(self, item):
        """
            do something with the item record
        """
        # return list on list view, object on show view
        #if isinstance(items, list):
        #    self.datamodel.delete_all(items)
        #    self.update_redirect()
        #else:
        #    self.datamodel.delete(items)
        return redirect(self.get_redirect())

    # action will be shown in list only
    @action("muldelete", "Delete", "Delete all Really?", "fa-rocket", single=False)
    def muldelete(self, items):
        self.datamodel.delete_all(items)
        self.update_redirect()
        return redirect(self.get_redirect())

class MultipleViewsExp(MultipleView):
    views = [GroupModelView, ContactModelView]

class GroupMasterView(MasterDetailView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]

db.create_all()
# more icon names: http://fontawesome.io/icons/
appbuilder.add_view(GroupModelView, "List Groups",icon = "fa-folder-open-o",category = "Contacts",
                category_icon = "fa-envelope")
appbuilder.add_view(ContactModelView, "List Contacts",icon = "fa-envelope",category = "Contacts")
appbuilder.add_view(MultipleViewsExp, "Multiple Views", icon="fa-envelope", category="Contacts")
appbuilder.add_view(GroupMasterView, "Master Detail Views", icon="fa-envelope", category="Contacts")

class EmployeeHistoryView(ModelView):
    datamodel = SQLAInterface(EmployeeHistory)
    list_columns = ['department', 'begin_date', 'end_date']

def department_query():
    return db.session.query(Department)

class EmployeeView(ModelView):
    datamodel = SQLAInterface(Employee)

    list_columns = ['full_name', 'department', 'employee_number']
	# TODO there is a bug: the change of history doens't update employee's department
    edit_form_extra_fields = {'department':  QuerySelectField('Department',
                                query_factory=department_query,
                                widget=Select2Widget(extra_classes="readonly"))}

    related_views = [EmployeeHistoryView]
    show_template = 'appbuilder/general/model/show_cascade.html' # not a tab, but on the same page cascading

class FunctionView(ModelView):
    datamodel = SQLAInterface(Function)
    related_views = [EmployeeView]

class DepartmentView(ModelView):
    datamodel = SQLAInterface(Department)
    related_views = [EmployeeView]

class BenefitView(ModelView):
    datamodel = SQLAInterface(Benefit)
    related_views = [EmployeeView]
    add_columns = ['name']
    edit_columns = ['name']
    show_columns = ['name']
    list_columns = ['name']

appbuilder.add_view(EmployeeView, "Employees", icon="fa-folder-open-o", category="Company")
appbuilder.add_separator("Company")
appbuilder.add_view(DepartmentView, "Departments", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(FunctionView, "Functions", icon="fa-folder-open-o", category="Company")
appbuilder.add_view(BenefitView, "Benefits", icon="fa-folder-open-o", category="Company")
appbuilder.add_view_no_menu(EmployeeHistoryView, "EmployeeHistoryView")

"""
	Chart Views
"""
class CountryDirectChartView(DirectByChartView):
    datamodel = SQLAInterface(CountryStats)
    chart_title = 'Direct Data Example'

    definitions = [
    {
        'label': 'Unemployment',
        'group': 'stat_date',
        'series': ['unemployed_perc',
                   'college_perc']
    }
]

appbuilder.add_view(CountryDirectChartView, "Show Country Chart", icon="fa-dashboard", category="Statistics")
# TODO explore more

"""
    Application wide 404 error handler
"""
@appbuilder.app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', base_template=appbuilder.base_template, appbuilder=appbuilder), 404



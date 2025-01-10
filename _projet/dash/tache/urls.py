from django.urls import path
from .views import ResponsiblesListView, ResponsibleDetailView, ResponsibleAddView, ResponsibleUpdateView, ResponsibleDeleteView, EntitiesListView, EntityDetailView, EntityAddView, EntityUpdateView, EntityDeleteView
from .views import AxesListView, AxeDetailView, AxeAddView, AxeUpdateView, AxeDeleteView
from .views import ProjectsListView, ProjectDetailView, ProjectAddView, ProjectUpdateView, ProjectDeleteView
from .views import ComponentsListView, ComponentDetailView, ComponentAddView, ComponentUpdateView, ComponentDeleteView
from .views import ResultsListView, ResultDetailView, ResultAddView, ResultUpdateView, ResultDeleteView
from .views import ProductsListView, ProductDetailView, ProductAddView, ProductUpdateView, ProductDeleteView
from .views import ActivitiesListView, ActivityDetailView, ActivityAddView, ActivityUpdateView, ActivityDeleteView
from .views import TasksListView, TaskDetailView, TaskAddView, TaskUpdateView, TaskDeleteView
from .views import ProgressionsListView, ProgressionDetailView, ProgressionAddView, ProgressionUpdateView, ProgressionDeleteView
from .views import PhonenumbersListView, PhonenumberDetailView, PhonenumberAddView, PhonenumberUpdateView, PhonenumberDeleteView
from .views import AoiListView, WorldView, AoipopupListView
from . import views



app_name = 'tache'

urlpatterns = [
    path('', views.home, name='home'),
    path('Chart', views.chartJ, name='Chart-views'),
    path('schedulemail/', views.schedul_mail, name='schedulemail'),
    path('welcome',views.welcome,name='welcome'),
    

# ______________________ Responsibles ________________________________________________
    path('responsibles', ResponsiblesListView.as_view(), name='responsibles-list'),
    path('responsible/<int:pk>', ResponsibleDetailView.as_view(), name='responsible-detail'),
    path('responsible_add', ResponsibleAddView.as_view(), name='responsible-add'),
    path('responsible/update/<int:pk>', ResponsibleUpdateView.as_view(), name='responsible-update'),
    path('responsible/delete/<int:pk>', ResponsibleDeleteView.as_view(), name='responsible-delete'),

# ______________________ Entities ________________________________________________
    path('entities', EntitiesListView.as_view(), name='entities-list'),
    path('entity/<int:pk>', EntityDetailView.as_view(), name='entity-detail'),
    path('entity_add', EntityAddView.as_view(), name='entity-add'),
    path('entity/update/<int:pk>', EntityUpdateView.as_view(), name='entity-update'),
    path('entity/delete/<int:pk>', EntityDeleteView.as_view(), name='entity-delete'),

# ______________________ Axes ________________________________________________
    path('axes', AxesListView.as_view(), name='axes-list'),
    path('axe/<int:pk>', AxeDetailView.as_view(), name='axe-detail'),
    path('axe_add', AxeAddView.as_view(), name='axe-add'),
    path('axe/update/<int:pk>', AxeUpdateView.as_view(), name='axe-update'),
    path('axe/delete/<int:pk>', AxeDeleteView.as_view(), name='axe-delete'),

# ______________________ Projects ________________________________________________
    path('projects', ProjectsListView.as_view(), name='projects-list'),
    path('project/<int:pk>', ProjectDetailView.as_view(), name='project-detail'),
    path('axe/<int:axe_id>/project_add', ProjectAddView.as_view(), name='project-add'),
    path('axe/<int:axe_id>/project/update/<int:pk>', ProjectUpdateView.as_view(), name='project-update'),
    path('axe/<int:axe_id>/project/delete/<int:pk>', ProjectDeleteView.as_view(), name='project-delete'),

# ______________________ Components ________________________________________________
    path('components', ComponentsListView.as_view(), name='components-list'),
    path('component/<int:pk>', ComponentDetailView.as_view(), name='component-detail'),

    path('project/<int:project_id>/component_add', ComponentAddView.as_view(), name='component-add'),

    path('project/<int:project_id>/component/<int:pk>/update', ComponentUpdateView.as_view(), name='component-update'),
    path('project/<int:project_id>/component/<int:pk>/delete', ComponentDeleteView.as_view(), name='component-delete'),

# ______________________ Results ________________________________________________
    path('results', ResultsListView.as_view(), name='results-list'),
    path('result/<int:pk>', ResultDetailView.as_view(), name='result-detail'),

    path('component/<int:component_id>/result_add', ResultAddView.as_view(), name='result-add'),
    
    path('component/<int:component_id>/result/<int:pk>/update', ResultUpdateView.as_view(), name='result-update'),
    path('component/<int:component_id>/result/<int:pk>/delete', ResultDeleteView.as_view(), name='result-delete'),

# ______________________ Products ________________________________________________
    path('products', ProductsListView.as_view(), name='products-list'),
    path('product/<int:pk>', ProductDetailView.as_view(), name='product-detail'),

    path('result/<int:result_id>/product_add', ProductAddView.as_view(), name='product-add'),

    path('result/<int:result_id>product/<int:pk>/update', ProductUpdateView.as_view(), name='product-update'),
    path('result/<int:result_id>product/<int:pk>/delete', ProductDeleteView.as_view(), name='product-delete'),

# ______________________ Activities ________________________________________________
    path('activities', ActivitiesListView.as_view(), name='activities-list'),
    path('activity/<int:pk>', ActivityDetailView.as_view(), name='activity-detail'),

    path('product/<int:product_id>/activity_add', ActivityAddView.as_view(), name='activity-add'),

    path('product/<int:product_id>/activity/<int:pk>/update', ActivityUpdateView.as_view(), name='activity-update'),
    path('product/<int:product_id>/activity/<int:pk>/delete', ActivityDeleteView.as_view(), name='activity-delete'),

# ______________________ Tasks ________________________________________________
    path('tasks', TasksListView.as_view(), name='tasks-list'),
    path('task/<int:pk>', TaskDetailView.as_view(), name='task-detail'),

    path('activity/<int:activity_id>/task_add', TaskAddView.as_view(), name='task-add'),

    path('activity/<int:activity_id>/task/<int:pk>/update', TaskUpdateView.as_view(), name='task-update'),
    path('activity/<int:activity_id>/task/<int:pk>/delete', TaskDeleteView.as_view(), name='task-delete'),

# ______________________ Progressions _______________________________________________
    path('progressions', ProgressionsListView.as_view(), name='progressions-list'),
    path('progression/<int:pk>', ProgressionDetailView.as_view(), name='progression-detail'),

    path('task/<int:task_id>/progression_add', ProgressionAddView.as_view() ,name='progression-add'),
    path('task/<int:task_id>/progression/<int:pk>/update', ProgressionUpdateView.as_view(), name='progression-update'),
    path('task/<int:task_id>/progression/<int:pk>/delete', ProgressionDeleteView.as_view(), name='progression-delete'),

# ______________________ Phonenumber ________________________________________________
    path('phone_numbers', PhonenumbersListView.as_view(), name='phone_numbers-list'),
    path('phone_number/<int:pk>', PhonenumberDetailView.as_view(), name='phone_number-detail'),
    path('phone_number_add', PhonenumberAddView.as_view(), name='phone_number-add'),
    path('phone_number/update/<int:pk>', PhonenumberUpdateView.as_view(), name='phone_number-update'),
    path('phone_number/delete/<int:pk>', PhonenumberDeleteView.as_view(), name='phone_number-delete'),

# ______________________ Geometry ________________________________________________
    path('aois', AoiListView.as_view(), name='aoi-list'),
    path('aoispopup', AoipopupListView.as_view(), name='aoispopup-list'),
    path('world', WorldView.as_view(), name='world'),
    ]


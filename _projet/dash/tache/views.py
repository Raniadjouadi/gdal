from html import entities
from inspect import BoundArguments
from multiprocessing import context
from operator import is_not
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.views import generic
from django.views.generic import CreateView
from django.urls import reverse_lazy
# from requests import request
from django.contrib.auth import authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime
from django.core.mail import send_mail
from .tasks import send_mail_fonction
from django_celery_beat.models import PeriodicTask, CrontabSchedule

# from requests import request

from tache.models import Aoi, Responsibles, Entities, Axes, Projects, Components, Results, Products, Activities, Phone_numbers
from tache.models import Tasks, Progressions, ProjectEntities, ActivitiesEntitiesBudget, Phases
from tache.models import PopulatedPlaces, Notification
from django.contrib.auth.models import User

from .forms import ProgressionForm, TaskForm, ActivityForm, ProductForm, ResultForm, ComponentForm, ProjectForm

from django.db import connection
from django.core.serializers import serialize
from collections import namedtuple
from django.db.models import FilteredRelation, Q
from django.db.models import Prefetch


def welcome(request):
    return render (request, 'welcome')

def schedul_mail(request):
    schedule, create = CrontabSchedule.objects.get_or_create(hour = 19, minute = 0 )
    task = PeriodicTask.objects.create(crontab=schedule, name="schedule_mail_task_"+"1",task='tache.tasks.send_mail_fonction')
    return HttpResponse("Done")
global curant_username
global curant_entitie
global budget_project


# calcul du budget total de l'ensemble des axes ****
def axesBudgetOss():
    axes= Axes.objects.all()
    budget_axes_total = 0
    if axes :
        for axe in axes:
            axe_id= axe.id
            budgetAxe = axeBudgetOss(axe_id)
            budget_axes_total = budget_axes_total + budgetAxe
    else:
        budget_axes_total = budget_axes_total
    return(budget_axes_total)

# calcul du budget de l'ensemble des axes par entité ****
def axesBudget(entite_id):
    axes= Axes.objects.all()
    budget_axes = 0
    if axes :
        budget_axes_total = 0
        for axe in axes:
            axe_id= axe.id
            budgetAxe = axeBudget(axe_id, entite_id)
            budget_axes = budget_axes + budgetAxe[0]
            budget_axes_total = budget_axes_total + budgetAxe[1]
    else:
        budget_axes = budget_axes
        budget_axes_total = budget_axes_total
    return(budget_axes, budget_axes_total)
# calcul du budget total par axe ****
def axeBudgetOss(axe_id):
    projets = Projects.objects.filter(axe_id=axe_id)
    budget_axe_total = 0
    if projets:
        for projet in projets:
            budgetproet = projet.budget
            budget_axe_total = budget_axe_total + budgetproet
    else:
        budget_axe_total = budget_axe_total

    return(budget_axe_total)

# calcul du budget de l'axe par entité ****
def axeBudget(axe_id, entite_id):
    projets = Projects.objects.filter(axe_id=axe_id)
    budget_axe = 0
    if projets:
        budget_axe_total = 0
        for projet in projets:
            projet_id = projet.id
            projectentities= ProjectEntities.objects.filter(project_id = projet_id, entity_id= entite_id)
            if projectentities:
                for projectentitie in projectentities:
                    projectentitie_id = projectentitie.id
                    budgetproet = projectBudget(projet_id, entite_id)
                    budget_axe = budget_axe + budgetproet
                    budget_axe_total = budget_axe_total + projet.budget
            else:
                budget_axe = budget_axe
                budget_axe_total = budget_axe_total

    else:
        budget_axe = 0
        budget_axe_total = 0

    return(budget_axe, budget_axe_total)
# calcul du budget par projet par entité ****
def projectBudget(project_id, Entite_id):
    budget_project = 0
    projectEntites= ProjectEntities.objects.filter(project_id=project_id, entity_id=Entite_id )
    if  projectEntites:
        for projectEntite in projectEntites:
            projectEntite_id = projectEntite.id
            activ_enti_budgs =ActivitiesEntitiesBudget.objects.filter(project_entity_id=projectEntite_id)
        
            if activ_enti_budgs:
                for activ_enti_budg in activ_enti_budgs:
                    budget_project = budget_project + activ_enti_budg.Budget
            else:
                budget_project = budget_project
    else:
        budget_project = 0
                
    return(budget_project)


# calcul du budget total du projet ****
def projectBudgetOss(project_id):
    projectEnties= ProjectEntities.objects.filter(project_id=project_id)
    budget_project = 0
    if projectEnties:
        
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            activ_enti_budgs =ActivitiesEntitiesBudget.objects.filter(project_entity_id=projectentitie_id)           
            if activ_enti_budgs:
                for activ_enti_budg in activ_enti_budgs:
                    budget_project = budget_project + activ_enti_budg.Budget
            else:
                budget_project = budget_project
    else:
        budget_project = budget_project       
    return(budget_project)

# calcul du budget du projet pour chaque entité (OSS) ****
def projectBudgetOss_entites(project_id):
    projectEnties= ProjectEntities.objects.filter(project_id=project_id)
    l=()
    l2=(('',0,0,0,0,0),)    
    if projectEnties:
        i=0            
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            role= projectEntie.name # àparametrer implementation (OSS)
            if role != 'OSS':

                entite_id = projectEntie.entity_id
                entite_Noms = Entities.objects.filter(id=entite_id)
                if entite_Noms:
                    for entite_Nom in entite_Noms:
                        nom_Entite = entite_Nom.acronym
                else:
                    nom_Entite = ''
                entite = nom_Entite + ' '+ role
                activ_enti_budgs =ActivitiesEntitiesBudget.objects.filter(project_entity_id=projectentitie_id)
                budget_project = 0           
                if activ_enti_budgs:
                    for activ_enti_budg in activ_enti_budgs:
                        budget_project = budget_project + activ_enti_budg.Budget
                else:
                        budget_project = budget_project
                data = Components.objects.raw("SELECT tache_components.id, tache_components.component, tache_components.budget FROM tache_components WHERE (tache_components.project_id =" +str(project_id) + ")")
                #initialisation des budgets
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0
                if data :
                    for component in data:
                        Components_id = component.id
                        
                        budgets =budget_Compoment(Components_id, projectentitie_id)
                        budget_reserve = budget_reserve + budgets[0]
                        budget_engage = budget_engage + budgets[1]
                        budget_consome = budget_consome + budgets[2]
                        budget_restant = budget_restant + budgets[3]
                        l1 = ((entite,budget_project,budget_reserve,budget_engage,budget_consome,budget_restant),)
                        #print(l)
                else:
                    budget_reserve = 0
                    budget_engage = 0
                    budget_consome = 0
                    budget_restant = 0
                    l1 = ((entite,budget_project,budget_reserve,budget_engage,budget_consome,budget_restant),)
            
                l = l + l1 
                l2=(('Total',l2[0][1]+l1[0][1],l2[0][2]+l1[0][2],l2[0][3]+l1[0][3],l2[0][4]+l1[0][4],l2[0][5]+l1[0][5]),)
        l=l+l2    
    else:
        l=l+l2         
    return(l)
# calcul du budget par composante (OSS)
def compoment_BudgetOss(Components_id):
    Budget_compoment= 0
    results = Results.objects.filter(component_id=Components_id)
    if results:
        for result in results:
            result_id = result.id 
            products = Products.objects.filter(result_id=result_id)
            if products:
                for product in products:
                    product_id = product.id   
                    activities = Activities.objects.filter(product_id=product_id)
                    if activities:
                        for activitie in activities:
                            activitie_id = activitie.id
                            activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activitie_id)
                            if activentitiesBudgets:
                                for activentitiesBudget in activentitiesBudgets:
                                    Budget_compoment = Budget_compoment + activentitiesBudget.Budget
                            else:
                                Budget_compoment = Budget_compoment
                    else:
                        Budget_compoment = Budget_compoment
            else:
                Budget_compoment = Budget_compoment                    
    else:
        Budget_compoment = 0    
    return(Budget_compoment)



# calcul du budget de la composante pour chaque entité (OSS)
def CompomentBudgetOss_entites(Components_id, project_id):

    projectEnties= ProjectEntities.objects.filter(project_id=project_id)    
    if projectEnties:
        l=()
        l2=(('',0,0,0,0,0),)
        i=0            
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            role= projectEntie.name
            if role != 'OSS':

                entite_id = projectEntie.entity_id
                entite_Noms = Entities.objects.filter(id=entite_id)
                if entite_Noms:
                    for entite_Nom in entite_Noms:
                        nom_Entite = entite_Nom.acronym
                else:
                    nom_Entite = ''
                entite = nom_Entite + ' '+ role
                compomentBudget = compoment_Budget(Components_id, projectentitie_id)

                data = Results.objects.raw("SELECT tache_results.id, tache_results.result, tache_results.budget FROM tache_results WHERE (tache_results.component_id =" +str(Components_id) + ")")
                #initialisation des budgets
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0
                if data :
                    for result in data:
                        Result_id = result.id
                        
                        budgets =budget_Result(Result_id, projectentitie_id)
                        budget_reserve = budget_reserve + budgets[0]
                        budget_engage = budget_engage + budgets[1]
                        budget_consome = budget_consome + budgets[2]
                        budget_restant = budget_restant + budgets[3]
                        l1 = ((entite,compomentBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)
                else:
                    budget_reserve = 0
                    budget_engage = 0
                    budget_consome = 0
                    budget_restant = 0
                    l1 = ((entite,compomentBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)

                
            
                l = l + l1 
                l2=(('Total',l2[0][1]+l1[0][1],l2[0][2]+l1[0][2],l2[0][3]+l1[0][3],l2[0][4]+l1[0][4],l2[0][5]+l1[0][5]),)
    l=l+l2    
            
    return(l)
# calcul du budget de la composante pour chaque entité (OSS)
def compoment_Budget(Components_id, projectentitie_id):
    Budget_compoment= 0
    results = Results.objects.filter(component_id=Components_id)
    if results:
        for result in results:
            result_id = result.id 
            Budget_compoment = Budget_compoment + resultBudget(result_id, projectentitie_id)                  
    else:
        Budget_compoment = Budget_compoment
    return(Budget_compoment)

# calcul du budget du Result par entite
def resultBudgetOss(Result_id):
    Budget_result= 0
    products = Products.objects.filter(result_id=Result_id)
    if products:
        for product in products:
            product_id = product.id     
            activities = Activities.objects.filter(product_id=product_id)
            if activities:
                for activitie in activities:
                    activitie_id = activitie.id
                    activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activitie_id)
                    if activentitiesBudgets:
                        for activentitiesBudget in activentitiesBudgets:
                            Budget_result = Budget_result + activentitiesBudget.Budget
                    else:
                        Budget_result = Budget_result
            else:
                Budget_result = Budget_result
    else:
        Budget_result = Budget_result
    return(Budget_result)

def ResultBudgetOss_entites(Result_id, project_id):

    projectEnties= ProjectEntities.objects.filter(project_id=project_id)    
    if projectEnties:
        l=()
        l2=(('',0,0,0,0,0),)
        i=0            
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            role= projectEntie.name
            if role != 'OSS':

                entite_id = projectEntie.entity_id
                entite_Nom = Entities.objects.get(id=entite_id)
                if entite_Nom:
                    #for entite_Nom in entite_Noms:
                    nom_Entite = entite_Nom.acronym
                else:
                    nom_Entite = ''
                entite = nom_Entite + ' '+ role
                ResultBudget = resultBudget(Result_id, projectentitie_id)

                data = Products.objects.raw("SELECT tache_products.id, tache_products.product, tache_products.budget FROM tache_products WHERE (tache_products.result_id =" +str(Result_id) + ")")
                #initialisation des budgets
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0
                if data :
                    for product in data:
                        product_id = product.id
                        
                        budgets =budget_Prodact(product_id, projectentitie_id)
                        budget_reserve = budget_reserve + budgets[0]
                        budget_engage = budget_engage + budgets[1]
                        budget_consome = budget_consome + budgets[2]
                        budget_restant = budget_restant + budgets[3]
                        l1 = ((entite,ResultBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)
                else:
                    budget_reserve = 0
                    budget_engage = 0
                    budget_consome = 0
                    budget_restant = 0
                    l1 = ((entite,ResultBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)            
                l = l + l1 
                l2=(('Total',l2[0][1]+l1[0][1],l2[0][2]+l1[0][2],l2[0][3]+l1[0][3],l2[0][4]+l1[0][4],l2[0][5]+l1[0][5]),)
    l=l+l2    

            
    return(l)

def resultBudget(Result_id, projectentitie_id):
    Budget_result= 0
    products = Products.objects.filter(result_id=Result_id)
    if products:
        for product in products:
            product_id = product.id 
            Budget_result =  Budget_result + prodactBudget(product_id, projectentitie_id) 
    else:
        Budget_result = 0
    return(Budget_result)

# calcul du budget du prodact
def prodactBudgetOss(product_id):   
    activities = Activities.objects.filter(product_id=product_id)
    Budget_product= 0
    if activities:
        for activitie in activities:
            activitie_id = activitie.id
            activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activitie_id)
            if activentitiesBudgets:
                for activentitiesBudget in activentitiesBudgets:
                    Budget_product = Budget_product + activentitiesBudget.Budget
            else:
                Budget_product = Budget_product
    else:
        Budget_product = Budget_product
    return(Budget_product)

def ProdactBudgetOss_entites(product_id, project_id):

    projectEnties= ProjectEntities.objects.filter(project_id=project_id)
    l=()    
    if projectEnties:
        l=()
        l2=(('',0,0,0,0,0),)
        i=0            
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            role= projectEntie.name
            if role != 'OSS':

                entite_id = projectEntie.entity_id
                entite_Noms = Entities.objects.filter(id=entite_id)
                if entite_Noms:
                    for entite_Nom in entite_Noms:
                        nom_Entite = entite_Nom.acronym
                else:
                    nom_Entite = ''
                entite = nom_Entite + ' '+ role
                ProdactBudget = prodactBudget(product_id, projectentitie_id)

                data = Activities.objects.raw("SELECT tache_activities.id, tache_activities.activity, tache_activities.budget FROM tache_activities INNER JOIN tache_activitiesEntitiesBudget ON (tache_activities.id = tache_activitiesEntitiesBudget.activity_id) WHERE (tache_activities.product_id=" +str(product_id) +" and tache_activitiesEntitiesBudget.project_entity_id =" + str(projectentitie_id) + ")")
                #initialisation des budgets
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0
                if data :
                    for activite in data:
                        activite_id = activite.id
                        Budget_activite = activeteentite_sBudgets(activite_id, projectentitie_id)
                        
                        budgets =activiteBedgetReserveEngage(activite_id, projectentitie_id, Budget_activite)
                        budget_reserve = budget_reserve + budgets[0]
                        budget_engage = budget_engage + budgets[1]
                        budget_consome = budget_consome + budgets[2]
                        budget_restant = budget_restant + budgets[3]
                        l1 = ((entite,ProdactBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)
                else:
                    budget_reserve = 0
                    budget_engage = 0
                    budget_consome = 0
                    budget_restant = 0
                    l1 = ((entite,ProdactBudget,budget_reserve,budget_engage,budget_consome,budget_restant),)
      
                l = l + l1 
                l2=(('Total',l2[0][1]+l1[0][1],l2[0][2]+l1[0][2],l2[0][3]+l1[0][3],l2[0][4]+l1[0][4],l2[0][5]+l1[0][5]),)
    l=l+l2    

            
    return(l)

def ActivitesBudgetOss_entites(activite_id, project_id):

    projectEnties= ProjectEntities.objects.filter(project_id=project_id)
    l=()    
    if projectEnties:
        l2=(('',0,0,0,0,0),)
        i=0            
        for projectEntie in projectEnties:
            projectentitie_id = projectEntie.id
            role= projectEntie.name
            if role != 'OSS':
                entite_id = projectEntie.entity_id
                entite_Nom = Entities.objects.get(id=entite_id)
                if entite_Nom:
                    nom_Entite = entite_Nom.acronym
                else:
                    nom_Entite = ''
                entite = nom_Entite + ' '+ role
                #Budget_activite = activeteentite_sBudgets(activite_id, projectentitie_id)
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0

                Budget_activite = activeteentite_sBudgets(activite_id, projectentitie_id)                      
                budgets =activiteBedgetReserveEngage(activite_id, projectentitie_id, Budget_activite)
                budget_reserve = budget_reserve + budgets[0]
                budget_engage = budget_engage + budgets[1]
                budget_consome = budget_consome + budgets[2]
                budget_restant = budget_restant + budgets[3]
                l1 = ((entite,Budget_activite,budget_reserve,budget_engage,budget_consome,budget_restant),)     
                l = l + l1 
                l2=(('Total',l2[0][1]+l1[0][1],l2[0][2]+l1[0][2],l2[0][3]+l1[0][3],l2[0][4]+l1[0][4],l2[0][5]+l1[0][5]),)
                
    l=l+l2            
    return(l)

def prodactBudget(product_id, projectentitie_id):   
    activities = Activities.objects.filter(product_id=product_id)
    Budget_product= 0
    if activities:
        for activitie in activities:
            activitie_id = activitie.id
            activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activitie_id, project_entity_id = projectentitie_id)
            if activentitiesBudgets:
                for activentitiesBudget in activentitiesBudgets:
                    Budget_product = Budget_product + activentitiesBudget.Budget
            else:
                Budget_product = Budget_product
    else:
        Budget_product = Budget_product
    return(Budget_product)

def projectEntiteAccronima(curant_username):
    # Recuperation du username de l'utilisateur et de son id
    if  curant_username :
        curant_users = User.objects.filter(username=curant_username)
        for user in curant_users:
            curant_usernam_id = user.id  
    # relier l'utilisateur avec le responsable
        responsables = Responsibles.objects.filter(user_id=curant_usernam_id)
        if responsables:
            for responsable in responsables:
                curant_entitie_id = responsable.entity_id
                projectentite_id = responsable.project_entity_id
                idresponsable1= responsable.id
            # recuperation de l'entite auquelle appartien le responsable
            enteties= Entities.objects.filter(id=curant_entitie_id)
            if enteties:
                for entitie in enteties:
                    entiteAcronin = entitie.acronym
                    entite_id = entitie.id
                return (entiteAcronin, entite_id, projectentite_id, idresponsable1)
    else:
        return None
def activitiesproduct_id(activite_id):
    # recuperation de id product auquelle appartien l'activité en question
    activitie = Activities.objects.get(id=activite_id)
    product_id = activitie.product_id

    return(product_id)

def productsResult_id(product_id):
    # recuperation de id Result auquelle appartien le Prodact en question
    product = Products.objects.get(id=product_id)
    Result_id = product.result_id
    return(Result_id)

def resultsComponents_id(Result_id):
    # recuperation de id composante auquelle appartien le Result en question
    result = Results.objects.get(id=Result_id)
    Components_id = result.component_id
    return(Components_id)
def componentsProjects_id(Components_id):
    # recuperation de id Project auquelle appartien la Composante en question
    component = Components.objects.get(id=Components_id )
    project_id = component.project_id
    return(project_id)
def projectEntities(projectentitie_id):
    # recuperation de id projectEntitie auquelle appartien l'entité et le projet en question
    projectEntitie = ProjectEntities.objects.get(id = projectentitie_id)
    if projectEntitie:
        projectentitie_name = projectEntitie.name
    else:
        projectentitie_name = None
    return( projectentitie_name )

    # budgetActivite
def activeteentite_sBudgetsOss(activite_id):
    activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activite_id)
    Budget_activite = 0
    if activentitiesBudgets :
        for activentitiesBudget in activentitiesBudgets:
            Budget_activite = Budget_activite + activentitiesBudget.Budget
    else:
            Budget_activite = Budget_activite   
    return(Budget_activite)

def activeteentite_sBudgets(activite_id, projectentitie_id):
    Budget_activite =0 
    activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activite_id, project_entity_id = projectentitie_id)
    if activentitiesBudgets :

        for activentitiesBudget in activentitiesBudgets:
            Budget_activite = activentitiesBudget.Budget
    else:
            Budget_activite =  Budget_activite   
    return(Budget_activite)
# calcul des budgets reservé, engagé, consommé et restant pour tous les Axes ****
def budget_AxesOss():
    data = Axes.objects.all()
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data:
        for axe in data:
            Axe_id = axe.id
            budgets = budget_AxeOss(Axe_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0

    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)
# calcul des budgets reservé, engagé, consommé et restant par Axe et par entité ****
def budget_Axes(entite_id):
    data = Axes.objects.all()
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data:
        for axe in data:
            Axe_id = axe.id
            budgets = budget_Axe(Axe_id, entite_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0

    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)
# calcul des budgets reservé, engagé, consommé et restant par Axe ****
def budget_AxeOss(Axe_id):
    data = Projects.objects.raw("SELECT tache_projects.id, tache_projects.acronym, tache_projects.budget FROM tache_projects WHERE (tache_projects.axe_id =" +str(Axe_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for project in data:
            Project_id = project.id                   
            budgets =projectBudgetOss_entites(Project_id)
            if budgets:
                for budget in budgets:
                    if budget[0] != "Total":
                        budget_reserve = budget_reserve + budget[2]
                        budget_engage = budget_engage + budget[3]
                        budget_consome = budget_consome + budget[4]
                        budget_restant = budget_restant + budget[5]
                    else :
                        budget_reserve = budget_reserve
                        budget_engage = budget_engage
                        budget_consome = budget_consome
                        budget_restant = budget_restant
            else:
                budget_reserve = 0
                budget_engage = 0
                budget_consome = 0
                budget_restant = 0

    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# calcul des budgets reservé, engagé, consommé et restant par Axe  et par entité ****
def budget_Axe(Axe_id, entite_id):
    data = Projects.objects.raw("SELECT tache_projects.id, tache_projects.acronym, tache_projects.budget FROM tache_projects WHERE (tache_projects.axe_id =" +str(Axe_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :

        for project in data:
            Project_id = project.id
            projectentities= ProjectEntities.objects.filter(project_id = Project_id, entity_id= entite_id)
            if projectentities:
                for projectentitie in projectentities:
                    projectentitie_id = projectentitie.id            
                    budgets =budget_Project(Project_id, projectentitie_id)
                    budget_reserve = budget_reserve + budgets[0]
                    budget_engage = budget_engage + budgets[1]
                    budget_consome = budget_consome + budgets[2]
                    budget_restant = budget_restant + budgets[3]
            else:
                    budget_reserve = budget_reserve
                    budget_engage = budget_engage
                    budget_consome = budget_consome
                    budget_restant = budget_restant
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# calcul des budgets reserve, engage, consome et restant par Projet
def budget_ProjectOss(Project_id):
    data = Components.objects.raw("SELECT tache_components.id, tache_components.component, tache_components.budget FROM tache_components WHERE (tache_components.project_id =" +str(Project_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :

        for component in data:
            Components_id = component.id
             
            budgets =budget_CompomentOss(Components_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]

    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

def budget_Project(Project_id, projectentitie_id):
    data = Components.objects.raw("SELECT tache_components.id, tache_components.component, tache_components.budget FROM tache_components WHERE (tache_components.project_id =" +str(Project_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for component in data:
            Components_id = component.id
             
            budgets =budget_Compoment(Components_id, projectentitie_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# calcul des budgets reserve, engage, consome et restant par Composante

def budget_CompomentOss(Components_id):
    data = Results.objects.raw("SELECT tache_results.id, tache_results.result, tache_results.budget FROM tache_results WHERE (tache_results.component_id =" +str(Components_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for result in data:
            Result_id = result.id
             
            budgets =budget_ResultOss(Result_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]

    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

def budget_Compoment(Components_id, projectentitie_id):
    data = Results.objects.raw("SELECT tache_results.id, tache_results.result, tache_results.budget FROM tache_results WHERE (tache_results.component_id =" +str(Components_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for result in data:
            Result_id = result.id
             
            budgets =budget_Result(Result_id, projectentitie_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)
# calcul des budgets reserve, engage, consome et restant par Result
def budget_ResultOss(Result_id):
    data = Products.objects.raw("SELECT tache_products.id, tache_products.product, tache_products.budget FROM tache_products WHERE (tache_products.result_id =" +str(Result_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for product in data:
            product_id = product.id
             
            budgets =budget_ProdactOss(product_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]

    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

def budget_Result(Result_id, projectentitie_id):
    data = Products.objects.raw("SELECT tache_products.id, tache_products.product, tache_products.budget FROM tache_products WHERE (tache_products.result_id =" +str(Result_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for product in data:
            product_id = product.id
             
            budgets =budget_Prodact(product_id, projectentitie_id)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# calcul des budgets reserve, engage, consome et restant par Product

def budget_ProdactOss(product_id):
    data = Activities.objects.raw("SELECT tache_activities.id, tache_activities.activity, tache_activities.budget FROM tache_activities INNER JOIN tache_activitiesEntitiesBudget ON (tache_activities.id = tache_activitiesEntitiesBudget.activity_id) WHERE (tache_activities.product_id=" +str(product_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for activite in data:
            activite_id = activite.id
            Budget_activite = activeteentite_sBudgetsOss(activite_id)
             
            budgets =activiteBedgetReserveEngageOss(activite_id, Budget_activite)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

def budget_Prodact(product_id, projectentitie_id):
    data = Activities.objects.raw("SELECT tache_activities.id, tache_activities.activity, tache_activities.budget FROM tache_activities INNER JOIN tache_activitiesEntitiesBudget ON (tache_activities.id = tache_activitiesEntitiesBudget.activity_id) WHERE (tache_activities.product_id=" +str(product_id) +" and tache_activitiesEntitiesBudget.project_entity_id =" + str(projectentitie_id) + ")")
    #initialisation des budgets
    budget_reserve = 0
    budget_engage = 0
    budget_consome = 0
    budget_restant = 0
    if data :
        for activite in data:
            activite_id = activite.id
            Budget_activite = activeteentite_sBudgets(activite_id, projectentitie_id)
             
            budgets =activiteBedgetReserveEngage(activite_id, projectentitie_id, Budget_activite)
            budget_reserve = budget_reserve + budgets[0]
            budget_engage = budget_engage + budgets[1]
            budget_consome = budget_consome + budgets[2]
            budget_restant = budget_restant + budgets[3]
    else:
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0
        budget_restant = 0
    return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# calcul des budgets reserve, engage, consome et restant par activité
def activiteBedgetReserveEngageOss(activite_id, Budget_activite):
        # Recuperation des taches de l'activité en question
        data= Tasks.objects.raw("SELECT tache_tasks.id, tache_tasks.task, tache_tasks.budget FROM tache_tasks WHERE (tache_tasks.activity_id =" + str(activite_id) + ")")
        
        if data :
            budget_reserve = 0
            budget_engage = 0
            budget_consome = 0
            budget_restant = Budget_activite
            for task in data:
                task_budget = task.budget
                task_id = task.id
                phase =''
                # Recupération des progressions de chaque tache verification du niveau de progression de la tache
                progression = Progressions.objects.raw("SELECT tache_progressions.phase_id, tache_progressions.id FROM tache_progressions INNER JOIN tache_phases ON (tache_progressions.phase_id = tache_phases.id) WHERE (tache_progressions.task_id =" + str(task_id) +")")
                if progression :
                    for prog in progression:
                        phase_id = prog.phase_id
                        phass = Phases.objects.get(id=phase_id)            
                        progres_phase = phass.phase
                        if progres_phase in ("To do","Proposals examination", "Tender", "Tor drafting") and phase not in("engage", "consome"):
                            phase = 'reserve'
                        elif progres_phase in ("Validation","Report", "Progress rate (%)", "contract signature") and  phase !="consome":
                            phase = 'engage'
                        elif progres_phase in  ('Payement', 'Done'):
                            phase = 'consome'
                    # Calcul des budget reservés, engagés, consomés et restants pour l'activité en question selon le niveau de progrssion de ses taches
                    
                    if phase == 'reserve' :
                        budget_reserve1 = budget_reserve + task_budget
                        budget_engage1 = budget_engage
                        budget_consome1 = budget_consome
                        budget_restant1 = budget_restant - task_budget
                    elif phase == 'engage':
                        budget_reserve1 = budget_reserve
                        budget_engage1 = budget_engage + task_budget
                        budget_consome1 = budget_consome
                        budget_restant1 = budget_restant - task_budget               
                    elif  phase == 'consome':
                        budget_reserve1 = budget_reserve
                        budget_engage1 = budget_engage 
                        budget_consome1 = budget_consome + task_budget
                        budget_restant1 = budget_restant - task_budget
 
                else:
                    
                    budget_reserve1 = budget_reserve
                    budget_engage1 = budget_engage 
                    budget_consome1 = budget_consome
                    budget_restant1 = budget_restant
                budget_reserve = budget_reserve1
                budget_engage = budget_engage1 
                budget_consome = budget_consome1
                budget_restant = budget_restant1
        else:
            budget_reserve = 0
            budget_engage = 0
            budget_consome = 0
            budget_restant = Budget_activite
        return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

def activiteBedgetReserveEngage(activite_id, projectentitie_id, Budget_activite):
        # Recuperation des taches de l'activité en question
        data= Tasks.objects.raw("SELECT tache_tasks.id, tache_tasks.task, tache_tasks.budget FROM tache_tasks INNER JOIN tache_responsibles ON (tache_tasks.responsible_id = tache_responsibles.id) WHERE (tache_responsibles.project_entity_id=" +str(projectentitie_id) +" and tache_tasks.activity_id =" + str(activite_id) + ")")
        budget_reserve = 0
        budget_engage = 0
        budget_consome = 0       
        budget_restant = Budget_activite
        if data :
            i=0
            for task in data:
                task_budget = task.budget
                phase =''
                task_id = task.id
                # Recupération des progressions de chaque tache verification du niveau de progression de la tache
                progression = Progressions.objects.raw("SELECT tache_progressions.phase_id, tache_progressions.id FROM tache_progressions INNER JOIN tache_phases ON (tache_progressions.phase_id = tache_phases.id) WHERE (tache_progressions.task_id =" + str(task_id) +")")
                if progression :
                    j=0
                    for prog in progression:                       
                        phase_id = prog.phase_id
                        phass = Phases.objects.get(id=phase_id)
                    
                        progres_phase = phass.phase
                        if progres_phase in ("To do","Proposals examination", "Tender", "Tor drafting") and phase not in("engage", "consome"):
                            phase = 'reserve'
                        elif progres_phase in ("Validation","Report", "Progress rate (%)", "contract signature") and  phase !="consome":
                            phase = 'engage'
                        elif progres_phase in  ('Payement', 'Done'):
                            phase = 'consome'
                    # Calcul des budget reservés, engagés, consomés et restants pour l'activité en question selon le niveau de progrssion de ses taches
                    if phase == 'reserve' :
                        budget_reserve = budget_reserve + task_budget
                        budget_engage = budget_engage
                        budget_consome = budget_consome
                        budget_restant = budget_restant - task_budget
                    elif phase == 'engage':
                        budget_reserve = budget_reserve
                        budget_engage = budget_engage + task_budget
                        budget_consome = budget_consome
                        budget_restant = budget_restant - task_budget                 
                    else :
                        budget_reserve = budget_reserve
                        budget_engage = budget_engage 
                        budget_consome = budget_consome + task_budget
                        budget_restant = budget_restant - task_budget
        else:
            budget_reserve = 0
            budget_engage = 0
            budget_consome = 0
            budget_restant = Budget_activite
        return(budget_reserve, budget_engage, budget_consome, budget_restant, data)

# Create your views here.
def home(request):
    # template_name = 'tache/responsibles_detail.html'
    # return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'tache/home.html')

def dictfetchall(cursor):

    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
def namedtuplefetchall(cursor):

    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


# Responsibles _________________________________________________________

class ResponsiblesListView(LoginRequiredMixin, generic.ListView):
    model = Responsibles
    template_name = 'tache/responsibles_list.html'
    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global projectentitie_id
        global entitie_id
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]               
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        responsables = Responsibles.objects.filter(entity_id= entitie_id)
        context = super().get_context_data(**kwargs)
        context['responsables']=responsables
        context['Entite'] = curant_entitie    
        context['projet_entitie_id']=projectentitie_id
        context['entitie_id']=entitie_id
        return context

class ResponsibleDetailView(LoginRequiredMixin, generic.DetailView):
    model = Responsibles
    template_name = 'tache/responsible_detail.html'

class ResponsibleAddView(LoginRequiredMixin, generic.CreateView):
    model = Responsibles
    # form_class = ProjetForm
    template_name = 'tache/responsible_add.html'
    fields = '__all__'

class ResponsibleUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Responsibles
    # form_class = ProjetForm
    template_name = 'tache/responsible_update.html'
    fields = '__all__'

class ResponsibleDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Responsibles
    # form_class = ProjetForm
    template_name = 'tache/responsible_delete.html'
    fields = '__all__'
    success_url = reverse_lazy('tache:responsibles-list')

# Entities _________________________________________________________

class EntitiesListView(LoginRequiredMixin, generic.ListView):
    model = Entities
    template_name = 'tache/entities_list.html'
    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global projectentitie_id
        global entitie_id
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]               
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        entites = Entities.objects.filter(id= entitie_id)
        context = super().get_context_data(**kwargs)
        context['entites']=entites
        context['Entite'] = curant_entitie    
        context['projet_entitie_id']=projectentitie_id
        context['entitie_id']=entitie_id
        return context


class EntityDetailView(LoginRequiredMixin, generic.DetailView):
    model = Entities
    template_name = 'tache/entity_detail.html'

class EntityAddView(LoginRequiredMixin, generic.CreateView):
    model = Entities
    # form_class = ProjetForm
    template_name = 'tache/entity_add.html'
    fields = '__all__'

class EntityUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Entities
    # form_class = ProjetForm
    template_name = 'tache/entity_update.html'
    fields = '__all__'

class EntityDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Entities
    # form_class = ProjetForm
    template_name = 'tache/entity_delete.html'
    fields = '__all__'
    success_url = reverse_lazy('tache:entities-list')

# Axes _________________________________________________________

class AxesListView(LoginRequiredMixin, generic.ListView):
    model = Axes
    template_name = 'tache/axes_list.html'

    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global Projects_id
        global budget_total
        global budget_axe
        global axe_id
        global entitie_id
        global projectentitie_id
        global Axes_list
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            print("1189_curant_username ====== ", curant_username)
           #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            if projectentitie_id !=5:
                Axes_list= Axes.objects.raw("SELECT DISTINCT tache_axes.id, tache_axes.name FROM tache_projectentities INNER JOIN tache_projects ON tache_projects.id = tache_projectentities.project_id INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id WHERE (tache_projectentities.entity_id=" + str(entitie_id) +")")
                # Budget projet par entity 
                budget = axesBudget(entitie_id)
                budget_axe = budget[0]
                budget_total = budget[1]
            else:
                budget = axesBudgetOss()
                budget_total = budget         
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        aois_in_axe = Aoi.objects.none()
        for proj in Projects.objects.filter(axe=self.kwargs.get('pk')):
            aois_in_axe = aois_in_axe.union(proj.aoi_set.all())
        smjson = serialize('geojson', aois_in_axe , geometry_field='geom', fields=('name',))
        if projectentitie_id !=5:
            fonction2 = budget_Axes(entitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = fonction2[3]
            data1 = fonction2[4]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['Entite'] = curant_entitie
            context['axes']= Axes_list
            context['Budget']= budget_axe
            context['Budget_total']= budget_total        
            context['aoi'] = smjson
            context['entitie_id']=projectentitie_id
            context['labels'] = labels
            context['data']=data
        else:
            fonction2 = budget_AxesOss()
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = budget_total - (budget_reserve + budget_engage + budget_consome)
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['axes']= data1
            context['Budget_total']= budget_total        
            context['aoi'] = smjson
            context['entitie_id']=projectentitie_id
            context['labels'] = labels
            context['data']=data
        return context

def Taux_progression_Axes(Axe_id, projectentitie_id):  
    projectenti= ProjectEntities.objects.get(id = projectentitie_id) 
    if projectenti:       
        projet_id = projectenti.project_id
        entitie_id= projectenti.entity_id
    projets=Projects.objects.get(axe_id=Axe_id, id=projet_id)
    if projets:
        l6=()
        l7=(("", "", "", ""),)
        taux_prog_Projets = Taux_progression_Projects(projet_id, projectentitie_id)
        budget_project = projectBudget(projet_id, entitie_id)
        projet_Name=Projects.objects.get(id=projet_id).acronym
        if taux_prog_Projets and budget_project !=0:
            Prog_proj =0               
            for Progress_projet in taux_prog_Projets:
                Progres_proj=((Progress_projet[2]/budget_project)*Progress_projet[3])
                Prog_proj=Prog_proj + Progres_proj
            l7 =((projet_id, projet_Name, budget_project, int(Prog_proj)),)
            l6= l6 + l7
        else:
            l7=l7
        return(l6)
    else:
        l6=()
        return(l6) 

def Taux_progression_Axe_implementation(Axe_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            entitie_id=proj_entitie.entity_id           
            projectentitie_Acronim= proj_entitie.name
            budget_Axe = axeBudget(axe_id, entitie_id)
            taux_Axes = Taux_progression_Axes(Axe_id, projectentitie_id)
            if taux_Axes and budget_Axe !=0:
                Prog_Axe =0
                for taux_Axe in taux_Axes:
                    Progress_Axe= ((taux_Axe[3]/budget_Axe[0])*taux_Axe[2])
                    Prog_Axe=Prog_Axe + Progress_Axe
                l3= ((Axe_id, projectentitie_Acronim, budget_Axe[0], int(Prog_Axe)),)
                l=l+l3
            else:
                #l3= ((result_id, projectentitie_Acronim, 0, 0),)
                l=l
        return(l)

    return(l)   
def chartJ(request):
    # template_name = 'tache/responsibles_detail.html'
    # return HttpResponse("Hello, world. You're at the polls index.")
    return render(request, 'tache/Chart_views.html')


class AxeDetailView(LoginRequiredMixin, generic.DetailView):
    model = Axes
    template_name = 'tache/axe_detail.html'

    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global Projects_id
        global budget_total
        global budget_axe
        global axe_id
        global entitie_id
        global projectentitie_id
        global projets
        global aois_in_axe
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
           #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            axe_id = str(self.kwargs.get('pk'))
            if projectentitie_id !=5:
                projets= Projects.objects.raw("SELECT DISTINCT tache_projects.id, tache_projects.acronym FROM tache_projectentities INNER JOIN tache_projects ON tache_projects.id = tache_projectentities.project_id WHERE (tache_projectentities.entity_id=" + str(entitie_id) + "and tache_projects.axe_id=" + str(axe_id)+")")
                l = ()
                for projet in projets:
                    l=l + (projet.id,)
                aois_in_axe = Aoi.objects.filter(project_id__in= l)

                # Budget projet par entity                
                budget = axeBudget(axe_id, entitie_id)
                budget_axe = budget[0]
                budget_total = budget[1]
            else:
                projets= Projects.objects.all()
                aois_in_axe = Aoi.objects.none()
                for proj in Projects.objects.filter(axe=self.kwargs.get('pk')):
                    aois_in_axe = aois_in_axe.union(proj.aoi_set.all())
                # Budget projet par entity                
                
                budget_total =  axeBudgetOss(axe_id)
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        if projectentitie_id !=5:
            prog_projets=Taux_progression_Axes(axe_id, projectentitie_id)
            if prog_projets and budget_axe !=0:
                Prog_Axe=0
                for Progress_proj in prog_projets:
                    Progress_projet= ((Progress_proj[2]/budget_axe)*Progress_proj[3])
                    Prog_Axe=Prog_Axe + Progress_projet
                Progres_Axe= int(Prog_Axe)
            else:
                Progres_Axe = 0
        else:
            prog_Axes=Taux_progression_Axe_implementation(axe_id)
            if prog_Axes and budget_total !=0:
                Prog_Axe=0
                for Progr_Axe in prog_Axes:                 
                    Progress_Axe= ((Progr_Axe[2]/budget_total)*Progr_Axe[3])
                    Prog_Axe=Prog_Axe + Progress_Axe
                Progres_Axe= int(Prog_Axe)
                print("Progres_Axe  ======= ", Progres_Axe)
            else:
                Progres_Axe = 0
                print("Progres_Axe R ======= ", Progres_Axe)
        context = super().get_context_data(**kwargs)
        smjson = serialize('geojson', aois_in_axe , geometry_field='geom', fields=('name',))
        if projectentitie_id !=5:
            fonction2 = budget_Axe(axe_id, entitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = fonction2[3]
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['Entite'] = curant_entitie
            context['projets']= projets
            context['Budget']= budget_axe
            context['Budget_total']= budget_total        
            context['aoi'] = smjson
            context['entitie_id']=projectentitie_id
            context['prog_projets']=prog_projets
            context['Progres_Axe']=Progres_Axe
            context['labels']=labels
            context['data']=data
        else:
            fonction2 = budget_AxeOss(axe_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = budget_total - (budget_reserve + budget_engage + budget_consome)
            data1 = fonction2[4]
            if budget_total != 0:
                labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
                context['labels']=labels
                context['data']=data
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['axes']= data1
            context['Budget_total']= budget_total        
            context['aoi'] = smjson
            context['entitie_id']=projectentitie_id
            context['progress_Axes']=prog_Axes
            context['Progres_Axe']=Progres_Axe
            

        return context


class AxeAddView(LoginRequiredMixin, generic.CreateView):
    model = Axes
    # form_class = ProjetForm
    template_name = 'tache/axe_add.html'
    fields = '__all__'


class AxeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Axes
    # form_class = ProjetForm
    template_name = 'tache/axe_update.html'
    fields = '__all__'


class AxeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Axes
    template_name = 'tache/axe_delete.html'
    fields = '__all__'
    success_url = reverse_lazy('tache:axes-list')

#_______________________________Authentification________________________________________

# Projects _________________________________________________________

class ProjectsListView(LoginRequiredMixin, generic.ListView):
    model = Projects
    template_name = 'tache/projects_list.html'
    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global projets
        global entitie_id
        global Aois
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            if curant_entitie != 'OSS':
                l = ()
                Entites = ProjectEntities.objects.filter(entity_id = entitie_id)
                for entite in Entites:
                    l=l + (entite.project_id,)
                Aois = Aoi.objects.filter(project_id__in= l)
                projets= Projects.objects.filter(id__in = l)
            else:
                projets= Projects.objects.all()
                Aois = Aoi.objects.all()               
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        smjson0 = serialize('geojson', Aois, geometry_field='geom', fields=('name',))
        context['aoi'] = smjson0
        context['Entite'] = curant_entitie    
        context['projets']=projets
        context['entitie_id']=entitie_id
        return context


def Taux_progression_Projet_implementation(project_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            entitie_id=proj_entitie.entity_id
           
            projectentitie_Acronim= proj_entitie.name
            budget_project = projectBudget(project_id, entitie_id)
            taux_Projects = Taux_progression_Projects(project_id, projectentitie_id)
            if taux_Projects and budget_project !=0:
                Prog_Project =0
                for taux_Project in taux_Projects:
                    Progress_Project= ((taux_Project[3]/budget_project)*taux_Project[2])
                    Prog_Project=Prog_Project + Progress_Project
                Etat_Project = Evaluation_progression_Project(project_id, Prog_Project)
                l3= ((project_id, projectentitie_Acronim, budget_project, int(Prog_Project), Etat_Project[1]),)
                l=l+l3
            else:
                #l3= ((result_id, projectentitie_Acronim, 0, 0),)
                l=l
        return(l)
    else:
        print("pas d'entités inscrite dans le projet ")
    return(l)


def Taux_progression_Projects(project_id, project_entity_id):
    compoments=Components.objects.filter(project_id=project_id)
    l=()
    if compoments:

        l1 = ("",)
        for compoment in compoments:
            compoment_id = compoment.id
            if compoment_id in l:
                l1=()
            else:
                l1= (compoment_id,)
            l= l +l1
    else: 
        l=l
    if l:
        #print("l compoment = ", l)
        l6=()
        l7=(("", "", "", "" ),)
        for compoment_id in l:
            taux_prog_comp = Taux_progression_Component(compoment_id, project_entity_id)
            Budget_compoment=compoment_Budget(compoment_id, project_entity_id)
            if taux_prog_comp and Budget_compoment !=0 :
                Prog_Comp =0
                compoment_Name=Components.objects.get(id=compoment_id).component
                for Progress_compoment in taux_prog_comp:
                    Progres_Comp=((Progress_compoment[2]/Budget_compoment)*Progress_compoment[3])
                    Prog_Comp=Prog_Comp + Progres_Comp
                Etat_Comp = Evaluation_progression_Component(compoment_id, Prog_Comp)
                l7 =((compoment_id, compoment_Name, Budget_compoment, int(Prog_Comp), Etat_Comp[1]),)
                l6= l6 + l7
            else:
                l6=l6
        return(l6)
    else:
        l6=()
        return(l6) 
def Component_date(Comp_id):
        results = Results.objects.filter(component_id=Comp_id)
        if results :
            i = 0
            for result in results :
                Result_id = result.id
                result_date =Date_debut_Date_fin_result(Result_id)
                if i == 0 :
                    date_due_debut = result_date[0]
                    date_due_fin = result_date[1]
                else:
                    if result_date[0] < date_due_debut :
                        date_due_debut = result_date[0]
                    else: 
                        date_due_debut = date_due_debut
                    if result_date[1] > date_due_fin :
                        date_due_fin = result_date[1]
                    else: 
                        date_due_fin = date_due_fin
                i = i + 1
        return(date_due_debut, date_due_fin)

def Evaluation_progression_Project(Project_id, prog_Project):
    composantes =Components.objects.filter(project_id=Project_id)
    if composantes :
        i=0
        for composante in composantes:
            Comp_id = composante.id
            project_date = Component_date(Comp_id)
            if i == 0 :
                    date_due_debut = project_date[0]
                    date_due_fin = project_date[1]
            else:
                if project_date[0] < date_due_debut :
                    date_due_debut = project_date[0]
                else: 
                    date_due_debut = date_due_debut
                if project_date[1] > date_due_fin :
                    date_due_fin = project_date[1]
                else: 
                    date_due_fin = date_due_fin
            i = i + 1
    duree_Component = ((date_due_fin) - (date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (date_due_debut)).days
    duree_consommee_PourCent= int((duree_consommee/duree_Component)*100)
    if prog_Project < 100:
        if duree_consommee_PourCent >100:
            depassement = ((datetime.datetime.now().date()) - (date_due_fin)).days
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_PourCent
        if prog_duree < 100:
            decalage = prog_Project - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_Project - prog_duree) < -5 and (prog_Project - prog_duree) > -15:                
                etat = "risque de retard"
            elif (prog_Project - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement, date_due_debut, date_due_fin)
    else:
        if duree_consommee_PourCent <100:
            depassement = 0
            prog_duree = duree_consommee_PourCent
            etat = "Project cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "Project cloturée"
    return(prog_duree, etat, depassement, date_due_debut, date_due_fin)

class ProjectDetailView(LoginRequiredMixin, generic.DetailView):    
    model = Projects
    # form_class = ProjectForm
    template_name = 'tache/project_detail.html'
    
    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global budget_project
        global Projects_id
        global projectentitie_name
        global projectentitie_id
        global entitie_id
        global Projects_id
        global budget_Projet_Oss
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
           #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            #print('projectentitie_id_2 == ', projectentitie_id)
            #print('entitie_id == ', projectentitie_id)

            Projects_id = str(self.kwargs.get('pk'))
            # projectentite
            projentite =projectEntities(projectentitie_id)
            projectentitie_name = projentite
            if projectentitie_id !=5:
                # Budget projet par entity 
                budget_project = projectBudget(Projects_id, entitie_id)
                #print('budget_project_1 = ', budget_project)
            else:
                project= Projects.objects.filter(id=Projects_id)
                budget_Projet_Oss = projectBudgetOss_entites(Projects_id)
                if project:
                    for proj in project:
                        budget_project =proj.budget
                        if budget_project is None:
                            budget_project = 0
                else:
                    budget_project =0

                #budget_project = projectBudgetOss(Projects_id)          
        return super().dispatch(request, *args, **kwargs)
        
    def get_context_data(self, **kwargs):
        # Call the base implementationest first to get a context
        if projectentitie_id !=5:
            Progress_Compoments = Taux_progression_Projects(Projects_id, projectentitie_id)
            if Progress_Compoments and budget_project !=0:
                #print("taux_comp = ", Progress_Compoments)
                Prog_Project=0
                for Progress_Compoment in Progress_Compoments:
                    Progress_comp= ((Progress_Compoment[2]/budget_project)*Progress_Compoment[3])
                    Prog_Project=Prog_Project + Progress_comp
                Prog_Project= int(Prog_Project)
                duree_Project =Evaluation_progression_Project(Projects_id, Prog_Project)
                Etat=duree_Project[1]
                prog_duree=duree_Project[0]
                depassement = duree_Project[2]
            else:
                Prog_Project = 0
                duree_Project =Evaluation_progression_Project(Projects_id, Prog_Project)
                Etat=duree_Project[1]
                prog_duree=duree_Project[0]
                depassement = duree_Project[2]
        else:
            Progress_Projects=Taux_progression_Projet_implementation(Projects_id)
            if Progress_Projects and budget_project !=0:
                #print("Progress_Projects = ", Progress_Projects)
                Prog_Project=0
                for Progress_Project in Progress_Projects:
                    Progress_Proj= ((Progress_Project[2]/budget_project)*Progress_Project[3])
                    Prog_Project=Prog_Project + Progress_Proj
                Prog_Project= int(Prog_Project)
                duree_Project =Evaluation_progression_Project(Projects_id, Prog_Project)
                Etat=duree_Project[1]
                prog_duree=duree_Project[0]
                depassement = duree_Project[2]
            else:
                Prog_Project = 0
                duree_Project =None
                Etat=None
                prog_duree=None
                depassement = None

        context = super().get_context_data(**kwargs)
        #print('budget_project = ', budget_project)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe FROM tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id WHERE (((tache_projects.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        if projectentitie_id !=5:
            fonction2 = budget_Project(Projects_id, projectentitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant =  fonction2[3]
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['Role_Entite'] = projectentitie_name
            context['Entite'] = curant_entitie
            context['components']= data1
            context['Progress_Compoments']=Progress_Compoments
            context['Prog_Project']=Prog_Project
            context['labels']=labels
            context['data']=data
            context['parent'] = dictfetchall(cursor)
            smjson = serialize('geojson', Projects.objects.get(id=self.kwargs.get('pk')).aoi_set.all() , geometry_field='geom', fields=('name',))
            context['aoi'] = smjson
            context['Budget']= budget_project
            context['entitie_id']=projectentitie_id
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement 
        else:
            fonction2 = budget_ProjectOss(Projects_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = budget_project - (budget_reserve + budget_engage + budget_consome)
            data1 = fonction2[4]
            for budget_Projet_Os in budget_Projet_Oss:
                    if budget_Projet_Os[0]=="Total":
                        labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                        data=[int(budget_Projet_Os[2]), int(budget_Projet_Os[3]), int(budget_Projet_Os[4]), int(budget_Projet_Os[5])]
                        context['labels']=labels
                        context['data']=data
                    #else:
                    #    labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                    #    data=[int(0), int(0), int(0), int(0)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['components']= data1
            context['Progress_Projects']=Progress_Projects
            context['Prog_Project']=Prog_Project      
            context['parent'] = dictfetchall(cursor)
            smjson = serialize('geojson', Projects.objects.get(id=self.kwargs.get('pk')).aoi_set.all() , geometry_field='geom', fields=('name',))
            context['aoi'] = smjson
            context['Budget']= budget_project
            context['entitie_id']=projectentitie_id
            context['Budget_Projet']=budget_Projet_Oss
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement 
        return context



class ProjectAddView(LoginRequiredMixin, generic.CreateView):
    model = Projects
    form_class = ProjectForm
    template_name = 'tache/project_add.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:axe-detail', kwargs={'pk': self.kwargs['axe_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        axe_id = self.kwargs['axe_id']
        axe = Axes.objects.get(id=axe_id)
        context['axe'] = axe
        return context


class ProjectUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Projects
    # form_class = ProjectForm
    template_name = 'tache/project_update.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:axe-detail', kwargs={'pk': self.kwargs['axe_id']})

class ProjectDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Projects
    # form_class = ProjectForm
    template_name = 'tache/project_delete.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:axe-detail', kwargs={'pk': self.kwargs['axe_id']})

# Components _________________________________________________________

class ComponentsListView(LoginRequiredMixin, generic.ListView):
    model = Components
    template_name = 'tache/components_list.html'

def Taux_progression_Component_implementation(compoment_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            projectentitie_Acronim= proj_entitie.name
            Budget_compoment= compoment_Budget(compoment_id, projectentitie_id)
            Budget_Comp = Budget_compoment
            taux_Comps = Taux_progression_Component(compoment_id, projectentitie_id)
            if taux_Comps and Budget_Comp !=0:
                Prog_Comp =0
                for taux_Comp in taux_Comps:
                    Progress_Comp= ((taux_Comp[3]/Budget_Comp)*taux_Comp[2])
                    Prog_Comp=Prog_Comp + Progress_Comp
                Etat_Comp = Evaluation_progression_Component(compoment_id, Prog_Comp)
                l3= ((compoment_id, projectentitie_Acronim, Budget_Comp, int(Prog_Comp), Etat_Comp[1]),)
                l=l+l3
            else:
                #l3= ((result_id, projectentitie_Acronim, 0, 0),)
                l=l
        return(l)
    else:
        print("pas d'entités inscrite dans le projet ")
    return(l)
     
        
def Taux_progression_Component(compoment_id, project_entity_id):
    results=Results.objects.filter(component=compoment_id)
    if results:
        l=()
        l1 = ("",)
        for result in results:
            result_id = result.id
            if result_id in l:
                l1=()
            else:
                l1= (result_id,)
            l= l +l1
    else: 
        l=l
    
    if l:
        l6=()
        l7=(("", "", "", "" ),)
        for result_id in l:
            taux_prog_results = Taux_progression_Result(result_id, project_entity_id)
            Budget_result=resultBudget(result_id, project_entity_id)
            if taux_prog_results and Budget_result!=0:
                Prog_Result =0
                Result_Name=Results.objects.get(id=result_id).result
                for Progress_Result in taux_prog_results:
                    Progres_Result=((Progress_Result[2]/Budget_result)*Progress_Result[3])
                    Prog_Result=Prog_Result + Progres_Result
                Etat_Result = Evaluation_progression_Result(result_id, Prog_Result)
                l7 =((result_id, Result_Name, Budget_result, int(Prog_Result), Etat_Result[1]),)
                l6= l6 + l7
            else:
                l6=l6
        return(l6)
    else:
        l6=()
        return(l6)    
def Evaluation_progression_Component(Comp_id, prog_Comp):
    results = Results.objects.filter(component_id=Comp_id)
    if results :
        i = 0
        for result in results :
            Result_id = result.id
            result_date =Date_debut_Date_fin_result(Result_id)
            if i == 0 :
                date_due_debut = result_date[0]
                date_due_fin = result_date[1]
            else:
                if result_date[0] < date_due_debut :
                    date_due_debut = result_date[0]
                else: 
                    date_due_debut = date_due_debut
                if result_date[1] > date_due_fin :
                    date_due_fin = result_date[1]
                else: 
                    date_due_fin = date_due_fin
            i = i + 1
    duree_Component = ((date_due_fin) - (date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (date_due_debut)).days
    duree_consommee_PourCent= int((duree_consommee/duree_Component)*100)
    if prog_Comp < 100:
        if duree_consommee_PourCent >100:
            depassement = ((datetime.datetime.now().date()) - (date_due_fin)).days
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_PourCent
        if prog_duree < 100:
            decalage = prog_Comp - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_Comp - prog_duree) < -5 and (prog_Comp - prog_duree) > -15:                
                etat = "risque de retard"
            elif (prog_Comp - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement, date_due_debut, date_due_fin)
    else:
        if duree_consommee_PourCent <100:
            depassement = 0
            prog_duree = duree_consommee_PourCent
            etat = "Comp cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "Comp cloturée"
    return(prog_duree, etat, depassement, date_due_debut, date_due_fin)
class ComponentDetailView(LoginRequiredMixin, generic.DetailView):
    model = Components
    template_name = 'tache/component_detail.html'
    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_usernam_id
        global curant_entitie
        global budget_Composante_Oss
        global Budget_compoment
        global Components_id
        global projectentitie_id
        global projectentitie_name
        global entitie_id
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
           #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            Components_id = str(self.kwargs.get('pk'))
            # prject id
            project = componentsProjects_id(Components_id)
            Projects_id = project            
            # projectentite
            projentite =projectEntities(projectentitie_id)
            projectentitie_name = projentite
            if projectentitie_id !=5:    
                Budget_compoment= compoment_Budget(Components_id, projectentitie_id)
            else:
                budget_Composante_Oss = CompomentBudgetOss_entites(Components_id, Projects_id)
                compoments = Components.objects.filter(id = Components_id)
                for compoment in compoments:
                    
                    Budget_compoment=compoment.budget
                    if Budget_compoment is None:
                        Budget_compoment = 0
                #Budget_compoment= compoment_BudgetOss(Components_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        if projectentitie_id !=5:
            taux_Results = Taux_progression_Component(Components_id, projectentitie_id)
            if taux_Results and Budget_compoment !=0:
                Prog_Comp=0
                for taux_prog_Result in taux_Results:
                    Progress_comp= ((taux_prog_Result[2]/Budget_compoment)*taux_prog_Result[3])
                    Prog_Comp=Prog_Comp + Progress_comp
                Prog_Comp= int(Prog_Comp)
                duree_Comp =Evaluation_progression_Component(Components_id, Prog_Comp)
                Etat=duree_Comp[1]
                prog_duree=duree_Comp[0]
                depassement = duree_Comp[2]
            else:
                Prog_Comp = 0
                duree_Comp =Evaluation_progression_Component(Components_id, Prog_Comp)
                Etat=duree_Comp[1]
                prog_duree=duree_Comp[0]
                depassement = duree_Comp[2]
        else:
            taux_prog_Comp =Taux_progression_Component_implementation(Components_id)
            if taux_prog_Comp and Budget_compoment !=0:
                Prog_Comp=0
                for taux_prog_compo in taux_prog_Comp:
                    Progress_comp= ((taux_prog_compo[2]/Budget_compoment)*taux_prog_compo[3])
                    Prog_Comp=Prog_Comp + Progress_comp
                Prog_Comp= int(Prog_Comp)
                duree_Comp =Evaluation_progression_Component(Components_id, Prog_Comp)
                Etat=duree_Comp[1]
                prog_duree=duree_Comp[0]
                depassement = duree_Comp[2]
            else:
                Prog_Comp = 0
                duree_Comp =Evaluation_progression_Component(Components_id, Prog_Comp)
                Etat=duree_Comp[1]
                prog_duree=duree_Comp[0]
                depassement = duree_Comp[2]

        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project FROM tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id WHERE (((tache_components.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        if projectentitie_id !=5:
            fonction2 = budget_Compoment(Components_id, projectentitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = fonction2[3]
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['Role_Entite'] = projectentitie_name
            context['Entite'] = curant_entitie
            context['results']= data1
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_compoment
            context['entitie_id']=projectentitie_id
            context['taux_Results'] = taux_Results
            context['Prog_Comp'] = Prog_Comp
            context['labels'] = labels
            context['data'] = data
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement             
        else:
            fonction2 = budget_CompomentOss(Components_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant =  Budget_compoment - (budget_reserve + budget_engage + budget_consome)
            data = fonction2[4]
            for budget_Composante in budget_Composante_Oss:
                    if budget_Composante[0]=="Total":
                        labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                        data=[int(budget_Composante[2]), int(budget_Composante[3]), int(budget_Composante[4]), int(budget_Composante[5])]

            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['results']= data
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_compoment
            context['entitie_id']=projectentitie_id
            context['Budget_Comp']= budget_Composante_Oss
            context['taux_prog_Comp'] = taux_prog_Comp
            context['Prog_Comp'] = Prog_Comp
            context['labels'] = labels
            context['data'] = data
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement
        return context


class ComponentAddView(LoginRequiredMixin, generic.CreateView):
    model = Components
    form_class = ComponentForm
    template_name = 'tache/component_add.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:project-detail', kwargs={'pk': self.kwargs['project_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        project_id = self.kwargs['project_id']
        project = Projects.objects.get(id=project_id)
        context['project'] = project
        return context


class ComponentUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Components
    form_class = ComponentForm
    template_name = 'tache/component_update.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:project-detail', kwargs={'pk': self.kwargs['project_id']})


class ComponentDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Components
    # form_class = ComponentForm
    template_name = 'tache/component_delete.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:project-detail', kwargs={'pk': self.kwargs['project_id']})

# Results _________________________________________________________

class ResultsListView(LoginRequiredMixin, generic.ListView):
    model = Results
    template_name = 'tache/results_list.html'

def Taux_progression_Result(result_id, project_entity_id):
    activitesentites= ActivitiesEntitiesBudget.objects.filter(project_entity_id = project_entity_id)
    # récupération des produits du résultat en question
    products=Products.objects.filter(result_id=result_id)
    if products:
        l=()
        l1 = ("",)
        for product in products:
            product_id = product.id
            if product_id in l:
                l1=()
            else:
                l1= (product_id,)
            l= l +l1
    else: 
        l=()
    if l:
        l6=()
        l7=(("", "", "", "" ),)
        for product_id in l:
            taux_prog_prods = Taux_progression_Product(product_id, project_entity_id)
            if taux_prog_prods:
                Prog_Product =0
                product_Name=Products.objects.get(id=product_id).product
                for Progress_Activity in taux_prog_prods:
                    Budget_product= prodactBudget(product_id, project_entity_id)
                    Progress_Prod=((Progress_Activity[2]/Budget_product)*Progress_Activity[3])
                    Prog_Product=Prog_Product + Progress_Prod
                Etat_Product = Evaluation_progression_Product(product_id, Prog_Product)
                l7 =((product_id, product_Name, Budget_product, int(Prog_Product), Etat_Product[1]),)
                l6= l6 + l7
            else:
                l6=l6
        return(l6)
    else:
        l6=()
        return(l6)

def Taux_progression_Result_implementation(result_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            projectentitie_Acronim= proj_entitie.name
            Budget_result=resultBudget(Result_id, projectentitie_id)
            Budget_Result = Budget_result
            taux_Prodacts= Taux_progression_Result(result_id, projectentitie_id)
            if taux_Prodacts and Budget_Result !=0:
                Prog_Result =0
                for taux_Prodact in taux_Prodacts:
                    Progress_Result= ((taux_Prodact[3]/Budget_Result)*taux_Prodact[2])
                    Prog_Result=Prog_Result + Progress_Result
                Etat_result = Evaluation_progression_Result(result_id, Prog_Result)
                l3= ((result_id, projectentitie_Acronim, Budget_Result, int(Prog_Result), Etat_result[1]),)
                l=l+l3
            else:
                l=l
        return(l)
    return(l)

def Date_debut_Date_fin_result(Result_id):
    products = Products.objects.filter(result_id=Result_id)
    if products :
        i=0
        for product in products :
            product_id = product.id
            activites=Activities.objects.filter(product_id=product_id)
            if activites :
                for activite in activites:
                    if i == 0 :
                        date_due_fin = activite.date_due_debut
                        date_due_debut = activite.date_due_fin
                        i=i+1                    
                for activite in activites:
                    if activite.date_due_debut <= date_due_debut :
                        date_due_debut = activite.date_due_debut
                    if activite.date_due_fin >= date_due_fin:
                        date_due_fin = activite.date_due_fin
    return(date_due_debut, date_due_fin)

def Evaluation_progression_Result(Result_id, prog_Result):
    result_date =Date_debut_Date_fin_result(Result_id)
    date_due_debut = result_date[0]
    date_due_fin = result_date[1]
    duree_result = ((date_due_fin) - (date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (date_due_debut)).days
    duree_consommee_PourCent= int((duree_consommee/duree_result)*100)
    if prog_Result < 100:
        if duree_consommee_PourCent >100:
            depassement = ((datetime.datetime.now().date()) - (date_due_fin)).days
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_PourCent
        if prog_duree < 100:
            decalage = prog_Result - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_Result - prog_duree) < -5 and (prog_Result - prog_duree) > -15:                
                etat = "risque de retard"
            elif (prog_Result - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement, date_due_debut, date_due_fin)
    else:
        if duree_consommee_PourCent <100:
            depassement = 0
            prog_duree = duree_consommee_PourCent
            etat = "Result cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "Result cloturée"
    return(prog_duree, etat, depassement, date_due_debut, date_due_fin)



class ResultDetailView(LoginRequiredMixin, generic.DetailView):
    model = Results
    template_name = 'tache/result_detail.html'

    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global Budget_result
        global projectentitie_id
        global Result_id
        global projectentitie_name
        global entitie_id
        global Budget_results
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            Result_id = str(self.kwargs.get('pk'))
            #Composante_id
            Components= resultsComponents_id(Result_id)
            Components_id = Components
            # prject id
            project = componentsProjects_id(Components_id)
            Projects_id = project
            # projectentite
            projentite =projectEntities(projectentitie_id)
            projectentitie_name = projentite
            if projectentitie_id !=5:
                # Budget de avtivite
                Budget_result=resultBudget(Result_id, projectentitie_id)
            else:
                Budget_results = ResultBudgetOss_entites(Result_id, Projects_id)
                results = Results.objects.get(id = Result_id )
                Budget_result=results.budget
                if Budget_result is None:
                    Budget_result = 0
                else:
                    Budget_result=Budget_result
                #Budget_result= resultBudgetOss(Result_id)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        if projectentitie_id !=5:
            taux_prog_result=Taux_progression_Result(Result_id, projectentitie_id)
            if taux_prog_result and Budget_result !=0:
                Prog_result=0
                for taux_prog in taux_prog_result:
                    Progress_resul= ((taux_prog[2]/Budget_result)*taux_prog[3])
                    Prog_result=Prog_result + Progress_resul
                Progress_result= int(Prog_result)
                duree_result =Evaluation_progression_Result(Result_id, Progress_result)
                Etat=duree_result[1]
                prog_duree=duree_result[0]
                depassement = duree_result[2]
            else:
                Progress_result = 0
                duree_result =Evaluation_progression_Result(Result_id, Progress_result)
                Etat=duree_result[1]
                prog_duree=duree_result[0]
                depassement = duree_result[2]
        else:
            taux_prog_result=Taux_progression_Result_implementation(Result_id)
            if taux_prog_result and Budget_result !=0:
                Prog_result=0
                for taux_prog in taux_prog_result:
                    Progress_resul= ((taux_prog[2]/Budget_result)*taux_prog[3])
                    Prog_result=Prog_result + Progress_resul
                Progress_result= int(Prog_result)
                duree_result =Evaluation_progression_Result(Result_id, Progress_result)
                Etat=duree_result[1]
                prog_duree=duree_result[0]
                depassement = duree_result[2]
            else:
                Progress_result = 0
                duree_result =Evaluation_progression_Result(Result_id, Progress_result)
                Etat=duree_result[1]
                prog_duree=duree_result[0]
                depassement = duree_result[2]

        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project, tache_components.id AS component_id, tache_components.component FROM tache_results INNER JOIN (tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id) ON tache_results.component_id = tache_components.id WHERE (((tache_results.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        if projectentitie_id !=5:
            fonction2 = budget_Result(Result_id, projectentitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = fonction2[3]
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]

            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['Role_Entite'] = projectentitie_name
            context['Entite'] = curant_entitie
            context['products']= data1
            context['taux_prog_products']=taux_prog_result
            context['taux_prog_result']=Progress_result
            context['labels']=labels
            context['data']=data
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_result
            context['entitie_id']=projectentitie_id
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement 
        else:
            fonction2 = budget_ResultOss(Result_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = Budget_result - (budget_reserve + budget_engage + budget_consome)
            data1 = fonction2[4]
            for Budget_result_T in Budget_results:
                    if Budget_result_T[0]=="Total":
                        labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                        data=[int(Budget_result_T[2]), int(Budget_result_T[3]), int(Budget_result_T[4]), int(Budget_result_T[5])]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['products']= data1
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_result
            context['entitie_id']=projectentitie_id
            context['Budget_Result']=Budget_results
            context['taux_prog_Results']=taux_prog_result
            context['taux_prog_result']=Progress_result
            context['labels']=labels
            context['data']=data
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement 
        return context

class ResultAddView(LoginRequiredMixin, generic.CreateView):
    model = Results
    form_class = ResultForm
    template_name = 'tache/result_add.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:component-detail', kwargs={'pk': self.kwargs['component_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        component_id = self.kwargs['component_id']
        component = Components.objects.get(id=component_id)
        context['component'] = component
        return context


class ResultUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Results
    form_class = ResultForm
    template_name = 'tache/result_update.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:component-detail', kwargs={'pk': self.kwargs['component_id']})

class ResultDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Results
    # form_class = ProjetForm
    template_name = 'tache/result_delete.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:component-detail', kwargs={'pk': self.kwargs['component_id']})

# Products _________________________________________________________
def Evaluation_progression_Product(product_id, prog_product):
    activites=Activities.objects.filter(product_id=product_id)
    if activites :
        i=0
        for activite in activites:
            if i == 0:
                date_due_fin = activite.date_due_debut
                date_due_debut = activite.date_due_fin
        for activite in activites:
            if activite.date_due_debut <= date_due_debut :
                date_due_debut = activite.date_due_debut
            else:
                date_due_debut = date_due_debut
            if activite.date_due_fin >= date_due_fin:
                date_due_fin = activite.date_due_fin
            else :
                date_due_fin = date_due_fin
    duree_product = ((date_due_fin) - (date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (date_due_debut)).days
    duree_consommee_PourCent= int((duree_consommee/duree_product)*100)
    if prog_product < 100:
        if duree_consommee_PourCent >100:
            depassement = ((datetime.datetime.now().date()) - (date_due_fin)).days
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_PourCent
        if prog_duree < 100:
            decalage = prog_product - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_product - prog_duree) < -5 and (prog_product - prog_duree) > -15:
                
                etat = "risque de retard"
            elif (prog_product - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement)
    else:
        if duree_consommee_PourCent <100:
            depassement = 0
            prog_duree = duree_consommee_PourCent
            etat = "Product cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "Product cloturée"
    return(prog_duree, etat, depassement, date_due_debut, date_due_fin)

class ProductsListView(LoginRequiredMixin, generic.ListView):
    model = Products
    template_name = 'tache/products_list.html'

class ProductDetailView(LoginRequiredMixin, generic.DetailView):
    model = Products
    template_name = 'tache/product_detail.html'

    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global product_id
        global Budget_product
        global projectentitie_name
        global projectentitie_id
        global entitie_id
        global Prodacts_Budget
        global responsable_id
        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            responsable_id = user_entite[3]
            product_id = str(self.kwargs.get('pk'))
            #Result_id
            Result = productsResult_id(product_id)
            Result_id = Result
            #Composante_id
            Components= resultsComponents_id(Result_id)
            Components_id = Components
            # prject id
            project = componentsProjects_id(Components_id)
            Projects_id = project           
            projentite =projectEntities(projectentitie_id)
            projectentitie_name = projentite
            if projectentitie_id !=5:
                Budget_product= prodactBudget(product_id, projectentitie_id)
            else:
                Prodacts_Budget = ProdactBudgetOss_entites(product_id, Projects_id)
                products = Products.objects.filter(id = product_id)
                for product in products:
                    Budget_product= product.budget
                    if Budget_product is None:
                        Budget_product = 0
                #Budget_product= prodactBudgetOss(product_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project, tache_components.id AS component_id, tache_components.component, tache_results.id AS result_id, tache_results.result FROM tache_products INNER JOIN (tache_results INNER JOIN (tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id) ON tache_results.component_id = tache_components.id) ON tache_products.result_id = tache_results.id WHERE (((tache_products.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        activites= Activities.objects.filter(product_id=product_id)
        if projectentitie_id !=5:
            taux_prog_activites = Taux_progression_Product(product_id, projectentitie_id)
            if taux_prog_activites and Budget_product !=0:
                Prog_product=0
                for taux_prog in taux_prog_activites:
                    Progress_Activity= ((taux_prog[2]/Budget_product)*taux_prog[3])
                    Prog_product=Prog_product + Progress_Activity
                Prog_product= int(Prog_product)
                duree_product =Evaluation_progression_Product(product_id, Prog_product)
                Etat=duree_product[1]
                prog_duree=duree_product[0]
                depassement = duree_product[2]
            else:
                Prog_product = 0
                duree_product =Evaluation_progression_Product(product_id, Prog_product)
                Etat=duree_product[1]
                prog_duree=duree_product[0]
                depassement = duree_product[2]
        else:
            taux_prog_activites_impl = Taux_progression_Prodact_implementation(product_id)
            if taux_prog_activites_impl and Budget_product !=0:
                Prog_product=0
                for taux_prog in taux_prog_activites_impl:
                    Progress_Activity= ((taux_prog[2]/Budget_product)*taux_prog[3])
                    Prog_product=Prog_product + Progress_Activity
                Prog_product= int(Prog_product)
                duree_product =Evaluation_progression_Product(product_id, Prog_product)
                Etat=duree_product[1]
                prog_duree=duree_product[0]
                depassement = duree_product[2]
            else:
                Prog_product = 0
                duree_product =Evaluation_progression_Product(product_id, Prog_product)
                Etat=duree_product[1]
                prog_duree=duree_product[0]
                depassement = duree_product[2]
        if projectentitie_id !=5:
            fonction2=budget_Prodact(product_id, projectentitie_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = fonction2[3]
            data1 = fonction2[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            
            #cursor2.execute(data,)
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            context['Role_Entite'] = projectentitie_name
            context['Entite'] = curant_entitie
            context['activites']= data1
            context['taux_prog_activites']= taux_prog_activites
            context['taux_prog_product']= Prog_product
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_product
            context['entitie_id']=projectentitie_id
            context['labels'] = labels
            context['data']=data  
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement          
        else:
            fonction2=budget_ProdactOss(product_id)
            budget_reserve = fonction2[0]
            budget_engage = fonction2[1]
            budget_consome = fonction2[2]
            budget_restant = Budget_product - (budget_reserve + budget_engage + budget_consome)
            data = fonction2[4]
            for Budget_Prod in Prodacts_Budget:
                    if Budget_Prod[0]=="Total":
                        labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                        data=[int(Budget_Prod[2]), int(Budget_Prod[3]), int(Budget_Prod[4]), int(Budget_Prod[5])]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant
            #context['Role_Entite'] = projectentitie_name
            #context['Entite'] = curant_entitie
            context['activites']= activites
            context['parent'] = dictfetchall(cursor)
            context['Budget'] = Budget_product
            context['entitie_id']=projectentitie_id
            context['Prodacts_Budget']=Prodacts_Budget
            context['taux_prog_Prodact']= taux_prog_activites_impl
            context['prog_Prodact']= Prog_product
            context['labels']= labels
            context['data']= data
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement 
        return context

class ProductAddView(LoginRequiredMixin, generic.CreateView):
    model = Products
    form_class = ProductForm
    template_name = 'tache/product_add.html'

    def get_success_url(self):
        return reverse_lazy('tache:result-detail', kwargs={'pk': self.kwargs['result_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        result_id = self.kwargs['result_id']
        result = Results.objects.get(id=result_id)
        context['result'] = result
        return context


class ProductUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Products
    form_class = ProductForm
    template_name = 'tache/product_update.html'

    def get_success_url(self):
        return reverse_lazy('tache:result-detail', kwargs={'pk': self.kwargs['result_id']})


class ProductDeleteView(generic.DeleteView):
    model = Products
    # form_class = ProductForm
    fields = '__all__'
    template_name = 'tache/product_delete.html'

    def get_success_url(self):
        return reverse_lazy('tache:result-detail', kwargs={'pk': self.kwargs['result_id']})


# Activities _________________________________________________________

class ActivitiesListView(LoginRequiredMixin, generic.ListView):
    model = Activities
    template_name = 'tache/activities_list.html'
# calcul du taux de progression de chaque produit de chaque entité en question (taux_prog_prodact =((taux_prog_prodact_entite_i), (taux_prog_prodact_entite_i+1), ...)
def Taux_progression_Prodact_implementation(product_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            projectentitie_Acronim= proj_entitie.name
            Prodact_Bdget = prodactBudget(product_id, projectentitie_id)
            Budget_Prodact = Prodact_Bdget
            taux_Ativies= Taux_progression_Product(product_id,  projectentitie_id)
            if taux_Ativies and Budget_Prodact !=0:
                Prog_Prodact =0
                for taux_Ativie in taux_Ativies:
                    Progress_Prodact= ((taux_Ativie[3]/Budget_Prodact)*taux_Ativie[2])
                    Prog_Prodact=Prog_Prodact + Progress_Prodact
                Etat_product = Evaluation_progression_Product(product_id, Prog_Prodact)
                l3= ((product_id, projectentitie_Acronim, Budget_Prodact, int(Prog_Prodact), Etat_product[1]),)
                l=l+l3
            else:
                Prog_Prodact = 0
                #Etat_product = Evaluation_progression_Product(product_id, Prog_Prodact)
                #l3= ((product_id, projectentitie_Acronim, 0, 0, Etat_product[1]),)
                #l=l+l3
        return(l)
    else:
        print("pas d'entités inscrite dans le projet ")
    return(l)
# calcul du taux de progression de chaque activité du produit de l'entité en question (taux_prog_prodact =((taux_prog_activité_i), (taux_prog_activité_i+1), ...)
def Taux_progression_Product(Product_id,  projectentitie_id):
    activitesentites= ActivitiesEntitiesBudget.objects.filter(project_entity_id = projectentitie_id)

    if activitesentites:
        l=( )
        l4=("",)
        for activitesentite in activitesentites:
            activitesentite_id = activitesentite.activity_id
            if activitesentite_id in l:
                l4=()
            else:
                l4=(activitesentite_id,)
            l = l + l4
    else:
        l=()
    if l:
        l3=()
        l2=(("", "", "", "" , "" , "", ""),)
        activites=Activities.objects.filter(product_id=Product_id, id__in = l)
        if activites:
                for activite in activites:
                    activite_id= activite.id
                    activite_Name=activite.activity
                    date_debut = activite.date_due_debut
                    date_fin = activite.date_due_fin
                    activete_Bdget = activeteentite_sBudgets(activite_id, projectentitie_id)
                    Budget_activite = activete_Bdget
                    taux_taches= Taux_progression_Activite(activite_id, projectentitie_id)
                    Prog_Activity =0
                    for taux_tache in taux_taches:
                        Progress_Activity= ((taux_tache[3]/Budget_activite)*taux_tache[2])
                        Prog_Activity=Prog_Activity + Progress_Activity
                    Etat_Activite = Evaluation_progression_Activite(activite_id, int(Prog_Activity))
                    l2 =((activite_id, activite_Name, Budget_activite, int(Prog_Activity), date_debut, date_fin, Etat_Activite[1]),)
                    l3= l3 + l2
                return(l3)
        else:
            return(l3)
    else:
        l3=()
        return(l3)


def Taux_progression_Activite_implementation(activite_id):
    proj_entities= ProjectEntities.objects.all()
    l=()
    if proj_entities:
        l3=(("", "", "", ""),)
        for proj_entitie in proj_entities:
            projectentitie_id = proj_entitie.type_id
            projectentitie_Acronim= proj_entitie.name
            activete_Bdget = activeteentite_sBudgets(activite_id, projectentitie_id)
            Budget_activite = activete_Bdget
            taux_taches= Taux_progression_Activite(activite_id, projectentitie_id)
            if taux_taches and Budget_activite !=0:
                Prog_Activity =0
                for taux_tache in taux_taches:
                    Progress_Activity= ((taux_tache[3]/Budget_activite)*taux_tache[2])
                    Prog_Activity=Prog_Activity + Progress_Activity
                Etat_activite = Evaluation_progression_Activite(activite_id, Prog_Activity)
                l3= ((activite_id, projectentitie_Acronim, activete_Bdget, int(Prog_Activity), Etat_activite[1]),)
                l=l+l3
            else:
                if activete_Bdget != 0 :                
                    Prog_Activity = 0
                    Etat_activite = Evaluation_progression_Activite(activite_id, Prog_Activity)
                    l3= ((activite_id, projectentitie_Acronim, activete_Bdget, int(Prog_Activity), Etat_activite[1]),)
                    l=l+l3
                else:
                    activete_Bdget = 0
                    Prog_Activity = 0
        return(l)
    return(l)

#Calcul du taux de progression de chaque tache de lactivité par entité (taux_prog_tache_activité =((taux_prog_tache_i), (taux_prog_tache_i+1), ...)

def Taux_progression_Activite(activite_id, projectentitie_id):
    responsables= Responsibles.objects.filter(project_entity_id=projectentitie_id)
    if responsables:
        l1=( )
        l5=("",)
        for responsable in responsables:
            responsable_id = responsable.id
            if responsable_id in l1:
                l5=()
            else:
                l5=(responsable_id,)
            l1=l1+l5
    else:
        l1()
    if l1:
        l3=()
        taches= Tasks.objects.filter(activity_id = activite_id, responsible_id__in = l1)
        if taches:
            l=()
            l4=("",)
            l3=()
            l2=(("", "", "", "", ""),)
            for tache in taches:
                id_tache= tache.id
                tache_name = tache.task
                if id_tache in l:
                    l4=()
                else: 
                    l4= (id_tache,)
                l = l + l4
        else:
            l=()
    else:
        l=()
    if l :
        for k in l:
            prog_tache = Taux_progression_Tache(k)
            if prog_tache is not None:
                prog_tache = int(prog_tache)
            else:
                prog_tache =0
            Task_2 = taches.get(id = k)
            tache_name = Task_2.task
            budget_tache= Task_2.budget
            etat_tache = Evaluation_progression_tache(k)
            l2 = ((k, tache_name, prog_tache, budget_tache, etat_tache[1]),)
            l3=l3 +l2
        return(l3)
    return(l3)

def Evaluation_progression_tache(tache_id):
    prog_tache= int(Taux_progression_Tache(tache_id))
    tache=Tasks.objects.get(id=tache_id)
    duree_tache = ((tache.date_due_fin) - (tache.date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (tache.date_due_debut)).days
    duree_consommee_duree= int((duree_consommee/duree_tache)*100)
    if prog_tache < 100:
        if duree_consommee_duree >100:
            depassement = duree_consommee
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_duree
        if prog_duree < 100:
            decalage = prog_tache - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_tache - prog_duree) < -5 and (prog_tache - prog_duree) > -15:
                
                etat = "risque de retard"
            elif (prog_tache - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement)
    else:
        if duree_consommee_duree <100:
            depassement = 0
            prog_duree = duree_consommee_duree
            etat = "tache cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "tache cloturée"

        return(prog_duree, etat, depassement)

def Taux_progression_Tache(tache_id):
    # calcul du taux de progression de la tache dont le id = tache_id :(taux_progrssion_ tache = somme((coeffission de pondération)i*(taux_prog_phase)i)
    progress= Progressions.objects.filter(task_id=tache_id)
    if progress:
        l=()
        l4=("",)
        for phase in progress:
            id_phase= phase.phase_id
            if id_phase in l:
                l4=()
            else: 
                l4= (id_phase,)
            l = l + l4
    else:
        l=()
    l2=(2, 10, 10, 5, 3, 40, 10, 10, 5, 5)
    tau_prog_tache=0
    if l :
        for i in l:
            progess_rate_precied = None
            progress1= progress.filter(phase_id=i)
            if progress1:
                for prog in progress1:
                    if progess_rate_precied != None:
                            if progess_rate_precied < prog.progess_rate:
                                progess_rate_precied = prog.progess_rate
                            else:
                                progess_rate_precied = progess_rate_precied
                    else:
                        progess_rate_precied = prog.progess_rate
                tau_prog_phase = progess_rate_precied *l2[i-1]/100
                tau_prog_tache = tau_prog_tache + tau_prog_phase
    else:
        tau_prog_tache=0
    return(tau_prog_tache)

def Evaluation_progression_Activite(activte_id, prog_activite):
    activite=Activities.objects.get(id=activte_id)
    duree_activite = ((activite.date_due_fin) - (activite.date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (activite.date_due_debut)).days
    duree_consommee_PourCent= int((duree_consommee/duree_activite)*100)
    if prog_activite < 100:
        if duree_consommee_PourCent >100:
            depassement = ((datetime.datetime.now().date()) - (activite.date_due_fin)).days
            prog_duree = 100
        else:
            depassement = 0
            prog_duree = duree_consommee_PourCent
        if prog_duree < 100:
            decalage = prog_activite - prog_duree
            if decalage < -5 and decalage > -15 :
                etat = "risque de retard"
            elif decalage <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        else:
            if (prog_activite - prog_duree) < -5 and (prog_activite - prog_duree) > -15:
                
                etat = "risque de retard"
            elif (prog_activite - prog_duree) <= -15 :
                etat = "en retard"
            else:
                etat = "pas de retard"
        return(prog_duree, etat, depassement)
    else:
        if duree_consommee_PourCent <100:
            depassement = 0
            prog_duree = duree_consommee_PourCent
            etat = "Activité cloturée"
        else:
            depassement = 0
            prog_duree = 100
            etat = "Activité cloturée"

    return(prog_duree, etat, depassement)

class ActivityDetailView(LoginRequiredMixin, generic.DetailView):

    model = Activities
    template_name = 'tache/activity_detail.html'

    def dispatch(self, request, *args, **kwargs):
        global curant_username
        global curant_entitie
        global projectentitie_name
        global Budget_activite
        global projectentitie_id
        global entitie_id
        global Budget_Actites
        global responsable_id

        if request.user.is_authenticated:
            curant_username = request.user.get_username()
            #recuperation de l'entité de l'utilisateur
            user_entite = projectEntiteAccronima(curant_username)
            entitie_id = user_entite[1]
            curant_entitie = user_entite[0]
            projectentitie_id = user_entite[2]
            responsable_id = user_entite[3]
            #recuperation de id de l'activité concernée
            activite_id = str(self.kwargs.get('pk'))
            #Product_id
            product = activitiesproduct_id(activite_id)
            product_id = product
            #Result_id
            Result = productsResult_id(product_id)
            Result_id = Result
            #Composante_id
            Components= resultsComponents_id(Result_id)
            Components_id = Components
            # prject id
            project = componentsProjects_id(Components_id)
            Projects_id = project
            # projectentite
            projentite =projectEntities(projectentitie_id)
            projectentitie_name = projentite
            if projectentitie_id !=5:
                # Budget de avtivite
                activete_Bdget = activeteentite_sBudgets(activite_id, projectentitie_id)
                Budget_activite = activete_Bdget
            else:
                Budget_Actites =ActivitesBudgetOss_entites(activite_id, Projects_id)
                ativite = Activities.objects.get(id = activite_id)
                if Budget_Actites is None:
                    Budget_activite = 0
                else:                            
                    Budget_activite = ativite.budget
                #activete_Bdget = activeteentite_sBudgetsOss(activite_id)
                #Budget_activite = activete_Bdget  
          
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        activite_id = str(self.kwargs.get('pk'))
        if projectentitie_id !=5:
            # calcul du taux de progression de chaque tache de l'activité (taux_taches = Taux_progression_Activite(activite_id, projectentitie_id))
            taux_activites = Taux_progression_Activite(activite_id, projectentitie_id)
            Prog_Activity =0
            # calcul du taux de progression de l'activité  par entité (Prog_Activity)
            if taux_activites:
                for taux_activite in taux_activites:
                    Progress_Activity= ((taux_activite[3]/Budget_activite)*taux_activite[2])
                    Prog_Activity=Prog_Activity + Progress_Activity
                duree_activite =Evaluation_progression_Activite(activite_id, Prog_Activity)
                Etat=duree_activite[1]
                prog_duree=duree_activite[0]
                depassement = duree_activite[2]
            else:
                Prog_Activity =0
                duree_activite =Evaluation_progression_Activite(activite_id, Prog_Activity)
                Etat=duree_activite[1]
                prog_duree=duree_activite[0]
                depassement = duree_activite[2]
        else:
             # calcul du taux de progression de chaque tache de l'activité  par entité (taux_Activites_impl = Taux_progression_Activite_implementation(activite_id))
            taux_Activites_impl = Taux_progression_Activite_implementation(activite_id)
            Prog_Activity_impl=0
            # calcul du taux de progression global de l'activité (Prog_Activity_impl)
            if   taux_Activites_impl :  
                for taux_Activite_impl in taux_Activites_impl:
                    Progress_Activity= ((taux_Activite_impl[2]/Budget_activite)*taux_Activite_impl[3])
                    Prog_Activity_impl=Prog_Activity_impl + Progress_Activity
                duree_activite =Evaluation_progression_Activite(activite_id, Prog_Activity_impl)
                Etat=duree_activite[1]
                prog_duree=duree_activite[0]
                depassement = duree_activite[2]
            else:
                Prog_Activity_impl =0
                duree_activite =Evaluation_progression_Activite(activite_id, Prog_Activity_impl)
                Etat=duree_activite[1]
                prog_duree=duree_activite[0]
                depassement = duree_activite[2]
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project, tache_components.id AS component_id, tache_components.component, tache_results.id AS result_id, tache_results.result, tache_products.id AS product_id, tache_products.product FROM tache_activities INNER JOIN (tache_products INNER JOIN (tache_results INNER JOIN (tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id) ON tache_results.component_id = tache_components.id) ON tache_products.result_id = tache_results.id) ON tache_activities.product_id = tache_products.id WHERE (((tache_activities.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        if projectentitie_id !=5:
            # Recuperation des budgets reservés, engagés, consomés et restant cocernant l'activité en cour (une fonction())
            fonction1=activiteBedgetReserveEngage(activite_id, projectentitie_id, Budget_activite)
            budget_reserve = fonction1[0]
            budget_engage = fonction1[1]
            budget_consome = fonction1[2]
            budget_restant = fonction1[3]
            data1 = fonction1[4]
            labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
            data=[int(budget_reserve), int(budget_engage), int(budget_consome), int(budget_restant)]
            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant 
            context['Role_Entite'] = projectentitie_name
            context['Entite'] = curant_entitie
            context['taches']= data1
            context['parent'] = dictfetchall(cursor)
            context['Budget']= Budget_activite
            context['entitie_id']=projectentitie_id
            context["prog_tache"]= taux_activites
            context["prog_activite"] = int(Prog_Activity)
            context['data']= data
            context['labels']= labels
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement
        else:
            # Recuperation des budgets reservés, engagés, consomés et restant cocernant l'activité en cour (une fonction())
            fonction1=activiteBedgetReserveEngageOss(activite_id, Budget_activite)
            budget_reserve = fonction1[0]
            budget_engage = fonction1[1]
            budget_consome = fonction1[2]
            budget_restant = Budget_activite- (budget_reserve + budget_engage + budget_consome)
            data1 = fonction1[4]
            for Budget_Act in Budget_Actites:
                    if Budget_Act[0]=="Total":
                        labels=['Budget réservé', 'Budget engagé', 'Budget consommé', 'Budget restant']
                        data=[int(Budget_Act[2]), int(Budget_Act[3]), int(Budget_Act[4]), int(Budget_Act[5])]

            context['budget_reserve'] = budget_reserve
            context['budget_engage'] = budget_engage
            context['budget_consome'] = budget_consome
            context['budget_restant'] = budget_restant 
            context['taches']= data1
            context['parent'] = dictfetchall(cursor)
            context['Budget']= Budget_activite
            context['entitie_id']=projectentitie_id
            context['Budget_Actites']=Budget_Actites
            context["prog_tache"]=taux_Activites_impl
            context["prog_activite"] = int(Prog_Activity_impl)
            context['data']= data
            context['labels']= labels
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement
            context["Etat"] = Etat
            context["prog_duree"] = prog_duree
            context["depassement"] = depassement
        return context


class ActivityAddView(LoginRequiredMixin, generic.CreateView):
    model = Activities
    form_class = ActivityForm
    template_name = 'tache/activity_add.html'

    def get_success_url(self):
        return reverse_lazy('tache:product-detail', kwargs={'pk': self.kwargs['product_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        product_id = self.kwargs['product_id']
        product = Products.objects.get(id=product_id)
        context['product'] = product
        return context

class ActivityUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Activities
    form_class = ActivityForm
    template_name = 'tache/activity_update.html'

    def get_success_url(self):
        return reverse_lazy('tache:product-detail', kwargs={'pk': self.kwargs['product_id']})

class ActivityDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Activities
    # form_class = ActivityForm
    fields = '__all__'
    template_name = 'tache/activity_delete.html'

    def get_success_url(self):
        return reverse_lazy('tache:product-detail', kwargs={'pk': self.kwargs['product_id']})

# Tasks _________________________________________________________
# progression par phse pour chaque tache
def prog_Phases(task_id):
    progress_phases= Progressions.objects.filter(task_id=task_id)
    l=()
    l2=(('','','','',''),)
    if progress_phases:
        for progress_phase in progress_phases:
            phase_id= progress_phase.phase_id
            phase_name=Phases.objects.get(id=phase_id).phase
            l2=((progress_phase.id, progress_phase.phase_id, phase_name, progress_phase.progess_rate, progress_phase.date_record ),)
            l=l+l2
    else:
        l=l
    return(l)

# Envoi de message concernant le risque de retard des travaux de la tache


def notif_precedante(tache_id):
    totifications =Notification.objects.filter(task=tache_id)
    mail=0
    if totifications :
        duree=0
        for totification in totifications:
            notif_date= totification.notif_date
            notif_type= totification.notif_type
            duree_notif = ((datetime.datetime.now().date()) - (notif_date)).days
            if duree_notif > duree and notif_type == "Alerte risque de retard":
                duree = duree_notif
            else:
                duree = duree
        if duree > 7 :
            mail = 1
            print("duree _1 ==== ", mail)
            return mail
        else:
            mail = 0
            print("duree _0 ==== ", mail)
            return mail
    else:
        mail = 1
        print("duree _01 ==== ", mail)
        return mail




class TasksListView(LoginRequiredMixin, generic.ListView):
    model = Tasks
    template_name = 'tache/tasks_list.html'

class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Tasks
    template_name = 'tache/task_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        Task_id = self.kwargs['pk']
        # calcul du taux de progression de la tache ( taux_tache= Taux_progression_Tache(Task_id))
        taux_tache= Taux_progression_Tache(Task_id)
        
        
        duree_tache =Evaluation_progression_tache(Task_id)
        Etat=duree_tache[1]
        prog_duree=duree_tache[0]
        depassement = duree_tache[2]
        if taux_tache is None:
            taux_tache =0
        else:
            taux_tache = int(taux_tache)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project, tache_components.id AS component_id, tache_components.component, tache_results.id AS result_id, tache_results.result, tache_products.id AS product_id, tache_products.product, tache_activities.id AS activity_id, tache_activities.activity FROM tache_tasks INNER JOIN (tache_activities INNER JOIN (tache_products INNER JOIN (tache_results INNER JOIN (tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id) ON tache_results.component_id = tache_components.id) ON tache_products.result_id = tache_results.id) ON tache_activities.product_id = tache_products.id) ON tache_tasks.activity_id = tache_activities.id WHERE (((tache_tasks.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        # progression de chaque phase de la tache ( l=prog_Phases(Task_id))
        l=prog_Phases(Task_id)                     
        context['parent'] = dictfetchall(cursor)
        context['progression'] = l
        context["tache"] = taux_tache
        context["Etat"] = Etat
        context["prog_duree"] = prog_duree
        context["depassement"] = depassement
        return context


class TaskAddView(LoginRequiredMixin, generic.CreateView):
    model = Tasks
    form_class = TaskForm
    template_name = 'tache/task_add.html'
    # fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:activity-detail', kwargs={'pk': self.kwargs['activity_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        activity_id = self.kwargs['activity_id']
        activity = Activities.objects.get(id=activity_id)
        context['activity'] = activity
        return context


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Tasks
    form_class = TaskForm
    template_name = 'tache/task_update.html'

    def get_success_url(self):
        return reverse_lazy('tache:activity-detail', kwargs={'pk': self.kwargs['activity_id']})

class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tasks
    template_name = 'tache/task_delete.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:activity-detail', kwargs={'pk': self.kwargs['activity_id']})

# Progressions _________________________________________________________

class ProgressionsListView(LoginRequiredMixin, generic.ListView):
    model = Progressions
    template_name = 'tache/progressions_list.html'

class ProgressionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Progressions
    template_name = 'tache/progression_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        cursor = connection.cursor()
        requete = "SELECT tache_axes.id AS axe_id, tache_axes.name AS axe, tache_projects.id AS project_id, tache_projects.acronym AS project, tache_components.id AS component_id, tache_components.component, tache_results.id AS result_id, tache_results.result, tache_products.id AS product_id, tache_products.product, tache_activities.id AS activity_id, tache_activities.activity, tache_tasks.id AS task_id, tache_tasks.task FROM tache_progressions INNER JOIN (tache_tasks INNER JOIN (tache_activities INNER JOIN (tache_products INNER JOIN (tache_results INNER JOIN (tache_components INNER JOIN (tache_projects INNER JOIN tache_axes ON tache_projects.axe_id = tache_axes.id) ON tache_components.project_id = tache_projects.id) ON tache_results.component_id = tache_components.id) ON tache_products.result_id = tache_results.id) ON tache_activities.product_id = tache_products.id) ON tache_tasks.activity_id = tache_activities.id) ON tache_progressions.task_id = tache_tasks.id WHERE (((tache_progressions.id)=" + str(self.kwargs.get('pk')) + "));"
        cursor.execute(requete,)
        context['parent'] = dictfetchall(cursor)
        return context


class ProgressionAddView(LoginRequiredMixin, generic.CreateView):
    model = Progressions
    form_class = ProgressionForm
    template_name = 'tache/progression_add.html'

    def get_success_url(self):
        return reverse_lazy('tache:task-detail', kwargs={'pk': self.kwargs['task_id']})
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        task = Tasks.objects.get(id=task_id)
        context['t_id'] = task
        return context


class ProgressionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Progressions
    form_class = ProgressionForm
    template_name = 'tache/progression_update.html'

    def get_success_url(self):
        return reverse_lazy('tache:task-detail', kwargs={'pk': self.kwargs['task_id']})


class ProgressionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Progressions
    template_name = 'tache/progression_delete.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy('tache:task-detail', kwargs={'pk': self.kwargs['task_id']})


# Phone_numbers _________________________________________________________

class PhonenumbersListView(LoginRequiredMixin, generic.ListView):
    model = Phone_numbers
    template_name = 'tache/phone_numbers_list.html'

class PhonenumberDetailView(LoginRequiredMixin, generic.DetailView):
    model = Phone_numbers
    template_name = 'tache/phone_number_detail.html'

class PhonenumberAddView(LoginRequiredMixin, generic.CreateView):
    model = Phone_numbers
    # form_class = ProjetForm
    template_name = 'tache/phone_number_add.html'
    fields = '__all__'

class PhonenumberUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Phone_numbers
    # form_class = ProjetForm
    template_name = 'tache/phone_number_update.html'
    fields = '__all__'

class PhonenumberDeleteView(LoginRequiredMixin,generic.DeleteView):
    model = Phone_numbers
    # form_class = ProjetForm
    template_name = 'tache/phone_number_delete.html'
    fields = '__all__'
    success_url = reverse_lazy('tache:phone_numbers-list')

class AoiListView(LoginRequiredMixin,generic.ListView):
    model = Aoi
    template_name = 'tache/aoi_list.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        smjson0 = serialize('geojson', PopulatedPlaces.objects.all(), geometry_field='geom', fields=('name',))
        context['pp'] = smjson0
        smjson1 = serialize('geojson', Aoi.objects.all(), geometry_field='geom', fields=('name',))
        context['aoi'] = smjson1
        return context


class AoipopupListView(LoginRequiredMixin,generic.ListView):
    model = Aoi
    template_name = 'tache/aoipopup_list.html'
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        smjson0 = serialize('geojson', PopulatedPlaces.objects.all(), geometry_field='geom', fields=('name',))
        context['pp'] = smjson0
        smjson1 = serialize('geojson', Aoi.objects.all(), geometry_field='geom', fields=('name',))
        context['aoi'] = smjson1
        return context

class WorldView(LoginRequiredMixin,generic.ListView):
    model = PopulatedPlaces
    # form_class = WorldBorderForm
    template_name = 'tache/world.html'
    # context_object_name = 'world_map'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        smjson = serialize('geojson', Aoi.objects.all(), geometry_field='geom', fields=('name',))
        context['ppgeojson'] = smjson
        return context
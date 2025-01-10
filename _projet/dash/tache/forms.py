from audioop import add
from dataclasses import fields
from turtle import textinput
from unittest import case
from django import forms
from .models import *
from django.contrib.gis import forms as geofroms
from datetime import datetime
from django.db import connection
from collections import namedtuple
from bootstrap_datepicker_plus.widgets import DatePickerInput
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
import datetime 


class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)


def activitiesproduct_id(activite_id):
    # recuperation de id product auquelle appartien l'activité en question
    activities = Activities.objects.filter(id=activite_id)
    for activitie in activities:
        product_id = activitie.product_id

    return(product_id)

def productsResult_id(product_id):
    # recuperation de id Result auquelle appartien le Prodact en question
    products = Products.objects.filter(id=product_id)
    for product in products:
        Result_id = product.result_id
    print('Result_id = ',Result_id )
    return(Result_id)

def resultsComponents_id(Result_id):
    # recuperation de id composante auquelle appartien le Result en question
    results = Results.objects.filter(id=Result_id)
    for result in results:
        Components_id = result.component_id
    print('Components_id = ',Components_id )
    return(Components_id)

#def projectEntities(entitie_id, Projects_id):
    # recuperation de id projectEntitie auquelle appartien l'entité et le projet en question
#    projectEntities = ProjectEntities.objects.filter(entity_id = entitie_id, project_id= Projects_id)
#    if projectEntities:
#        for projectEntitie in projectEntities:
#            projectentitie_id = projectEntitie.id
#            projectentitie_name = projectEntitie.name
#    else:
#        projectentitie_id = None
#        projectentitie_name = None
#    return(projectentitie_id, projectentitie_name )

def activeteentite_sBudgets(activite_id, projectentitie_id):

    activentitiesBudgets = ActivitiesEntitiesBudget.objects.filter(activity_id=activite_id, project_entity_id = projectentitie_id)
    if activentitiesBudgets :

        for activentitiesBudget in activentitiesBudgets:
            Budget_activite = activentitiesBudget.Budget
    else:
            Budget_activite =0   
    return(Budget_activite)

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields=('reference_code', 'acronym','name','objective','background_context','funder','budget','date_debut','date_debut_execution','date_closing','date_final_evaluation','axe')
        widgets = {
            'reference_code' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reference code ...'}),
            'acronym' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Acronym ...'}),
            'name' : forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name ...'}),
            'objective' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Objective ...'}),
            'background_context' : forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Background and context ...'}),
            #'project_manager' : forms.Select(),
            # 'executing_entity' : forms.SelectMultiple(),
            'funder' : forms.Select(),
            'budget' : forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'date_debut' : forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Beginng date ...'}),
            'date_debut_execution' : forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Execution Beginng date ...'}),
            'date_closing' : forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Closing date ...'}),
            'date_final_evaluation' : forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Final evaluation date ...'}),
            'axe' : forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_axe', 'type': 'hidden'}),
        }
    

class ComponentForm(forms.ModelForm):
    class Meta:
        model = Components
        fields=('component', 'description', 'budget', 'project')
        widgets = {
            'component': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description ...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_project', 'type': 'hidden'}),
        }


class ResultForm(forms.ModelForm):
    class Meta:
        model = Results
        fields=('result', 'description', 'budget', 'component')
        widgets = {
            'result': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description ...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'component': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_component', 'type': 'hidden'}),
        }
    def clean(self, *args, **kwargs):
        
        global component_c
        global budget_c 
        global result_c 
        
        cleaned_data = super().clean()
        # Récuperation des valeures des champs du formulaire
        
        result_c = cleaned_data.get('result')
        budget_c = cleaned_data.get('budget')
        component_c = cleaned_data.get('component')        

        print('component_c : ', component_c)
        print('budget_c : ', budget_c)
        print('result_c : ', result_c)

        requeste1 = Components.objects.filter(component = component_c)
        if requeste1:
            component_budget = 0
            for component in requeste1:
                component_budget = component_budget + component.budget
                component_id_c = component.id
        
            requeste2 = Results.objects.filter(component_id = component_id_c)
            if requeste2:
                Results_budget = 0
                for result in requeste2:
                    Results_budget = Results_budget + result.budget
                budget_result_restant = component_budget - Results_budget
                print('budget_result_restant = ', budget_result_restant)
                if budget_c > budget_result_restant:
                    msg = "le budget introduit (" + str(budget_c) + ") est superieur au budget restat (" + str(budget_result_restant) + ") !"
                    self.errors["budget"] = self.error_class([msg])

   
        return cleaned_data

class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields=('product', 'description', 'budget', 'result')
        widgets = {
            'product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description ...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'result': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_result', 'type': 'hidden'}),
        }
    def clean(self, *args, **kwargs):
        
        global product_c
        global budget_c 
        global result_c 
        
        cleaned_data = super().clean()
        # Récuperation des valeures des champs du formulaire
        
        product_c = cleaned_data.get('product')
        budget_c = cleaned_data.get('budget')
        result_c = cleaned_data.get('result')        

        print('product_c : ', product_c)
        print('budget_c : ', budget_c)
        print('result_c : ', result_c)

        requeste1 = Results.objects.filter(result = result_c)
        if requeste1:
            Results_budget = 0
            for result in requeste1:
                Results_budget = Results_budget + result.budget
                result_id_c = result.id
        
            requeste2 = Products.objects.filter(result_id = result_id_c)
            if requeste2:
                Products_budget = 0
                for Product in requeste2:
                    Products_budget = Products_budget + Product.budget
                budget_Product_restant = Results_budget - Products_budget
                print('budget_Product_restant = ', budget_Product_restant)
                if budget_c > budget_Product_restant:
                    msg = "le budget introduit (" + str(budget_c) + ") est superieur au budget restat (" + str(budget_Product_restant) + ") !"
                    self.errors["budget"] = self.error_class([msg])

   
        return cleaned_data

class ActivityForm(forms.ModelForm):
    class Meta:
        model =Activities
        fields=('activity', 'description', 'budget', 'product', 'date_due_debut', 'date_due_fin', 'date_due_delivery')
        widgets = {
            'activity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Activity ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description ...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'product': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_product', 'type': 'hidden'}),
            'date_due_debut':DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ),
            'date_due_fin':DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ),
            'date_due_delivery':DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ),
        } 
    

    def clean(self, *args, **kwargs):
        
        global activity_c
        global budget_c 
        global date_due_debut_c 
        global date_due_fin_c
        global date_due_delivery_c
        global product_id_c
        global activity_c
        global activitys_budget
        
        cleaned_data = super().clean()
        # Récuperation des valeures des champs du formulaire
        
        activity_c = cleaned_data.get('activity')
        budget_c = cleaned_data.get('budget')
        date_due_debut_c = cleaned_data.get('date_due_debut')        
        date_due_fin_c = cleaned_data.get('date_due_fin')
        date_due_delivery_c = cleaned_data.get('date_due_delivery')
        product_c = cleaned_data.get('product')

        print('activity_c : ', activity_c)
        print('budget_c : ', budget_c)
        print('date_due_debut_c : ', date_due_debut_c)
        print('date_due_fin_c : ', date_due_fin_c)
        print('date_due_delivery_c : ', date_due_delivery_c)
        print('product_c : ', product_c)

        requeste1 = Products.objects.filter(product = product_c)
        if requeste1:
            product_budget = 0
            for product in requeste1:
                product_budget = product_budget + product.budget
                product_id_c = product.id
        
            requeste2 = Activities.objects.filter(product_id = product_id_c)
            if requeste2:
                activitys_budget = 0
                for activity in requeste2:
                    activitys_budget = activitys_budget + activity.budget
                budget_activitys_restant = product_budget - activitys_budget
                print('budget_activitys_restant = ', budget_activitys_restant)
                if budget_c > budget_activitys_restant:
                    msg = "le budget introduit (" + str(budget_c) + ") est superieur au budget restat (" + str(budget_activitys_restant) + ") !"
                    self.errors["budget"] = self.error_class([msg])
                    
            if date_due_debut_c > date_due_fin_c:
                msg = "la date fin (" + str(date_due_fin_c) + ") de l'actvite est inferieure a la date debut (" + str(date_due_debut_c) + ") !"
                self.errors["date_due_fin"] = self.error_class([msg])
   
        return cleaned_data


class TaskForm(forms.ModelForm):
    global Budget_activite
    class Meta:
        model =Tasks
        fields=('id', 'task', 'responsible', 'objective', 'description', 'budget', 'date_due_debut', 'date_due_fin', 'activity')
        widgets = {
            'id': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_activity', 'type': 'hidden'}),
            'task': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Task ...'}),
            'responsible': forms.Select(),
            'objective': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objective ...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Description ...'}),
            'budget': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Budget ...'}),
            'date_due_debut':DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ),
            'date_due_fin':DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ),

            'activity': forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_activity', 'type': 'hidden'}),
        }

    def clean(self, *args, **kwargs):

        global task_c
        global task_id_c 
        global responsible_c 
        global budget_c
        global date_due_debut_c
        global date_due_fin_c
        global activity_c
        global tasts_budget
        global date_due_delivery
        global Budget_activite


        cleaned_data = super().clean()
        # Récuperation des valeures des champs du formulaire
        
        task_id = cleaned_data.get('id')
        task_c = cleaned_data.get('task')
        responsible_c = cleaned_data.get('responsible')
        budget_c = cleaned_data.get('budget')        
        date_due_debut_c = cleaned_data.get('date_due_debut')
        date_due_fin_c = cleaned_data.get('date_due_fin')
        activity_c = cleaned_data.get('activity')
        responsible = str(responsible_c).split()
        responsible_first_name = responsible[1]
        responsible_last_name = responsible[2]
        print('task_c = ',task_c)
        print("date_due_debut_c = ", date_due_debut_c)
        print("date_due_fin_c = ", date_due_fin_c)
        requeste1 = Activities.objects.filter(activity = activity_c)
        if requeste1 :
            #budget_activit = Budget_activite
            for Act in requeste1:
                budget = Act.budget
                date_due_debut = Act.date_due_debut
                date_due_fin = Act.date_due_fin
                date_due_delivery = Act.date_due_delivery
                activity_id_c = Act.id

            requeste3 = Responsibles.objects.filter(first_name = responsible_first_name, last_name = responsible_last_name)
            if requeste3:
                for responsabl in requeste3:
                    ProjectEntite = responsabl.project_entity_id
                    requeste4 = ActivitiesEntitiesBudget.objects.filter(project_entity_id = ProjectEntite, activity_id = activity_id_c)
                    if requeste4 :
                        for ActivitieEntitieBudget in requeste4:
                            budget_avtivite_Entite = ActivitieEntitieBudget.Budget
                    else:
                        requeste4 = None
            else:
                requeste3 = None
                # recuperation des responsables de l'entite en question
            reponsables_id = Responsibles.objects.filter(project_entity_id=ProjectEntite)
            if reponsables_id:
                id_responsables=()
                for reponsable_id in reponsables_id:
                    id_responsables = id_responsables+ (reponsable_id.id,) 
            else:
                id_responsables=()
             # test sur les dates de l'activite   
            if date_due_debut_c > date_due_fin_c:

                msg = "la date de fin de la tache (" + str(date_due_fin_c) + ") est ulterieure a la date de debut de la tache (" + str(date_due_debut_c) + ") . verifier les dates debut et fin de la tache."
                self.errors["date_due_fin"] = self.error_class([msg])
            if date_due_debut_c < date_due_debut or date_due_fin < date_due_debut_c:
                msg = "la date de debut (" + str(date_due_debut_c) + ") de la tache (" + str(task_c) + ") n est pas dans la plage d execution du : " + str( date_due_debut) + " au : " + str(date_due_fin ) + "de l activité  (" + str(activity_c) + ") . verifier date debut de la tache."
                self.errors["date_due_debut"] = self.error_class([msg])
            if date_due_fin_c < date_due_debut or date_due_fin < date_due_fin_c:
                msg = "la date de fin (" + str(date_due_fin_c) + ") de la tache (" + str(task_c) + ") n est pas dans la plage d execution du : " + str( date_due_debut) + " au : " + str(date_due_fin ) + "de l activité  (" + str(activity_c) + ") . verifier date fin de la tache."
                self.errors["date_due_debut"] = self.error_class([msg])
        #recperation des taches de l'activité en question de l'entité concernée et test sur le budget de cette dernière
        requeste2 = Tasks.objects.filter(activity_id = activity_id_c, responsible_id__in = id_responsables, )
        if requeste2:
            if requeste2 :
                tasts_budget = 0
                for task in requeste2:
                    task_task = task.task
                    if task_task != task_c:
                        tasts_budget = tasts_budget + task.budget
                    tasts_budget_t = tasts_budget + budget_c
                    if tasts_budget_t > budget_avtivite_Entite :
                        budget_a_consomer = budget_avtivite_Entite - tasts_budget
                        msg = "le budget : (" + str(budget_c) + ") concernant la tache (" + str(task_c) + ") depasse le budget a consomer (" + str( budget_a_consomer) + " concernant l activite  : (" + str(activity_c) + ")."
                        self.errors["date_due_debut"] = self.error_class([msg])
        elif budget_c > budget_avtivite_Entite:
            msg = "le budget : (" + str(budget_c) + ") concernant la tache (" + str(task_c) + ") depasse le budget de l'activité (" + str( budget_avtivite_Entite) + " : (" + str(activity_c) + ")."
            self.errors["date_due_debut"] = self.error_class([msg])
        return cleaned_data


# recupération de la phase precedente
def PhasePrecedf(string1):
    print('string1 is :', string1)
    if string1 == 'Tor drafting':
        phasePreced = 'To do'
        return 'To do'       
    if string1 == 'Tender':
        phasePreced = 'Tor drafting'
        return 'Tor drafting'
    if string1 == 'Proposals examination':
        phasePreced = 'Tender'
        return 'Tender'        
    if string1 == 'contract signature':
        phasePreced = 'Proposals examination'
        return 'Proposals examination'        
    if string1 == 'Progress rate (%)':
        phasePreced = 'contract signature'
        return 'contract signature'        
    if string1 == 'Report':
        phasePreced = 'Progress rate (%)'
        return 'Progress rate (%)'       
    if string1 == 'Validation':
        phasePreced = 'Report'
        return 'Report'       
    if string1 == 'Payement':
        phasePreced = 'Validation'
        return 'Validation'        
    if string1 == 'Done':
        phasePreced = 'Payement'
        return 'Payement'
def Phase(task_id, phase_id):
        progress= Progressions.objects.filter(task_id = task_id, phase_id = phase_id)
        prog_ra=0
        if progress :        
            for progres in progress:
                progression =progres.progess_rate
                if progression == 100:
                    prog_ra =100
                    return(prog_ra)
                else: 
                    prog_ra = progression
        return(prog_ra)


#class TaskPhaseForm(forms.ModelForm):
#    class Meta:
#        model = TaskPhase
#        fields=('phase', 'phases')
#        widgets = {
#            'phase': forms.Select(attrs={'class': 'form-control'}),
#            'phases': forms.MultiValueField(attrs={'class': 'form-control'}),
#        }


class ProgressionForm(forms.ModelForm):
      
    class Meta:
        model =Progressions
        fields=('phase', 'progess_rate', 'date_record', 'task')
        widgets = {
            'phase': forms.Select(attrs={'class': 'form-control'}),
            'progess_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_record': DatePickerInput( 
                options={
                    "format": "DD/MM/YYYY", # moment date-time format
                    "showClose": True,
                    "showClear": True,
                    "showTodayButton": True,
                }
            ), 
            'task' : forms.TextInput(attrs={'class': 'form-control', 'value': '' , 'id' : 'input_tache', 'type': 'hidden'}),
        }

    def clean(self, *args, **kwargs):
        global date_record_c
        global progess_rate
        global phase_c
        global task_c
        global task_id_c 
        global phase_id_c 
        global task_c
        
        cleaned_data = super().clean()
        # Récuperation des valeures des champs du formulaire
        progess_rate = cleaned_data.get('progess_rate')
        phase_c = cleaned_data.get('phase')        
        task_c = cleaned_data.get('task')
        date_record_c = cleaned_data.get('date_record')
        
        if phase_c is not None:
            if date_record_c is not None:
                if progess_rate is not None:

                    # Récuperation de id de la tache en questio (task)
                    requete1 = Tasks.objects.get(task = task_c)
                    #for e in requete1:
                    task_id_c = requete1.id
                    task = requete1.task
                    date_debu = requete1.date_due_debut
                    date_fin = requete1.date_due_fin
                    requete2 = Phases.objects.get(phase = phase_c)
                    phase_id_c = requete2.id
                    # récupération des id des progressions de la tache (task) concernées par des progression
                    requete3 = Progressions.objects.filter(task_id = task_id_c)
                    progQuery = requete3
                    progQuery2 = requete3
                    # vérification si la phase en question est déja incrite et récuperation de sa progression 
                    prog_phase =Phase(task_id_c, phase_id_c)
                    if prog_phase == 100.0:
                        msg = "la phase  (" + str(phase_c) + ") est déja inscrite dans la base de données avec une progression de (" + str(prog_phase) + "%)" 
                        self.errors["phase"] = self.error_class([msg])
                    if str(phase_c) == 'To do'  :
                        progess_Phase_query = progQuery.filter(phase_id = phase_id_c)
                        if progess_Phase_query:
                            print("phase_id_c = ", phase_id_c)
                            for progess_Phase in progess_Phase_query:
                                progess = progess_Phase.progess_rate
                                print("progress = ", progess)
                                if int(progess) == 100.0 :
                                    msg = "la phase  (" + str(phase_c) + ") est déja inscrite dans la base de données avec une progression de (" + str(progess) + "%)" 
                                    self.errors["phase"] = self.error_class([msg])
                    # vérification des contraintes de la phase objet de la mise à jour
                    else :
                        if progQuery :
                            phasePrecedente = PhasePrecedf(str(phase_c))       
                            i = 1
                            b = 0
                            for phase in progQuery:
                                print('boucle i : ', i)
                                if phase_id_c == phase.phase_id:
                                    b = 1
                                    break
                                else:
                                    i = i+1                       
                            j = 1
                            for phase2 in progQuery2:
                                print('j = ', j, ' : i = ', i)
                                if str(phasePrecedente) ==  str(phase2.phase) :
                                    print('phasePrecedente = ', phasePrecedente, ' : phase2.phase = ', phase2.phase)
                                    break
                                if j == (i - 1) and b == 0 :
                                    print('phasePrecedente = ', phasePrecedente, ' : phase2.phase = ', phase2.phase)
                                    msg = "la phase precedente (" + str(phasePrecedente) + ") a la phase en question (" + str(phase_c) + ") n a pas encore ete inscrite dans le suivi de la progression des phases "
                                    self.errors["phase"] = self.error_class([msg])
                                    break
                                j=j +1                

                    progess_rate_query = requete3.filter(phase_id = phase_id_c)
                    if str(phase_c) != 'To do'  :
                        phase = Phases.objects.get(phase = phasePrecedente)
                        if phase:
                            phase_reced_id= phase.id
                            print("phase_reced_id = ", phase_reced_id)

                        progess_reced_query = requete3.filter(phase_id = phase_reced_id)
                        if progess_rate_query :


                            if 0 <= progess_rate <= 100:
                                for progresse in progess_rate_query:                          
                                    if progess_rate < progresse.progess_rate : 
                                        msg = "le taux de progression de la phase introduit (" + str(phase_c) + " est de "+ str(progess_rate) +"% ), il est inferieure a ce lui de la derniere mise a jour ( " + str(progresse.progess_rate) + "% )! verifier le taux de progression introduit "
                                        self.errors["progess_rate"] = self.error_class([msg])  
                            else :
                                    msg = "le taux de progression de la tache introduite doit etre entre 0 et 100! "
                                    self.errors["progess_rate"] = self.error_class([msg])
                            # verification des contraintes date d'enregistrement de progression de la mise à jour de la phase  
                        else:
                            if progess_reced_query:
                                progess_reced_1 = 0.0
                                for Prog_reced in progess_reced_query:
                                    progess_reced = Prog_reced.progess_rate
                                    if progess_reced > progess_reced_1:
                                        progess_reced_1 = progess_reced
                                        print("progess_reced_1 = ", progess_reced_1)
                                if progess_reced_1 < 100:
                                    msg = "Il faut clôturer la phase " + str(phasePrecedente) + " (taux de progression de " + str(progess_reced_1) + ") avant d’inscrire une progression concernant la phase " + str(phase_c) 
                                    self.errors["progess_rate"] = self.error_class([msg])
                        progess_date_query = requete3.filter(phase_id = phase_reced_id)
                        if progess_date_query :
                            for progess_date in progess_date_query:
                                Prog_date_Preced= progess_date.date_record
                                if date_record_c < Prog_date_Preced :
                                            msg = "La date d’enregistrement " + str(date_record_c) + " de la progression  <<" + str(phase_c) +" >> est ultérieure à la date de la progression " + str(Prog_date_Preced) + ",de la phse pécedente"
                                            self.errors["date_record"] = self.error_class([msg]) 
                    # vérification des contraintes de la date de mise à jour de la phase
                    today = datetime.date.today()
                    if date_record_c > today:
                        msg = "La date d’enregistrement de la progression  <<" + str(phase_c) +" >> est dans le futur " + str(date_record_c) + ", vous ne pouvez pas enregistrer une progression avec une date dans le futur." 
                        self.errors["date_record"] = self.error_class([msg])
                    else: 
                        task_date = requete1
                        if task_date:
                                date_debu = task_date.date_due_debut
                                date_fin = task_date.date_due_fin          
                                if date_record_c < date_debu  or date_record_c > date_fin :
                                    msg = "la date de saisie de la progression de la phase <<" + str(phase_c) +" >> : " + str(date_record_c) + " est en dehors de la periode d execution de la tache en question << "+ str(task_c)+ " >>  du : "+ str(date_debu)+ " au : "+ str(date_fin) +" !" 
                                    self.errors["date_record"] = self.error_class([msg])
                                else:
                                    if progess_rate_query :
                                        derniere_date_M_A =  date_debu          
                                        for  date_ul in progess_rate_query:
                                            if date_ul.date_record > derniere_date_M_A :
                                                derniere_date_M_A =  date_ul.date_record
                                        if date_record_c < derniere_date_M_A:
                                                msg = "la date introduite <<" +str(date_record_c) + ">> est ultérieure a la derniere date de mise a jour <<" + str(derniere_date_M_A) + ">> de la progression de la phase <<" + str(phase_c) +">>"
                                                self.errors["date_record"] = self.error_class([msg])

            




        return cleaned_data
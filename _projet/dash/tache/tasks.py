# Create your tasks here
from celery import shared_task
from .models import Tasks, Responsibles, Progressions, Notification
from django.core.mail import send_mail 
import datetime 

def Evaluation_progression_tache(tache_id):
    prog_tache= int(Taux_progression_Tache(tache_id))
    tache=Tasks.objects.get(id=tache_id)
    duree_tache = ((tache.date_due_fin) - (tache.date_due_debut)).days
    duree_consommee= ((datetime.datetime.now().date()) - (tache.date_due_debut)).days
    duree_consommee_duree= int((duree_consommee/duree_tache)*100)
    if prog_tache < 100:
        if duree_consommee_duree >100:
            depassement = ((datetime.datetime.now().date()) - (tache.date_due_fin)).days
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

def notif_precedante(tache_id, etat_tache):
    if etat_tache == "risque de retard":
        type_notif = "Alerte risque de retard"
    elif etat_tache == "en retard":
        type_notif = "Alerte retard enregistré"
    totifications =Notification.objects.filter(task=tache_id, notif_type=type_notif)
    mail=0
    if totifications :
        duree=0
        for totification in totifications:
            notif_date= totification.notif_date
            notif_type= totification.notif_type
            duree_notif = ((datetime.datetime.now().date()) - (notif_date)).days
            if duree_notif > duree :
                duree = duree_notif
            else:
                duree = duree
        if duree > 7 :
            mail = 1
            return mail
        else:
            mail = 0
            return mail
    else:
        mail = 1
        return mail




@shared_task(bind=True)
def send_mail_fonction(self):
    taches = Tasks.objects.all()
    i=0
    if taches:
        for tache in taches:
            tache_id =  tache.id
            prog_tache = Evaluation_progression_tache(tache_id)
            etat_tache = prog_tache[1]
            if etat_tache == "risque de retard":
                duree_tache = notif_precedante(tache_id, etat_tache)
                if duree_tache == 1 :
                    responsab_id = tache.responsible_id
                    responsable= Responsibles.objects.get(id = responsab_id)
                    user_id = responsable.user_id
                    user_mail= responsable.email_address
                    taux_travaux = Taux_progression_Tache(tache_id)
                    taux_duree = prog_tache[0]
                    nom_tache =tache.task
                    send_mail(
                        "Risque de retard dans l'exécution des travaus de la tache " + nom_tache  ,
                        "Selon le taux consommé de la durée de la tache (" +str(taux_duree) +") et le taux d'exécution des travaux de la dite tache (" + str(taux_travaux) +"), il y a un risque de retard dans l'exécution de ces travaux, vous devez prondre les dispositifs nécessaires pour remédier à ce retard.",
                        'dashapp365@gmail.com',
                        ['mounirriahi.1963@gmail.com'],
                        fail_silently=False,
                        )
                    notification=Notification(task_id = tache_id, notif_type = "Alerte risque de retard" , description = "Selon le taux consommé de la durée de la tache (" +str(taux_duree) +") et le taux d'exécution des travaux de la dite tache (" + str(taux_travaux) +"), il y a un risque de retard dans l'exécution de ces travaux, vous devez prondre les dispositifs nécessaires pour remédier à ce retard.", notif_date = datetime.datetime.now().date())
                    notification.save()
                    i = i +1
                else:
                    i=i
            elif etat_tache == "en retard" :
                duree_tache = notif_precedante(tache_id, etat_tache)
                if duree_tache == 1 :
                    responsab_id = tache.responsible_id
                    responsable= Responsibles.objects.get(id = responsab_id)
                    user_id = responsable.user_id
                    user_mail= responsable.email_address
                    taux_travaux = Taux_progression_Tache(tache_id)
                    taux_duree = prog_tache[0]
                    nom_tache =tache.task
                    send_mail(
                        "Un retard a été enregisté dans l'exécution des travaus de la tache " + nom_tache  ,
                        "Selon le taux consommé de la durée de la tache (" +str(taux_duree) +") et le taux d'exécution des travaux de la dite tache (" + str(taux_travaux) +"), il y a un retard de " + str(taux_duree - taux_travaux ) + " dans l'exécution de ces travaux, vous devez prondre les dispositifs nécessaires pour remédier à ce retard.",
                        'dashapp365@gmail.com',
                        ['mounirriahi.1963@gmail.com'],
                        fail_silently=False,
                        )
                    notification=Notification(task_id = tache_id, notif_type = "Alerte retard enregistré" , description = "Un retard a été enregisté dans l'exécution des travaus de la tache " + nom_tache  +", Selon le taux consommé de la durée de la tache (" +str(taux_duree) +") et le taux d'exécution des travaux de la dite tache (" + str(taux_travaux) +"), il y a un retard de " + str(taux_duree - taux_travaux ) + " dans l'exécution de ces travaux, vous devez prondre les dispositifs nécessaires pour remédier à ce retard.", notif_date = datetime.datetime.now().date())
                    notification.save()
                    i = i +1                   
                else:
                    i=i
    if i != 0:
        message = "le nombre de mail envoyer est de " + str(i)

    else:
        message = "Auqu'une tache n'est en retard"
    return message





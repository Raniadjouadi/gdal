from xml.dom.minidom import Document
from django.db import models
from django.urls import reverse
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.gis.db import models
from django.contrib.auth.models import User 

# Create your models here.

class WorldBorder(models.Model):
    # Regular Django fields corresponding to the attributes in the
    # world borders shapefile.
    name = models.CharField(max_length=50)
    area = models.IntegerField()
    pop2005 = models.IntegerField('Population 2005')
    fips = models.CharField('FIPS Code', max_length=2, null=True)
    iso2 = models.CharField('2 Digit ISO', max_length=2)
    iso3 = models.CharField('3 Digit ISO', max_length=3)
    un = models.IntegerField('United Nations Code')
    region = models.IntegerField('Region Code')
    subregion = models.IntegerField('Sub-Region Code')
    lon = models.FloatField()
    lat = models.FloatField()

    # GeoDjango-specific: a geometry field (MultiPolygonField)
    mpoly = models.MultiPolygonField()

    # Returns the string representation of the model.
    def __str__(self):
        return self.name


class PopulatedPlaces(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    pop_max = models.BigIntegerField()
    geom = models.PointField(srid=4326)

    def __str__(self):
        return self.name

    # def get_absolute_url(self):
    #     return reverse('country-details', kwargs={"pk": self.pk})


class Axes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tache:axe-detail', kwargs={"pk": self.pk})


class Phone_number_types(models.Model):
    Phone_number_type = models.CharField(max_length=200)

    def __str__(self):
        return self.Phone_number_type


class Phone_numbers(models.Model):
    phone_type = models.ForeignKey(Phone_number_types, on_delete=models.CASCADE)
    phone_number = PhoneNumberField()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.phone_number)

    def get_absolute_url(self):
        return reverse('tache:phone_number-detail', kwargs={"pk": self.pk})


class Entities(models.Model):
    acronym = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200,null=True, blank=True)
    nom_fr = models.CharField(max_length=200,null=True, blank=True)
    nationality = models.CharField(max_length=200,null=True, blank=True)
    email_address = models.EmailField(max_length=254,null=True, blank=True)
    phone_number = models.ManyToManyField (Phone_numbers, null=True, blank=True)
    postal_address = models.CharField(max_length=200,null=True, blank=True)
    web_site = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.acronym) + ' | '  + str(self.name_en)

    def get_absolute_url(self):
        return reverse('tache:entity-detail', kwargs={"pk": self.pk})


class ProjectEntitiestypes(models.Model):
    type = models.CharField(max_length=100)
    def __str__(self):
        return self.type


class Projects(models.Model):
    reference_code = models.CharField(max_length=200,null=True, blank=True)
    acronym = models.CharField(max_length=200)
    name = models.CharField(max_length=512,null=True, blank=True)
    objective = models.TextField(null=True, blank=True)
    background_context = models.TextField(null=True, blank=True)
    # project_manager = models.ForeignKey(Responsibles, on_delete=models.PROTECT, null=True, blank=True)
    funder = models.ForeignKey (Entities, related_name='funder', on_delete=models.PROTECT, null=True, blank=True)
    budget = models.FloatField(null=True, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_debut_execution = models.DateField(null=True, blank=True)
    date_closing = models.DateField(null=True, blank=True)
    date_final_evaluation = models.DateField(null=True, blank=True)
    axe = models.ForeignKey(Axes, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.acronym

    def get_absolute_url(self):
        # return reverse('tache:project-detail', kwargs={"pk": self.pk})
        return reverse('tache:projects-list')


class ProjectEntities(models.Model):
    name = models.CharField(max_length=100,null=True, blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)
    entity = models.ForeignKey(Entities, on_delete=models.CASCADE)
    type = models.ForeignKey(ProjectEntitiestypes, on_delete=models.CASCADE)
    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.entity) 

    


class Responsibles(models.Model):
    civility = models.CharField(max_length=10,null=True, blank=True)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email_address = models.EmailField(max_length=254,)
    phone_number = models.ManyToManyField (Phone_numbers, null=True, blank=True)
    job_title = models.CharField(max_length=200,null=True, blank=True)
    entity = models.ForeignKey(Entities, on_delete=models.PROTECT,null=True, blank=True)
    project_entity = models.ForeignKey(ProjectEntities, on_delete=models.PROTECT,null=True, blank=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.civility) + ' '  + str(self.first_name) + ' ' + str(self.last_name)

    def get_absolute_url(self):
        return reverse('tache:responsible-detail', kwargs={"pk": self.pk})



class Aoi(models.Model):
    name = models.CharField(max_length=50)
    geom = models.MultiPolygonField(srid=4326)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Components(models.Model):
    component = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField(null=True, blank=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.component

    def get_absolute_url(self):
        return reverse('tache:components-list')


class Results(models.Model):
    result = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField()
    component = models.ForeignKey(Components, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.result

    def get_absolute_url(self):
        return reverse('tache:results-list')


class Products(models.Model):
    product = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField()
    result = models.ForeignKey(Results, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.product

    def get_absolute_url(self):
        return reverse('tache:products-list')


class Activities(models.Model):
    activity = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField()
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    date_due_debut = models.DateField()
    date_due_fin = models.DateField()
    date_due_delivery = models.DateField()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.activity

    def get_absolute_url(self):
        return reverse('tache:activities-list')


class Tasks(models.Model):
    task = models.CharField(max_length=500)
    responsible = models.ForeignKey(Responsibles, on_delete=models.PROTECT)
    objective = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    budget = models.FloatField()
    date_due_debut = models.DateField()
    date_due_fin = models.DateField()
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.task

    def get_absolute_url(self):
        return reverse('tache:tasks-list')

class Notification(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    notif_type = models.CharField(max_length=100)
    notif_date = models.DateField()

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.task



class Phases(models.Model):
    phase = models.CharField(max_length=100)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return self.phase

class TaskPhase(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    phase = models.ForeignKey(Phases, on_delete=models.CASCADE)
    class Meta:
        ordering = ["pk"]
    def __str__(self):
        return self.task

class Documenttypes(models.Model):
    type = models.CharField(max_length=100)


class Documents(models.Model):
    document = models.TextField()
    type = models.ForeignKey(Documenttypes, on_delete=models.CASCADE)


class Contracts(models.Model):
    reference_code = models.CharField(max_length=100)
    signer_client = models.ForeignKey(Responsibles, related_name='signer_client', on_delete=models.PROTECT)
    signer_provider = models.ForeignKey(Responsibles, related_name='signer_provider', on_delete=models.PROTECT)
    entity_client = models.ForeignKey(Entities, related_name='entity_client', on_delete=models.PROTECT)
    entity_provider = models.ForeignKey(Entities, related_name='entity_provider', on_delete=models.PROTECT)
    amount = models.FloatField()
    datedebut = models.DateField()
    datefin = models.DateField()
    document = models.ForeignKey(Documents, on_delete=models.CASCADE)


class Progressions(models.Model):
    date_record = models.DateField()
    progess_rate = models.IntegerField(null=True, blank=True)
    phase = models.ForeignKey(Phases, on_delete=models.PROTECT)
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    document = models.ForeignKey(Documents, on_delete=models.CASCADE,null=True, blank=True)
    contract = models.ForeignKey(Contracts, on_delete=models.CASCADE,null=True, blank=True)

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return str(self.date_record) + ' | '  + str(self.phase)

    def get_absolute_url(self):
        return reverse('tache:progressions-list')


class ActivitiesMilestones(models.Model):
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    date_due_milstone =  models.DateField()


class Currencies(models.Model):
    currency = models.CharField(max_length=50)
    code = models.CharField(max_length=3)
    symbol = models.CharField(max_length=3)


class CurrencyExchangeRates(models.Model):
    date = models.DateField()
    fm_currency = models.ForeignKey(Currencies, related_name='fm_currency', on_delete=models.CASCADE)
    to_currency = models.ForeignKey(Currencies, related_name='to_currency', on_delete=models.CASCADE)
    exchange_rate = models.FloatField()


class ActivitiesEntitiesBudget(models.Model):
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE)
    project_entity = models.ForeignKey(ProjectEntities, on_delete=models.CASCADE)
    Budget = models.FloatField()
    currency =  models.ForeignKey(Currencies, on_delete=models.PROTECT)


class ActivitiesBudgetPlan(models.Model):
    activity = models.ForeignKey(Activities, on_delete=models.CASCADE,null=True, blank=True)
    due_date = models.DateField()
    planned_disbursment = models.FloatField(null=True, blank=True)
    planned_grant = models.FloatField(null=True, blank=True)
    balance = models.FloatField(null=True, blank=True)
    currency =  models.ForeignKey(Currencies, on_delete=models.PROTECT)

    class Meta:
        ordering = ["pk"]

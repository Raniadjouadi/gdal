from django.contrib import admin

# Register your models here.
from django.contrib.gis import admin
from .models import Aoi, Projects

# admin.site.register(WorldBorder, admin.ModelAdmin)
admin.site.register(Aoi, admin.GISModelAdmin)
admin.site.register (Projects)
from django.contrib import admin
from . import models

admin.site.register(models.KeyPair)
admin.site.register(models.Account)
admin.site.register(models.Transaction)
admin.site.register(models.Block)
admin.site.register(models.Blockchain)
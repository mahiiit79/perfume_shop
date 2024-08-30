from django.contrib import admin
from . import models

class VolumeInline(admin.TabularInline):
    model = models.VolumePerfumePrice
    extra = 1
    fk_name = 'perfume'

class PerfumeAdmin(admin.ModelAdmin):
    inlines = [VolumeInline]
    list_filter = ['category', 'is_active']
    list_display = ['title', 'is_active', 'is_delete']
    list_editable = ['is_active']

class FooterLinkAdmin(admin.ModelAdmin):
    list_display = ['title', 'url']


class SiteBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'url', 'position']



admin.site.register(models.Perfume,PerfumeAdmin)
admin.site.register(models.PerfumeCategory)
admin.site.register(models.SiteSetting)
admin.site.register(models.FooterLinkBox)
admin.site.register(models.FooterLink, FooterLinkAdmin)
admin.site.register(models.SiteBanner, SiteBannerAdmin)
admin.site.register(models.ContactUs)
admin.site.register(models.PerfumeVisit)



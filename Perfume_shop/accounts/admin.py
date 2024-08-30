from django.contrib import admin
from accounts.models import User, Order, OrderDetail, ShippingMethod



class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_paid', 'payment_date', 'get_order_details')




class OrderDetailAdmin(admin.ModelAdmin):
    list_display = ('get_mobile', 'get_order_detail')
    list_display_links = ('get_mobile',)

    def get_mobile(self, obj):
        return obj.order.user.mobile

    get_mobile.short_description = 'User'

admin.site.register(OrderDetail, OrderDetailAdmin)
admin.site.register(User)
admin.site.register(Order,OrderAdmin)
admin.site.register(ShippingMethod)

# class VolumeInline(admin.TabularInline):
#     model = models.VolumePerfumePrice
#     extra = 1
#     fk_name = 'perfume'
#
# class PerfumeAdmin(admin.ModelAdmin):
#     inlines = [VolumeInline]
#     list_filter = ['category', 'is_active']
#     list_display = ['title', 'is_active', 'is_delete']
#     list_editable = ['is_active']

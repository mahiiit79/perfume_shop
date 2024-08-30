from django.contrib.auth.models import AbstractUser
from django.db import models
from accounts.myusermanager import MyUserManager
from shop.models import VolumePerfumePrice, Perfume


class User(AbstractUser):
    username = None
    mobile = models.CharField(max_length=11,unique=True,verbose_name='شماره همراه')
    otp = models.PositiveIntegerField(blank=True,null=True,verbose_name='رمزیکبارمصرف')
    otp_date = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(upload_to='images/user/',blank=True,null=True,verbose_name='تصویر آواتار')
    address = models.TextField(blank=True,null=True,verbose_name='آدرس کاربر')
    about_user = models.TextField(blank=True,null=True,verbose_name='درباره کاربر')

    objects = MyUserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    backend = 'accounts.my_backend.MobileBackend'


    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        if self.first_name is not '' and self.last_name is not '':
            return self.get_full_name()

        return self.mobile




class ShippingMethod(models.Model):
    title = models.CharField(max_length=200,verbose_name='نوع ارسال')
    price = models.PositiveIntegerField(verbose_name='قیمت ارسال')

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'شیوه ارسال'
        verbose_name_plural = 'شیوه های ارسال'






class Order(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE,verbose_name='کاربر')
    is_paid = models.BooleanField(verbose_name='نهایی شده/نشده')
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, null=True, blank=True, verbose_name='روش ارسال')
    payment_date = models.DateTimeField(null=True,blank=True,verbose_name='تاریخ پرداخت')

    def __str__(self):
        return str(self.user)


    def get_order_details(self):
        return ', '.join([f"{od.perfume.title} ({od.volume.volume}) x {od.count}" for od in self.orderdetail_set.all()])

    get_order_details.short_description = 'جزئیات سبدخرید'

    def calculate_total_price(self):
        total_amount = 0
        if self.is_paid:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.final_price * order_detail.count
        else:
            for order_detail in self.orderdetail_set.all():
                total_amount += order_detail.volume.price * order_detail.count
        return total_amount



    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید کاربران'





class OrderDetail(models.Model):
    order = models.ForeignKey('accounts.Order', on_delete=models.CASCADE,verbose_name='سبد خرید')
    perfume = models.ForeignKey('shop.Perfume', on_delete=models.CASCADE,verbose_name='محصول')
    final_price = models.IntegerField(null=True, blank=True)
    count = models.IntegerField(verbose_name='تعداد')
    volume = models.ForeignKey('shop.VolumePerfumePrice', on_delete=models.CASCADE,verbose_name='حجم محصول')

    def __str__(self):
        return str(self.order)

    def get_total_price(self):
        return self.count * self.volume.price

    def get_order_detail(self):
        return f"سبدخرید: {self.order.user.mobile},{self.order.user.first_name} {self.order.user.last_name}"

    get_order_detail.short_description = 'جزئیات سبدخرید'


    class Meta:
        verbose_name = 'جزییات سبد خرید'
        verbose_name_plural = 'لیست جزییات سبدهای خرید'



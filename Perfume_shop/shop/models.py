from django.db import models




class PerfumeCategory(models.Model):
    title = models.CharField(max_length=300,verbose_name='دسته بندی محصول')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان در url')

    def __str__(self):
        return f'({self.title} - {self.url_title})'

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'




class Perfume(models.Model):
    title = models.CharField(max_length=300,verbose_name='نام محصول')
    category = models.ManyToManyField(PerfumeCategory,related_name='perfume_categories',verbose_name='دسته بندی عطر')
    image = models.ImageField(upload_to='image/products',verbose_name='عکس محصول')
    brand = models.CharField(max_length=300, verbose_name='برند', null=True, blank=True)
    short_description = models.CharField(max_length=360, db_index=True, null=True, verbose_name='توضیحات کوتاه')
    description = models.TextField(verbose_name='توضیحات اصلی', db_index=True)
    slug = models.SlugField(default="", null=False, db_index=True, blank=True, max_length=200, unique=True,
                            verbose_name='عنوان در url')
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')
    mil_price = models.PositiveIntegerField(verbose_name='قیمت هر میل',null=True,blank=True)


    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'

    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)



# class VolumePerfumePrice(models.Model):
#     volume = models.CharField(max_length=300,verbose_name='حجم عطر')
#     price = models.IntegerField(verbose_name='قیمت عطر')
#     perfume =models.ForeignKey(Perfume, on_delete=models.CASCADE, related_name='volumes_perfume')
#
#     class Meta:
#         verbose_name = 'قیمت عطر'
#         verbose_name_plural = 'قیمت عطرها'
#
#
#
#     def __str__(self):
#         return f"{self.volume}میل-{self.price}تومان"


class VolumePerfumePrice(models.Model):
    volume = models.CharField(max_length=300,verbose_name='حجم عطر')
    price = models.IntegerField(verbose_name='قیمت عطر')
    perfume = models.ForeignKey('Perfume', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'قیمت عطر'
        verbose_name_plural = 'قیمت عطرها'



    def __str__(self):
        return f"{self.volume}میل-{self.price}تومان"



class PerfumeVisit(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    perfume = models.ForeignKey('Perfume', on_delete=models.CASCADE)
    ip = models.CharField(max_length=30, verbose_name='آی پی کاربر')


    def __str__(self):
        return f'{self.perfume.title} / {self.ip}'

    class Meta:
        verbose_name = 'بازدید محصول'
        verbose_name_plural = 'بازدیدهای محصول'





class SiteSetting(models.Model):
    site_name = models.CharField(max_length=200, verbose_name='نام سایت')
    site_url = models.CharField(max_length=200, verbose_name='دامنه سایت')
    address = models.CharField(max_length=200, verbose_name='آدرس')
    phone = models.CharField(max_length=200, null=True, blank=True, verbose_name='تلفن')
    fax = models.CharField(max_length=200, null=True, blank=True, verbose_name='فکس')
    email = models.CharField(max_length=200, null=True, blank=True, verbose_name='ایمیل')
    copy_right = models.TextField(verbose_name='متن کپی رایت سایت')
    about_us_text = models.TextField(verbose_name='متن درباره ما سایت')
    site_logo = models.ImageField(upload_to='images/site-setting/', verbose_name='لوگو سایت')
    is_main_setting = models.BooleanField(verbose_name='تنظیمات اصلی')
    image = models.ImageField(upload_to='images/site-setting/',verbose_name='تصویر درباره ما')

    class Meta:
        verbose_name = 'تنظیمات سایت'
        verbose_name_plural = 'تنظیمات'

    def __str__(self):
        return self.site_name


class FooterLinkBox(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')

    class Meta:
        verbose_name = 'دسته بندی لینک های فوتر'
        verbose_name_plural = 'دسته بندی های لینک های فوتر'

    def __str__(self):
        return self.title


class FooterLink(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان')
    url = models.URLField(max_length=500, verbose_name='لینک')
    footer_link_box = models.ForeignKey(to=FooterLinkBox, on_delete=models.CASCADE, verbose_name='دسته بندی')

    class Meta:
        verbose_name = 'لینک فوتر'
        verbose_name_plural = 'لینک های فوتر'

    def __str__(self):
        return self.title


class SiteBanner(models.Model):
    class SiteBannerPositions(models.TextChoices):
        product_list = 'product_list', 'صفحه لیست محصولات',
        product_detail = 'product_detail', 'صفحه ی جزییات محصولات',
        about_us = 'about_us', 'درباره ما'

    title = models.CharField(max_length=200, verbose_name='عنوان بنر')
    url = models.URLField(max_length=400, null=True, blank=True, verbose_name='آدرس بنر')
    image = models.ImageField(upload_to='images/banners', verbose_name='تصویر بنر')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    position = models.CharField(max_length=200, choices=SiteBannerPositions.choices, verbose_name='جایگاه نمایشی')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'بنر تبلیغاتی'
        verbose_name_plural = 'بنرهای تبلیغاتی'


class ContactUs(models.Model):
    title = models.CharField(max_length=300, verbose_name='عنوان')
    email = models.EmailField(max_length=300, verbose_name='ایمیل')
    full_name = models.CharField(max_length=300, verbose_name='نام و نام خانوادگی')
    message = models.TextField(verbose_name='متن تماس با ما')
    created_date = models.DateTimeField(verbose_name='تاریخ ایجاد', auto_now_add=True)
    response = models.TextField(verbose_name='متن پاسخ تماس با ما', null=True, blank=True)
    is_read_by_admin = models.BooleanField(verbose_name='خوانده شده توسط ادمین', default=False)

    class Meta:
        verbose_name = 'تماس با ما'
        verbose_name_plural = 'لیست تماس با ما'

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    image = models.ImageField(upload_to='images')
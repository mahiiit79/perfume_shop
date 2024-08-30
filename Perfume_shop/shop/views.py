from django import template
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F, Q, Count, Sum
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView
from accounts.models import OrderDetail, Order
from utils.http_service import get_client_ip
from .forms import VolumePerfumeForm, ContactUsModelForm
from .models import Perfume, VolumePerfumePrice, SiteSetting, FooterLinkBox, PerfumeCategory, PerfumeVisit

from django.shortcuts import get_object_or_404

class HomePageView(TemplateView):
    template_name = 'shop/index.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)



        latest_perfumes = Perfume.objects.filter(is_active=True,is_delete=False).order_by('-id')[:12]
        context['latest_perfumes'] = latest_perfumes

        most_visit_perfumes = Perfume.objects.filter(is_delete=False,is_active=True).annotate(visit_count=Count
        ('perfumevisit')).order_by('-visit_count')[:6]
        context['most_visit_perfumes'] = most_visit_perfumes

        most_bought_perfumes = Perfume.objects.filter(orderdetail__order__is_paid=True).annotate(order_count=Sum(
            'orderdetail__count'
        )).order_by('-order_count')[:6]
        context['most_bought_perfumes'] = most_bought_perfumes


        return context




class PerfumeListView(ListView):
    model = Perfume
    template_name = 'shop/product_list.html'
    context_object_name = 'perfumes'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        context = super(PerfumeListView,self).get_context_data(**kwargs)
        context['category'] = PerfumeCategory.objects.filter(is_active=True,is_delete=False)
        return context



    def get_queryset(self):
        query = super(PerfumeListView, self).get_queryset()
        category_name = self.kwargs.get('cat')
        if category_name is not None :
            query = query.filter(category__url_title__iexact = category_name)
        return query





def perfume_categories_component(request:HttpRequest):
    product_categories = PerfumeCategory.objects.filter(is_active=True,is_delete=False)
    context = {
        'categories' : product_categories
    }
    return render(request,'shop/components/perfume_component_categories.html',context)






class PerfumeDetailView(DetailView):
    model = Perfume
    template_name = 'shop/perfume_detail.html'

    def get_context_data(self, **kwargs):
        context = super(PerfumeDetailView,self).get_context_data()
        context['volume'] = VolumePerfumePrice.objects.all()
        context['volume_form'] = VolumePerfumeForm(queryset=VolumePerfumePrice.objects.filter(perfume=self.object))
        loaded_perfume = self.object
        user_ip = get_client_ip(self.request)
        user_id = None
        if self.request.user.is_authenticated:
            user_id = self.request.user.id


        has_been_visited = PerfumeVisit.objects.filter(ip__iexact=user_ip,perfume_id=loaded_perfume.id).exists()
        if not has_been_visited:
            new_visit = PerfumeVisit(ip=user_ip,user_id=user_id,perfume_id=loaded_perfume.id)
            new_visit.save()
        return context

    def get_object(self, queryset=None):
        if 'pk' in self.kwargs:
            return super().get_object(queryset)
        elif 'cat' in self.kwargs:
            category = get_object_or_404(PerfumeCategory, url_title=self.kwargs['cat'])
            return category.perfume_categories.first()  # or any other logic to get the perfume object



class About(TemplateView):
    template_name = 'shop/about_page.html'

    def get_context_data(self, **kwargs):
        context = super(About,self).get_context_data(**kwargs)
        context['site_setting'] = SiteSetting.objects.filter(is_main_setting=True).first()
        return context




class ContactUsView(CreateView):
    form_class = ContactUsModelForm
    template_name = 'shop/contact_us_page.html'
    success_url = '/contact-us/'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        setting: SiteSetting = SiteSetting.objects.filter(is_main_setting=True).first()
        context['site_setting'] = setting
        return context







# def site_header_component(request, cat=None):
#     site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
#     categories = PerfumeCategory.objects.filter(is_active=True, is_delete=False)
#     current_order = None
#     total_amount = 0
#     order_details = None
#
#     if request.user.is_authenticated:
#         current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
#         if current_order:
#             total_amount = sum(order_detail.volume.price * order_detail.count for order_detail in current_order.orderdetail_set.all())
#             order_details = current_order.orderdetail_set.all()
#
#     category = None
#     if cat:
#         category = get_object_or_404(PerfumeCategory, url_title=cat)
#         return redirect('perfume_categories_header_list', cat=category.url_title)
#
#     context = {
#         'site_setting': site_setting,
#         'categories': categories,
#         'category': category,
#         'order': current_order,
#         'sum': total_amount,
#         'order_details': order_details,
#     }
#
#     return render(request, 'shared/site_header_component.html', context)



class PerfumeCategoriesListView(ListView):
    model = Perfume
    template_name = 'shop/product_list.html'
    context_object_name = 'perfumes'
    paginate_by = 4

    def get_queryset(self):
        category_name = self.kwargs.get('cat')
        return Perfume.objects.filter(category__url_title=category_name, is_active=True, is_delete=False)




def site_header_component(request, cat=None):
    site_setting = SiteSetting.objects.filter(is_main_setting=True).first()
    categories = PerfumeCategory.objects.filter(is_active=True, is_delete=False)
    current_order = None
    total_amount = 0
    order_details = None

    if request.user.is_authenticated:
        current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
        if current_order:
            total_amount = sum(order_detail.volume.price * order_detail.count for order_detail in current_order.orderdetail_set.all())
            order_details = current_order.orderdetail_set.all()

    category = None
    if cat:
        category = get_object_or_404(PerfumeCategory, url_title=cat)
        return redirect('perfume_categories_header_list', cat=category.url_title)

    context = {
        'site_setting': site_setting,
        'categories': categories,
        'category': category,
        'order': current_order,
        'sum': total_amount,
        'order_details': order_details,
    }

    return render(request, 'shared/site_header_component.html', context)



def site_footer_component(request):
    return render(request,'shared/site_footer_component.html',{'site_setting':SiteSetting.objects.filter(is_main_setting=True).first(),
                                                               'footer_link_boxes':FooterLinkBox.objects.all()})

def mobile_header_component(request):
    return render(request,'shared/mobile_menu_component.html')



def search(request):
    query = request.GET.get('search')

    if query:
        perfume_search = Perfume.objects.filter(Q(title__icontains=query)|Q(description__icontains=query))
    else:
        perfume_search = Perfume.objects.none()  # Return an empty queryset if query is None

    paginator = Paginator(perfume_search, 2)  # 2 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'shared/search.html', {'perfume_search': page_obj})








# register = template.Library()
#
# @register.simple_tag
# def share_link_tag(perfume, platform):
#     if platform == 'twitter':
#         return f"https://twitter.com/intent/tweet?url={perfume.get_absolute_url()}&text={perfume.title}"
#     elif platform == 'linkedin':
#         return f"https://www.linkedin.com/sharing/share-offsite/?url={perfume.get_absolute_url()}"
#     elif platform == 'telegram':
#         return f"https://t.me/share/url?url={perfume.get_absolute_url()}&text={perfume.title}"
#     elif platform == 'copy':
#         return perfume.get_absolute_url()
#     else:
#         return ""
#
#
# def share_link(request, perfume_id):
#     perfume = Perfume.objects.get(pk=perfume_id)
#     platform = request.GET.get('platform')
#     if platform:
#         share_url = share_link_tag(perfume, platform)
#         return HttpResponse(share_url)
#     else:
#         return HttpResponse("Invalid platform")
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponseRedirect, HttpRequest, JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View, ListView
from django.contrib import messages
from accounts.forms import RegisterForm, LoginForm, ForgetPasswordForm, ResetPasswordForm, EditProfileModelForm, \
    ChangePasswordForm
from accounts.models import User, Order, OrderDetail, ShippingMethod
from shop.models import Perfume, VolumePerfumePrice, SiteSetting
from . import helper
from django.conf import settings
import requests
import json
import time



#'کدی که هنگام ثبت نام در سایت زرین پال بهمون میده'
MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
#'از این سه تا ادرس زمانی استفاده میشه که میخوایم کاربر رو هدایت کنیم به صفحه پرداخت'
ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"
#'مقدار مبلغ پرداختی'
amount = 11000  # Rial / Required
description = "نهایی کردن خرید شما از سایت ما"  # Required
email = ''  # Optional
mobile = ''  # Optional
# Important: need to edit for realy server.

#'به زرین پال ارسال میشه برای اینکه مشخص کنه وقتی تراکنش کاربر تموم شد به کدوم ادرس فرستاده بشه و اطلاعات پرداختی رو به کی بده'
CallbackURL = 'http://127.0.0.1:8000/accounts/verify-payment/'






class RegisterUserView(View):
    def get(self,request):
        register_form = RegisterForm()
        context = {
            'register_form' : register_form
        }
        return render(request,'accounts/register_page.html',context)
    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            mobile = register_form.cleaned_data.get('mobile')
            user_password = register_form.cleaned_data.get('password')
            user : bool = User.objects.filter(mobile__iexact=mobile).exists()
            if user:
                register_form.add_error('mobile','شماره همراه وارد شده تکراری می باشد!')
            else:

                new_user = User(mobile=mobile, is_active=False, otp=helper.get_random_otp())
                new_user.set_password(user_password)
                # send otp
                otp = new_user.otp
                helper.send_otp(mobile,otp)
                #save otp
                new_user.save()
                request.session['user_mobile'] = new_user.mobile
                #redirect to verify page
                return HttpResponseRedirect(reverse('verify'))
        context = {
            'register_form': register_form
        }
        return render(request,'accounts/register_page.html',context)





def verify(request):
    try:
        mobile = request.session.get('user_mobile')
        user = User.objects.get(mobile = mobile)

        if request.method == "POST":

            # check otp expiration
            if not helper.check_otp_expiration(user.mobile):
                messages.error(request, "زمان کد ارسال شده به پایان رسیده است. لطفا دوباره امتحان کنید.")
                return HttpResponseRedirect(reverse('register_page'))

            if user.otp != int(request.POST.get('otp')):
                messages.error(request, "کد وارد شده صحیح نیست!")
                return HttpResponseRedirect(reverse('verify'))

            user.is_active = True
            user.save()
            return redirect(reverse('login_page'))

        return render(request, 'accounts/verify.html', {'mobile': mobile})

    except User.DoesNotExist:
        messages.error(request, "Error accorded, try again.")
        return HttpResponseRedirect(reverse('register_page'))




class LoginUserView(View):
    def get(self,request):
        login_form = LoginForm()
        context = {
            'login_form': login_form
        }
        return render(request,'accounts/login_page.html',context)

    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            mobile = login_form.cleaned_data.get('mobile')
            user_password = login_form.cleaned_data.get('password')
            user : User = User.objects.filter(mobile=mobile).first()
            if user is not None:
                if  not user.is_active:
                    login_form.add_error(mobile,'حساب کاربری شما فعال نیست')
                else:
                    is_password_correct = user.check_password(user_password)
                    if is_password_correct:
                        login(request,user)
                        return redirect(reverse('dashboard'))
                    else:
                        login_form.add_error(mobile,'کلمه عبور اشتباه است.')
        context={
            'login_form': login_form
        }
        return render(request,'accounts/login_page.html',context)





class LogOutView(View):
    def get(self, request):
        logout(request)
        return redirect(reverse('login_page'))






class ForgetView(View):
    def get(self, request):
        forget_pass_form = ForgetPasswordForm()
        return render(request, 'accounts/forget_password_page.html', context={'forget_pass_form': forget_pass_form})

    def post(self, request):
        forget_pass_form = ForgetPasswordForm(request.POST)
        if forget_pass_form.is_valid():
            mobile = forget_pass_form.cleaned_data.get('mobile')
            user = User.objects.filter(mobile=mobile).first()
            if user is not None:
                otp = helper.get_random_otp()
                helper.send_otp(mobile, otp)
                request.session['user_mobile'] = mobile
                request.session['otp'] = otp
                return redirect(reverse('verify_pass'))
        return render(request, 'accounts/forget_password_page.html', context={'forget_pass_form': forget_pass_form, 'obile': mobile})









class VerifyPassView(View):
    def get(self, request, *args, **kwargs):
        mobile = request.session.get('user_mobile')
        return render(request, 'accounts/verify_forget.html', {'mobile': mobile})

    def post(self, request, *args, **kwargs):
        mobile = request.POST['mobile']
        otp = request.POST['otp']

        user = User.objects.filter(mobile=mobile, otp=otp).first()
        if user:
            # Redirect to the change_password_page
            return redirect('reset_pass', user.id)
        else:
            # Handle the case when the OTP is incorrect
            messages.error(request, "Invalid OTP. Please try again.")
            return render(request, 'accounts/verify_forget.html', {'mobile': mobile})





# #
# # #'forgetpassreset'
# class ChangePasswordView(View):
#     def get(self,request: HttpRequest,otp_code):
#         user : User = User.objects.filter(otp__exact=otp_code).first()
#         if user is None:
#             return redirect(reverse('login_page'))
#
#         reset_pass_form = ResetPasswordForm()
#         context = {
#             'reset_pass_form': reset_pass_form,
#             'user': user
#         }
#         return render(request,'accounts/reset_password_page.html',context)
#
#     def post(self,request: HttpRequest,otp_code):
#         reset_pass_form = ResetPasswordForm(request.POST)
#         user: User = User.objects.filter(otp_exact=otp_code).first()
#         if reset_pass_form.is_valid():
#             if user is None:
#                 return redirect(reverse('login_page'))
#
#             user_new_pass = reset_pass_form.cleaned_data.get('password')
#             user.set_password(user_new_pass)
#             user.otp = helper.get_random_otp()
#             user.is_active = True
#             user.save()
#             return redirect(reverse('login_page'))
#
#         context = {
#             'reset_pass_form': reset_pass_form,
#             'user': user
#         }
#
#         return render(request, 'accounts/reset_password_page.html', context)





class ChangePasswordView(View):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        reset_pass_form = ResetPasswordForm()
        return render(request, 'accounts/reset_password_page.html', context={'reset_pass_form': reset_pass_form, 'user': user})

    def post(self, request, user_id):
        user = User.objects.get(id=user_id)
        reset_pass_form = ResetPasswordForm(request.POST)
        if reset_pass_form.is_valid():
            new_password = reset_pass_form.cleaned_data.get('password')
            user.set_password(new_password)
            user.save()
            return redirect(reverse('login_page'))
        return render(request, 'accounts/reset_password_page.html', context={'reset_pass_form': reset_pass_form, 'user': user})




@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'accounts/dashboard.html'



@method_decorator(login_required, name='dispatch')
class EditUserProfilePage(View):
    def get(self, request: HttpRequest):
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(instance=current_user)
        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'accounts/edit_profile_page.html', context)

    def post(self, request: HttpRequest):
        current_user = User.objects.filter(id=request.user.id).first()
        edit_form = EditProfileModelForm(request.POST, request.FILES, instance=current_user)
        if edit_form.is_valid():
            edit_form.save(commit=True)

        context = {
            'form': edit_form,
            'current_user': current_user
        }
        return render(request, 'accounts/edit_profile_page.html', context)





@method_decorator(login_required, name='dispatch')
class EditPasswordDashboard(View):
    def get(self,request):
        form = ChangePasswordForm()
        return render(request,'accounts/change_dashboard_password.html',{'form':form})

    def post(self,request : HttpRequest):
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            current_user: User = User.objects.filter(id=request.user.id).first()
            if current_user.check_password(form.cleaned_data.get('current_password')):
                current_user.set_password(form.cleaned_data.get('password'))
                current_user.save()
                logout(request)
                return redirect('login_page')
            else:
                form.add_error('password', 'کلمه عبور وارد شده اشتباه می باشد')

        return render(request,'accounts/change_dashboard_password.html',{'form':form})




@login_required
def user_panel_menu_component(request: HttpRequest):
    return render(request, 'accounts/components/user_panel_menu_component.html')





@login_required
def add_perfume_to_order(request: HttpRequest):
    perfume_id = int(request.GET.get('perfume_id'))
    count = int(request.GET.get('count'))
    volume_id = int(request.GET.get('volume_id'))
    if count < 1:
        return JsonResponse({
            'status': 'invalid_count',
            'text': 'مقدار وارد شده معتبر نمی باشد.',
            'confirm_button_text': 'مرسی از شما!'
        })
    if request.user.is_authenticated:
        perfume = Perfume.objects.filter(id=perfume_id, is_active=True, is_delete=False).first()
        if perfume is not None:
            current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
            current_order_detail = current_order.orderdetail_set.filter(perfume_id=perfume_id, volume_id=volume_id).first()
            if current_order_detail is not None:
                current_order_detail.count += count
                current_order_detail.save()
            else:
                new_detail = OrderDetail(order_id=current_order.id, perfume_id=perfume_id, count=count, volume_id=volume_id)
                new_detail.save()

            order_details = current_order.orderdetail_set.all()
            order_total = current_order.calculate_total_price()
            order_data = {
                'order_details': [{'perfume_title': od.perfume.title, 'volume_title': od.volume.volume, 'count': od.count , 'image':od.perfume.image.url} for od in order_details],
                'order_total': order_total
            }

            return JsonResponse({
                'status': 'success',
                'text': 'محصول مورد نظر با موفقیت به سبد خرید شما اضافه شد.',
                'confirm_button_text': 'باشه ممنون!',
                'order_data': order_data
            })
        else:
            return JsonResponse({
                'status': 'not_found',
                'text': 'محصول مورد نظر یافت نشد!',
                'confirm_button_text': 'مرسیییی'
            })

    else:
        return JsonResponse({
            'status': 'not_auth',
            'text': 'برای افزوردن محصول به سبد خرید ابتدا می بایست وارد سایت شوید.',
            'confirm_button_text': 'ورود به سایت'
        })





@login_required
def remove_header_order_detail(request):
    if request.method == 'POST':
        detail_id = request.POST.get('detailId')
        print('detail_id:', detail_id)  # Add this line
        if detail_id is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid detail ID'})

    try:
        order_detail = OrderDetail.objects.get(id=detail_id, order__is_paid=False, order__user_id=request.user.id)
        order_detail.delete()
        print("Order detail deleted successfully!")

        current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
        header_basket_count = current_order.orderdetail_set.count()
        order_details = current_order.orderdetail_set.all()
        order_total = current_order.calculate_total_price()

        header_basket_html = render_to_string('shared/site_header_component.html', {'order_details': order_details})
        total_price = order_total

        return JsonResponse({
            'status': 'success',
            'site_header_component': header_basket_html,
            'header_basket_count': header_basket_count,
            'total_price': total_price
        })

    except OrderDetail.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Order detail not found',
        })








@login_required
def user_basket(request:HttpRequest):
    current_order,created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False,user_id=request.user.id)
    total_amount = 0
    for order_detail in current_order.orderdetail_set.all():
        total_amount += order_detail.volume.price * order_detail.count
    shipping_method_price = 0
    if request.method == 'POST':
        shipping_method_id = request.POST.get('shipping_method')
        if shipping_method_id:
            shipping_method = ShippingMethod.objects.get(id=shipping_method_id)
            current_order.shipping_method = shipping_method
            current_order.save()
            shipping_method_price = shipping_method.price
    total_amount_with_shipping = total_amount + shipping_method_price

    context = {
        'order' : current_order,
        'sum': total_amount,
        'total_amount_with_shipping': total_amount_with_shipping,
        'user': request.user,
        'shipping_methods': ShippingMethod.objects.all(),
    }

    return render(request,'accounts/user_basket.html',context)


@login_required
def remove_order_detail(request):
    detail_id = request.GET.get('detail_id')
    if detail_id is None:
        return JsonResponse({
            'status': 'not_found_detail_id'
        })

    deleted_count, deleted_dict = OrderDetail.objects.filter(id=detail_id, order__is_paid=False, order__user_id=request.user.id).delete()

    if deleted_count == 0:
        return JsonResponse({
            'status': 'detail_not_found'
        })

    current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = current_order.calculate_total_price()

    context = {
        'order': current_order,
        'sum': total_amount,

    }
    return JsonResponse({
        'status': 'success',
        'body': render_to_string('accounts/user_basket_content.html', context)
    })



@login_required
def change_order_detail_count(request: HttpRequest):
    detail_id = request.GET.get('detail_id')
    state = request.GET.get('state')
    if detail_id is None or state is None:
        return JsonResponse({
            'status': 'not_found_detail_or_state'
        })

    order_detail = OrderDetail.objects.filter(id=detail_id, order__user_id=request.user.id,
                                              order__is_paid=False).first()
    if order_detail is None:
        return JsonResponse({
            'status': 'detail_not_found'
        })

    if state == 'increase':
        order_detail.count += 1
        order_detail.save()
    elif state == 'decrease':
        if order_detail.count == 1:
            order_detail.delete()
        else:
            order_detail.count -= 1
            order_detail.save()
    else:
        return JsonResponse({
            'status': 'state_invalid'
        })
    current_order, created = Order.objects.prefetch_related('orderdetail_set').get_or_create(is_paid=False, user_id=request.user.id)
    total_amount = current_order.calculate_total_price()
    shipping_method = current_order.shipping_method
    total_amount_with_shipping = total_amount + shipping_method.price if shipping_method else total_amount

    context = {
        'order': current_order,
        'sum': total_amount,
        'user': request.user,
        'shipping_methods': ShippingMethod.objects.all(),
        'total_amount_with_shipping': total_amount_with_shipping
    }
    return JsonResponse({
        'status': 'success',
        'body': render_to_string('accounts/user_basket_content.html', context)
    })






@login_required
def my_shoppings(request:HttpRequest):
    orders = Order.objects.filter(user=request.user,is_paid=True).annotate(order_detail_count=Count('orderdetail'))
    context = {
        'orders': orders,
        'site_setting': SiteSetting.objects.filter(is_main_setting=True).first(),
        'customer': User.objects.filter(is_active=True).first(),

    }

    return render(request,'accounts/user_shopping.html',context)








def request_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    shipping_method_price = current_order.shipping_method.price if current_order.shipping_method else 0
    total_price_with_shipping = total_price + shipping_method_price

    if total_price == 0:
        return redirect(reverse('user_basket'))

    req_data = {
        "merchant_id": MERCHANT,
        "amount": total_price_with_shipping * 10,
        "callback_url": CallbackURL,
        "description": description,
        # "metadata": {"mobile": mobile, "email": email}
    }
    req_header = {"accept": "application/json", "content-type": "application/json'"}

    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(req_data), headers=req_header)

    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


@login_required
def verify_payment(request: HttpRequest):
    current_order, created = Order.objects.get_or_create(is_paid=False, user_id=request.user.id)
    total_price = current_order.calculate_total_price()
    shipping_method_price = current_order.shipping_method.price if current_order.shipping_method else 0
    total_price_with_shipping = total_price + shipping_method_price
    t_authority = request.GET['Authority']

    if request.GET.get('Status') == 'OK':

        req_header = {"accept": "application/json", "content-type": "application/json'"}

        req_data = {
            "merchant_id": MERCHANT,
            "amount": total_price_with_shipping  * 10,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:
                # 'current_order has to close'
                current_order.is_paid = True
                current_order.payment_date = time.time()
                current_order.save()
                ref_str = req.json()['data']['ref_id']
                return render(request, 'accounts/payment_result.html', {
                    'success': f'تراکنش شما با کد پیگیری {ref_str} با موفقیت انجام شد'
                })
            elif t_status == 101:
                return render(request, 'accounts/payment_result.html', {
                    'info': 'این تراکنش قبلا ثبت شده است'
                })
            else:
                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
                return render(request, 'accounts/payment_result.html', {
                    'error': str(req.json()['data']['message'])
                })
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
            return render(request, 'accounts/payment_result.html', {
                'error': e_message
            })
    else:
        return render(request, 'accounts/payment_result.html', {
            'error': 'پرداخت با خطا مواجه شد / کاربر از پرداخت ممانعت کرد'
        })
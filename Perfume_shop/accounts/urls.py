from django.urls import path

from accounts import views

urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register_page'),
    path('verify/', views.verify, name='verify'),
    path('login/', views.LoginUserView.as_view(), name='login_page'),
    path('dashboard/',views.DashboardView.as_view(),name='dashboard'),

    path('logout/',views.LogOutView.as_view(),name='logout'),
    path('forget-pass/', views.ForgetView.as_view(), name='forget_pass'),
    path('verify-pass/', views.VerifyPassView.as_view(), name='verify_pass'),
    path('reset-pass/<int:user_id>/', views.ChangePasswordView.as_view(), name='reset_pass'),

    path('edit-profile/', views.EditUserProfilePage.as_view(), name='edit_profile_page'),
    path('edit-pass-dashboard/', views.EditPasswordDashboard.as_view(), name='edit_password_dashboard_page'),

    path('my-shppings/', views.my_shoppings, name='user_shopping_page'),

    path('add-to-order',views.add_perfume_to_order,name='add_perfume_to_order'),
    path('user-basket/',views.user_basket,name='user_basket'),
    path('remove-basket-detail/',views.remove_order_detail,name='remove_basket'),
    path('change-order-detail/',views.change_order_detail_count,name='change_basket'),
    path('remove-header-order-detail/', views.remove_header_order_detail, name='remove_header_order_detail'),

    path('request-payment/',views.request_payment,name='request_payment'),
    path('verify-payment/',views.verify_payment,name='verify_payment')

]
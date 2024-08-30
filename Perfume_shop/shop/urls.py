from django.urls import path

from shop import views



urlpatterns = [
    path('',views.HomePageView.as_view(),name='home_page'),
    path('perfumes/',views.PerfumeListView.as_view(),name='perfume_list'),
    path('perfumes/cat/<cat>', views.PerfumeListView.as_view(), name='perfume_categories_list'),
    path('perfumes/<pk>/',views.PerfumeDetailView.as_view(), name='perfume_detail'),
    path('perfumes/cat/<str:cat>/', views.PerfumeCategoriesListView.as_view(), name='perfume_categories_list'),
    path('about-us/',views.About.as_view(),name='about_page'),
    path('contact-us/',views.ContactUsView.as_view(),name='Contact_us_page'),
    path('search/',views.search,name='search_page')

]
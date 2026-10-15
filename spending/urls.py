from django.urls import path
from spending.views import Signupview,GetMeView,ExpenseListCreateView,ExpenseRetrieveUpdateDeleteView
from rest_framework.authtoken.views import ObtainAuthToken
from spending.views import ExpenseSummaryView
from spending.views import BudgetPlan
urlpatterns = [
    path("register/",Signupview.as_view()),

    path("me/",GetMeView.as_view()),
    path('expense/',ExpenseListCreateView.as_view()),
    path('expense/<int:pk>/',ExpenseRetrieveUpdateDeleteView.as_view()),
    path('token/',ObtainAuthToken.as_view()),
    path('expense/summary/',ExpenseSummaryView.as_view()),
    path('expense/monthlybudget/',BudgetPlan.as_view()),
    
]
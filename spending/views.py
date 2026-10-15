from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum


from rest_framework.views import APIView
from rest_framework.response import Response

from spending.serializers import SignupSerializer,ExpenseSerializer
from rest_framework import authentication,permissions
from spending.models import Expense
from spending.permissions import IsOwner
from spending.ai_service import getbudgetplan

from datetime import datetime

# Create your views here.

class Signupview(APIView):
    def post(self,request):
        form_data=request.data
        serializer_instance=SignupSerializer(data=form_data)

        if serializer_instance.is_valid():
            cleaned_data=serializer_instance.validated_data
            qs=User.objects.create_user(**cleaned_data)

            serializer_instance=SignupSerializer(qs)
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

class GetMeView(APIView):
    #authentication_classes=[authentication.BasicAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[authentication.TokenAuthentication]
    

    def get(self,request):
        auth_user=request.user
        instance=User.objects.get(username=auth_user)
        serializer_instance=SignupSerializer(instance)
        return Response(data=serializer_instance.data)

class ExpenseListCreateView(APIView):
    #authentication_classes=[authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    
    

    def get(self,request):
        instance=Expense.objects.filter(owner=request.user)
        serializer_instance=ExpenseSerializer(instance,many=True)
        return Response(data=serializer_instance.data)


    def post(self,request):
        form_data=request.data
        serializer_instance=ExpenseSerializer(data=form_data)

        if serializer_instance.is_valid():
            serializer_instance.save(owner=request.user)
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

class ExpenseRetrieveUpdateDeleteView(APIView):
    #authentication_classes=[authentication.BasicAuthentication]
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[IsOwner]



    def get(self,request,pk=None):
        instance=get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,instance)
        serializer_instance=ExpenseSerializer(instance)
        return Response(data=serializer_instance.data)

    def put(self,request,pk=None):
        instance=get_object_or_404(Expense,id=pk)
        form_data=request.data
        self.check_object_permissions(request,instance)
        serializer_instance=ExpenseSerializer(data=form_data,instance=instance)
        if serializer_instance.is_valid():
            serializer_instance.save()
            return Response(data=serializer_instance.data)
        else:
            return Response(data=serializer_instance.errors)

    def delete(self,request,pk=None):
        instance=get_object_or_404(Expense,id=pk)
        self.check_object_permissions(request,instance)
        instance.delete()
        return Response(data={"message":"deleted"})


class ExpenseSummaryView(APIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]

    def get(self,request):
        response_data={
            "todays_total":0
        }
        cur_date=datetime.now().date()
        cur_month=datetime.now().month
        cur_year=datetime.now().year
        monthly_transaction=Expense.objects.filter(owner=request.user,created_at__month=cur_month,created_at__year=cur_year)
        if monthly_transaction:
            monthly_total=monthly_transaction.values("amount").aggregate(total=Sum("amount")).get("total")
            response_data["monthly_total"]=monthly_total
        todays_transaction=Expense.objects.filter(owner=request.user,created_at__date=cur_date)
        if todays_transaction:
            todays_total=todays_transaction.values("amount").aggregate(total=Sum("amount")).get("total")
            #todays category summary
            
            category_summary=todays_transaction.values("category").annotate(total=Sum("amount"))
            response_data["todays_total"]=todays_total
            
            response_data["category_summary"]=category_summary
        return Response(data=response_data)

class BudgetPlan(APIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        response_data={
            "monthly_total":0
        }                                                                   

        cur_date=datetime.now().date()
        cur_month=datetime.now().month
        cur_year=datetime.now().year

        monthly_transaction=Expense.objects.filter(owner=request.user,created_at__month=cur_month,created_at__year=cur_year)
        if monthly_transaction:

            monthly_total=monthly_transaction.values("amount").aggregate(total=Sum("amount")).get("total")
            category_summary=monthly_transaction.values("category").annotate(total=Sum("amount"))

            response_data["monthly_total"]=monthly_total
            response_data["category_summary"]=category_summary
            
            budgetPlan=getbudgetplan(response_data)
            response_data["plan"]=budgetPlan
        return Response(data=response_data)
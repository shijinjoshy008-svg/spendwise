from django.shortcuts import render,get_object_or_404
from django.contrib.auth.models import User
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication,permissions

from spending.serializers import SignupSerializer,ExpenseSerializer
from spending.models import Expense
from spending.permissions import IsOwner


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
    authentication_classes=[authentication.TokenAuthentication]

    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        auth_user=request.user
        instance=User.objects.get(username=auth_user)
        serializer_instance=SignupSerializer(instance)
        return Response(data=serializer_instance.data)

class ExpenseListCreateView(APIView):
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
class ExpenseSummery(APIView):
    authentication_classes=[authentication.TokenAuthentication]
    permission_classes=[permissions.IsAuthenticated]
    def get(self,request):
        response_data={
            "today_total":0
        }
        cur_date=datetime.now().date()
        cur_month=datetime.now().month
        cur_year=datetime.now().year
        month_transaction=Expense.objects.filter(owner=request.user,created_at__month=cur_month,created_at__year=cur_year)
        if month_transaction:
            month_total=month_transaction.values("amount").aggregate(total=Sum("amount")).get("total")
            response_data["month_total"]=month_total
           
        today_transaction=Expense.objects.filter(owner=request.user,created_at__date=cur_date)
        if today_transaction:
            today_total=today_transaction.values("amount").aggregate(total=Sum("amount")).get("total")
            category_summery=today_transaction.values("category").annotate(total=Sum("amount"))
            response_data["today_total"]=today_total
            response_data["category_summary"]=category_summery
        return Response(data=response_data)




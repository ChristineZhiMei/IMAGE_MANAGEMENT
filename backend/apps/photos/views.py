from django.http import HttpResponse
from django.shortcuts import render
from django.views import View


# Create your views here.
class PhotoMainView(View):
    def get(self, request):
        print("get请求")
        return HttpResponse("get请求")
    def post(self, request):
        print("post请求")
        return HttpResponse("post请求")
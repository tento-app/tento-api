from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from graphene_django.views import GraphQLView
# Create your views here.

class PrivateGraphQLView(LoginRequiredMixin, GraphQLView):
    pass
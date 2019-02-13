from django.urls import path
from gql.views import PrivateGraphQLView,GraphQLView
from django.views.decorators.csrf import csrf_exempt
urlpatterns = [
    # path('',GraphQLView.as_view(graphiql=True))
    path('',csrf_exempt(GraphQLView.as_view(graphiql=True)))
    # path('',PrivateGraphQLView.as_view(graphiql=True))
]
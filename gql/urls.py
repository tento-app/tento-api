from django.urls import path
from gql.views import PrivateGraphQLView,GraphQLView

urlpatterns = [
    path('',GraphQLView.as_view(graphiql=True))
    # path('',PrivateGraphQLView.as_view(graphiql=True))
]
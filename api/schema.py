import graphene
import graphql_jwt

import gql.schema
import users.schema


class Query(gql.schema.Query, users.schema.Query, graphene.ObjectType):
    # This class will inherit from multiple Queries
    # as we begin to add more apps to our project
    pass

class Mutation(gql.schema.Mutation, users.schema.Mutation, graphene.ObjectType):
    auth_token = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
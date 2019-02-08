import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required

from users.models import User,Course,Team,University,Department

class UniversityNode(DjangoObjectType):
    class Meta:
        model = University
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'users': ['exact'],
        }
        interfaces = (relay.Node, )

class DepartmentNode(DjangoObjectType):
    class Meta:
        model = Department
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'users': ['exact'],
        }
        interfaces = (relay.Node, )

class TeamNode(DjangoObjectType):
    class Meta:
        model = Team
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'is_official': ['exact'],
            'owner': ['exact'],
            'users': ['exact', 'icontains'],
            'host_projects': ['exact'],
            'university' : ['exact'],
            'university__name' : ['exact'],
        }
        interfaces = (relay.Node, )

class CourseNode(DjangoObjectType):
    class Meta:
        model = Course
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'users': ['exact'],
        }
        interfaces = (relay.Node, )

class UserNode(DjangoObjectType):
    class Meta:
        model = User
        # filter_fields = ['username', 'email','course','teams']
        filter_fields = {
            'username': ['exact', 'icontains', 'istartswith'],
            'name': ['exact', 'icontains', 'istartswith'],
            'email': ['exact', 'icontains'],
            'course': ['exact'],
            'course__name': ['exact'],
            'teams': ['exact'],
            'teams__name': ['exact'],
            'host_projects': ['exact'],
            'projects': ['exact'],
            'tags': ['exact'],
            'tags__name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserNode, token=graphene.String(required=True))

    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    university = relay.Node.Field(UniversityNode)
    all_university = DjangoFilterConnectionField(UniversityNode)

    department = relay.Node.Field(DepartmentNode)
    all_department = DjangoFilterConnectionField(DepartmentNode)

    course = relay.Node.Field(CourseNode)
    all_course = DjangoFilterConnectionField(CourseNode)

    team = relay.Node.Field(TeamNode)
    all_teams = DjangoFilterConnectionField(TeamNode)
    join_teams = DjangoFilterConnectionField(TeamNode, token=graphene.String(required=True))
    host_teams = DjangoFilterConnectionField(TeamNode, token=graphene.String(required=True))
    @login_required
    def resolve_join_teams(self, info, **kwargs):
        return info.context.user.teams
    @login_required
    def resolve_host_teams(self, info, **kwargs):
        return Team.objects.filter(owner=info.context.user)
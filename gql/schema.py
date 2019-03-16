import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id

from graphql_jwt.decorators import login_required

from gql.models import Category, Tag, Project

import django_filters

# Graphene will automatically map the Category model's fields onto the CategoryNode.
# This is configured in the CategoryNode's Meta class (as you can see below)

class CategoryNode(DjangoObjectType):
    class Meta:
        model = Category
        filter_fields = ['name']
        interfaces = (relay.Node, )

class TagNode(DjangoObjectType):
    class Meta:
        model = Tag
        filter_fields = ['name', 'teams', 'users', 'projects']
        interfaces = (relay.Node, )

class ProjectNode(DjangoObjectType):
    class Meta:
        model = Project
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
            'users': ['exact'],
            'tags': ['exact'],
            'tags__name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node, )

class isPubricFilter(django_filters.FilterSet):
    class Meta:
        model = Project
        fields = {
        'name': ['exact', 'icontains', 'istartswith'],
        'users': ['exact'],
        'tags': ['exact'],
        'tags__name': ['exact', 'icontains', 'istartswith'],
        }
    @property
    def qs(self):
        # The query context can be found in self.request.
        return super(isPubricFilter, self).qs.filter(is_public=True).order_by('created_at').reverse()

class Query(graphene.ObjectType):
    category = relay.Node.Field(CategoryNode)
    all_categories = DjangoFilterConnectionField(CategoryNode)

    tag = relay.Node.Field(TagNode)
    all_tags = DjangoFilterConnectionField(TagNode)

    project = relay.Node.Field(ProjectNode)
    all_projects = DjangoFilterConnectionField(ProjectNode, filterset_class=isPubricFilter)
    join_projects = DjangoFilterConnectionField(ProjectNode, token=graphene.String(required=True))
    @login_required
    def resolve_join_projects(self, info, **kwargs):
        return info.context.user.projects.filter(is_public=True)
    host_projects = DjangoFilterConnectionField(ProjectNode, token=graphene.String(required=True))
    @login_required
    def resolve_host_projects(self, info, **kwargs):
        return Project.objects.filter(user=info.context.user)    


class ProjectInput(graphene.InputObjectType):
    name = graphene.String()
    content = graphene.String()
    header = graphene.String()
    logo = graphene.String()
    url = graphene.String()
    tags = graphene.List(graphene.String)
    is_public = graphene.Boolean()

class CreateProject(graphene.Mutation):
    class Arguments:
        project_data = ProjectInput()
        token = graphene.String(required=True)

    project = graphene.Field(ProjectNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_data=None):
        project = Project.objects.create(
            name=project_data.name,
            content=project_data.content,
            user=info.context.user
        )
        if project_data.tags:
            for tag in project_data.tags:
                project.tags.add(Tag.objects.get(name=tag))
        return CreateProject(project=project)

class UpdateProject(graphene.Mutation):
    class Arguments:
        project_id  = graphene.String(required=True) # project_idはgraphql api上のid
        project_data = ProjectInput()
        token  = graphene.String(required=True)

    project = graphene.Field(ProjectNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_data=None, project_id=None):
        db_id = from_global_id(project_id)
        try:
            project = Project.objects.get(pk=db_id[1])
            project.name = project_data.name
            project.save()
            if project_data.tags:
                for tag in project_data.tags:
                    project.tags.add(Tag.objects.get(name=tag))
        except Project.model.DoesNotExist:
            return None
        return UpdateProject(project=project)


class JoinProject(graphene.Mutation):
    class Arguments:
        project_id  = graphene.String(required=True) # project_idはgraphql api上のid
        token  = graphene.String(required=True)
    project = graphene.Field(ProjectNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_id=None):
        db_id = from_global_id(project_id)
        project = Project.objects.get(pk=db_id[1])
        user = info.context.user
        user.projects.add(project)
        return UpdateProject(project=project)


class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    join_project = JoinProject.Field()

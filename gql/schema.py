import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphql_relay.node.node import from_global_id
from django.utils import timezone

from graphql_jwt.decorators import login_required

from gql.models import Category, Tag, Project

import django_filters

from graphene_file_upload.scalars import Upload


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
            'place': ['exact', 'icontains', 'istartswith'],
            'users': ['exact'],
            'start_at' : ['exact', 'year__gt'],
            'created_at' : ['exact', 'year__gt'],
            'updated_at' : ['exact', 'year__gt'],
            'is_public': ['exact'],
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
    name = graphene.String(default=None)
    content = graphene.String(default=None)
    contact = graphene.String(default=None)
    place = graphene.String(default=None)
    header = Upload(default=None)
    tags = graphene.List(graphene.String)
    start_at = graphene.String(default=timezone.now)
    is_public = graphene.Boolean(default=True)

class CreateProject(graphene.Mutation):
    class Arguments:
        project_data = ProjectInput()
        token = graphene.String(required=True)

    project = graphene.Field(ProjectNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_data=None):
        print(project_data)
        project = Project.objects.create(
            name=project_data.name,
            content=project_data.content,
            contact=project_data.contact,
            place=project_data.place,
            start_at=project_data.start_at,
            header=project_data.header,
            user=info.context.user
        )
        if project_data.tags:
            for tag in project_data.tags:
                print(tag)
                if Tag.objects.get(name=tag).exists():
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
            if project_data.name: project.name = project_data.name
            if project_data.content: project.content = project_data.content
            if project_data.contact: project.contact = project_data.contact
            if project_data.place: project.place = project_data.place
            if project_data.start_at: project.start_at = project_data.start_at
            if project_data.header: project.header = project_data.header
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

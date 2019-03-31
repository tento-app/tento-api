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
import dateutil.parser

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
            'start_at' : ['exact'],
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
        'place': ['exact', 'icontains', 'istartswith'],
        'users': ['exact'],
        'start_at' : ['exact'],
        'created_at' : ['exact', 'year__gt'],
        'updated_at' : ['exact', 'year__gt'],
        'is_public': ['exact'],
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
    contact = graphene.String()
    place = graphene.String()
    startat = graphene.String()
    header = Upload()
    tags = graphene.List(graphene.String)
    isPublic = graphene.Boolean()

class CreateProject(graphene.Mutation):
    class Arguments:
        project_data = ProjectInput()
        token = graphene.String(required=True)

    project = graphene.Field(ProjectNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_data=None):
        project = Project.objects.create(
            user=info.context.user,
            name=project_data.name,
            content=project_data.content,
            contact=project_data.contact,
            place=project_data.place,
            start_at=dateutil.parser.parse(project_data.startat),
            header=project_data.header,
            thumbnail=project_data.header,
            )
        if project_data.tags:
            for tag in project_data.tags:
                if Tag.objects.get(name=tag):
                    project.tags.add(Tag.objects.get(name=tag))
        return CreateProject(project=project)

class UpdateProject(graphene.Mutation):
    class Arguments:
        project_id  = graphene.String(required=True) # project_idはgraphql relay上のid
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
            if project_data.header:
                project.header = project_data.header
                project.thumbnail = project_data.header
            project.save()
            if project_data.tags:
                now_tags = project.tags.values_list('name', flat=True)
                new_tags = project_data.tags
                add_tags = list(set(new_tags)-set(now_tags))
                if add_tags:
                    for tag in add_tags:
                        project.tags.add(Tag.objects.get(name=tag))
                remove_tags = list(set(now_tags)-set(new_tags))
                if remove_tags:
                    for tag in remove_tags:
                        project.tags.remove(Tag.objects.get(name=tag))
        except Project.model.DoesNotExist:
            return None
        return UpdateProject(project=project)


class JoinProject(graphene.Mutation):
    class Arguments:
        project_id  = graphene.String(required=True) # project_idはgraphql api上のid
        token  = graphene.String(required=True)
    
    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_id=None):
        db_id = from_global_id(project_id)
        project = Project.objects.get(pk=db_id[1])
        user = info.context.user
        try:
            user.projects.add(project)
            success=True
        except:
            success=False
        return UpdateProject(success=success)

class OutProject(graphene.Mutation):
    class Arguments:
        project_id  = graphene.String(required=True) # project_idはgraphql api上のid
        token  = graphene.String(required=True)
    
    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, token=None, project_id=None):
        db_id = from_global_id(project_id)
        project = Project.objects.get(pk=db_id[1])
        user = info.context.user
        try:
            user.projects.remove(project)
            success=True
        except:
            success=False
        return OutProject(success=True)

class isJoined(graphene.Mutation):
    class Arguments:
        project_id = graphene.String(required=True)
        token = graphene.String()

    is_joined = graphene.Boolean()

    @staticmethod
    def mutate(self, info, project_id=None, token=None):
        if token:
            db_id = from_global_id(project_id)
            project = Project.objects.get(pk=db_id[1])
            if project.users.filter(pk=info.context.user.uuid).exists():
                is_joined=True
            else:
                is_joined=False
        else:
            is_joined=False
        return isJoined(is_joined=is_joined)

class Mutation(graphene.ObjectType):
    create_project = CreateProject.Field()
    update_project = UpdateProject.Field()
    join_project = JoinProject.Field()
    out_project = OutProject.Field()
    is_joined = isJoined.Field()

import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required

from users.models import User,Course,Team,University,Department,Like

from django.core.mail import send_mail
from graphql_relay.node.node import from_global_id
from graphene_file_upload.scalars import Upload


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

class LikeNode(DjangoObjectType):
    class Meta:
        model = Like
        filter_fields = {
            'user': ['exact'],
            'project': ['exact'],
            'created_at': ['exact'],
        }
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    viewer = graphene.Field(UserNode, token=graphene.String(required=True))

    @login_required
    def resolve_viewer(self, info, **kwargs):
        return info.context.user

    user = relay.Node.Field(UserNode)
    all_users = DjangoFilterConnectionField(UserNode)

    like = relay.Node.Field(LikeNode)
    all_likes = DjangoFilterConnectionField(LikeNode)

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


class UserInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    content = graphene.String()
    header = graphene.String()
    logo = graphene.String()
    url = graphene.String()
    position = graphene.String()
    tags = graphene.List(graphene.String)
    # is_public = graphene.Boolean()

class CreateUser(graphene.Mutation):
    class Arguments:
        user_data =UserInput()
        token = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None,user_data=None):
        user = User.objects.create(
            email = user_data.email,
            usernmae = user_data.usernmae,
            password = user_data.password,
            content = user_data.content,
            header = user_data.header,
            logo = user_data.logo,
            url = user_data.url,
            position = user_data.position,
        )
        if user_data.tags:
            for tag in user_data.tags:
                user.tags.add(Tag.objects.get(name=tag))
        send_mail('Subject here','Here is the message.','from@example.com',['to@example.com'])
        return CreateUser(user=user)

class UpdateUserInput(graphene.InputObjectType):
    name = graphene.String()
    email = graphene.String()
    content = graphene.String()
    header = graphene.String()
    logo = graphene.String()
    url = graphene.String()
    position = graphene.String()
    tags = graphene.List(graphene.String)

class UpdateUser(graphene.Mutation):
    class Arguments:
        user_data = UpdateUserInput()
        token = graphene.String(required=True)

    user = graphene.Field(UserNode)

    @staticmethod
    @login_required
    def mutate(root, info, token=None,user_data=None):
        user = info.context.user
        if user_data.name:  user.name = user_data.name
        if user_data.email:  user.email = user_data.email
        if user_data.content:  user.content = user_data.content
        if user_data.header:  user.header = user_data.header
        if user_data.logo:  user.logo = user_data.logo
        if user_data.url:  user.url = user_data.url
        if user_data.position:  user.position = user_data.position
        user.save()
        if user_data.tags:
            for tag in user_data.tags:
                user.tags.add(Tag.objects.get(name=tag))
        return UpdateUser(user=user)

class ChangePassword(graphene.Mutation):
    class Arguments:
        new_password = graphene.String()
        old_password = graphene.String()
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, token=None,new_password=None, old_password=None):
        try:
            user = info.context.user
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                success = True
            else:
                success = False
        except:
            success = False
        return ChangePassword(success=success)

class Liked(graphene.Mutation):
    class Arguments:
        like_id = graphene.String()
        project_id = graphene.String()
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, project_id=None, is_liked=None, like_id=None):
        if like_id:
            db_id = from_global_id(like_id)
            like = Like.objects.get(pk=db_id[1])
            like.delete()
        else:
            db_id = from_global_id(project_id)
            project = Project.objects.get(pk=db_id[1])
            Like.objects.create(
                user=info.context.user,
                project=project
            )
        return Liked(success=True)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    change_password = ChangePassword.Field()
    liked = Liked.Field()
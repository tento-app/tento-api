import graphene

from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from graphql_jwt.decorators import login_required

from users.models import User,Course,Team,University,Department,Like
from gql.models import Project, Tag

from django.core.mail import send_mail
from graphql_relay.node.node import from_global_id
from graphene_file_upload.scalars import Upload
import re
from graphql import GraphQLError

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
    all_likes = DjangoFilterConnectionField(LikeNode, token=graphene.String(required=True))
    @login_required
    def resolve_all_likes(self, info, **kwargs):
        return Like.objects.filter(user=info.context.user).order_by('-created_at')

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
    username = graphene.String(required=True)
    password = graphene.String(required=True)
    email = graphene.String(required=True)
    content = graphene.String()
    header = Upload()
    logo = Upload()
    url = graphene.String()
    position = graphene.String()
    tags = graphene.List(graphene.String)
    # is_public = graphene.Boolean()

class validateUser(object):
    def valUsername(self,username):
        if username:
            val_username = re.compile(r'^[a-zA-Z0-9_]{1,30}$')
            if val_username.match(username) is not None: return True
        raise GraphQLError("username_error")


    def valPassword(self,password):
        if password:
            val_password = re.compile(r'^[a-zA-Z0-9!-~︰-＠]{6,100}$')
            if val_password.match(password) is not None: return True
        raise GraphQLError("password_error")

    def valEmail(self,email):
        if email:
            val_email = re.compile('[A-Za-z0-9\._+]+@[A-Za-z]+\.[A-Za-z]')
            if val_email.match(email) is not None: return True
        raise GraphQLError("email_error")

class CreateUser(graphene.Mutation):
    class Arguments:
        user_data =UserInput(required=True)

    user = graphene.Field(UserNode)

    @staticmethod
    def mutate(root, info, user_data=None):
        validateUsers = validateUser()
        if validateUsers.valUsername(user_data.username) and validateUsers.valPassword(user_data.password) and validateUsers.valEmail(user_data.email):
            user = User(
                email = user_data.email,
                username = user_data.username,
                content = user_data.content,
                header = user_data.header,
                thumbnail=user_data.header,
                logo = user_data.logo,
                url = user_data.url,
                position = user_data.position,
            )
            user.set_password(user_data.password)
            if user_data.tags:
                for tag in user_data.tags:
                    user.tags.add(Tag.objects.get(name=tag))
            user.save()
            send_mail('Subject here','Here is the message.','from@example.com',['to@example.com'])
        return CreateUser(user=user)

class UpdateUserInput(graphene.InputObjectType):
    username = graphene.String()
    email = graphene.String()
    content = graphene.String()
    header = Upload()
    logo = Upload()
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
        validateUsers = validateUser()
        user = info.context.user
        if user_data.username:
            if validateUsers.valUsername(user_data.username):  user.username = user_data.username
        if user_data.email:
            if validateUsers.valEmail(user_data.email):  user.email = user_data.email
        if user_data.content:  user.content = user_data.content
        if user_data.header:
            user.header = user_data.header
            user.thumbnail = user_data.header
        if user_data.logo:  user.logo = user_data.logo
        if user_data.url:  user.url = user_data.url
        if user_data.position:  user.position = user_data.position
        user.save()
        if user_data.tags:
            now_tags = user.tags.values_list('name', flat=True)
            new_tags = user_data.tags
            add_tags = list(set(new_tags)-set(now_tags))
            if add_tags:
                for tag in add_tags:
                    user.tags.add(Tag.objects.get(name=tag))
            remove_tags = list(set(now_tags)-set(new_tags))
            if remove_tags:
                for tag in remove_tags:
                    user.tags.remove(Tag.objects.get(name=tag))
        return UpdateUser(user=user)

class ChangePassword(graphene.Mutation):
    class Arguments:
        new_password = graphene.String(required=True)
        old_password = graphene.String(required=True)
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(root, info, token=None,new_password=None, old_password=None):
        validateUsers = validateUser()
        if validateUsers.valPassword(new_password) and validateUsers.valPassword(old_password):
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
        else:
            success = False
        return ChangePassword(success=success)

class Liked(graphene.Mutation):
    class Arguments:
        project_id = graphene.String(required=True)
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, project_id=None, token=None):
        try:
            db_id = from_global_id(project_id)
            project = Project.objects.get(pk=db_id[1])
            try:
                old_like = Like.objects.get(user=info.context.user,project=project)
                old_like.delete()
                Like.objects.create(user=info.context.user,project=project)
            except:
                Like.objects.create(user=info.context.user,project=project)
            success=True
        except:
            success=False
        return Liked(success=success)

class Unliked(graphene.Mutation):
    class Arguments:
        project_id = graphene.String(required=True)
        token = graphene.String(required=True)

    success = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, project_id=None, token=None):
        try:
            db_id = from_global_id(project_id)
            project = Project.objects.get(pk=db_id[1])
            like = Like.objects.get(user=info.context.user,project=project)
            like.delete()
            success=True
        except:
            success=False
        return Liked(success=success)

class isLiked(graphene.Mutation):
    class Arguments:
        project_id = graphene.String(required=True)
        token = graphene.String(required=True)

    is_liked = graphene.Boolean()

    @staticmethod
    @login_required
    def mutate(self, info, project_id=None, token=None):
        if token:
            db_id = from_global_id(project_id)
            project = Project.objects.get(pk=db_id[1])
            if Like.objects.filter(user=info.context.user,project=project).exists():
                is_liked=True
            else:
                is_liked=False
        else:
            is_liked=False
        return isLiked(is_liked=is_liked)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    change_password = ChangePassword.Field()
    liked = Liked.Field()
    unliked = Unliked.Field()
    is_liked = isLiked.Field()
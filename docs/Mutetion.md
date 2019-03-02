# mutaion example
## createProject
mutation
```graphql
mutation($token: String!,$ProjectInput: ProjectInput!) {
  createProject(token:$token,projectData:$ProjectInput){
    project{
      name
    }
  }
}
```
VARIABLES
```json
{
  "token":"xxxx",
  "ProjectInput":{
    "name":"project1",
    "content":"# project1 \n hello",
    "tags":["vue","python"],
    "logo":"https://pbs.twimg.com/profile_images/1088462659215712257/w68hx_Mi_400x400.jpg",
    "url":"https://ark-cg.com/"
  }
}
```
## updateProject
mutation
```graphql
mutation($token: String!,$project_id: String!, $ProjectInput: ProjectInput!) {
  updateProject(token:$token,projectId:$project_id,projectData:$ProjectInput){
    project{
      name
    }
  }
}
```
VARIABLES
```json
{
  "token":"xxx",
    "project_id":"UHJvamVjdE5vZGU6Mw==",
  "ProjectInput":{
    "name":"project1-1"
  }
}
```
## changePassword
mutation
```graphql
mutation($token: String!,$new_password: String!,$old_password: String!) {
  changePassword(token:$token,newPassword:$new_password, oldPassword: $old_password){
    user{
      username
    }
  }
}
```
VARIABLES
```json
{
  "token":"xxxxxx",
  "old_password":"xxxxx",
  "new_password":"xxxxx"
}
```
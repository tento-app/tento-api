# API based on graphene for tento
## Auth

```graphql
mutation ($username: String!, $password: String!) {
  authToken(username: $username, password: $password) {
    token
  }
}
# variables
{
  "username": "xxxx",
  "password": "xxxx"
}
```

```graphql
{
  joinTeams(token: "xxxx") {
    edges {
      node {
        name
      }
    }
  }
}
```

## Reference

https://docs.graphene-python.org/en/latest/

https://django-filter.readthedocs.io/en/master/guide/usage.html#request-based-filtering

https://github.com/eamigo86/graphene-django-extras

https://qiita.com/okoppe8/items/10ae61808dc3056f9c8e


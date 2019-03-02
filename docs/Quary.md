# Quary example

```graphql
{
  allProjects(first:2, after: ""){
    edges{
      node{
        id
        name
        createdAt
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```
use pageInfo.endCursor to after
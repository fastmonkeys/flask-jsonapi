| Endpoint                      | Method   | URL rule                            |          |          |           |        |        |
| ----------------------------- | -------- | ----------------------------------- | -------- | -------- | --------- | -------| ------ |
| `books.self`                  | `GET`    | `/books`                            | `fields` | `filter` | `include` | `page` | `sort` |
|                               | `POST`   | `/books`                            | `fields` |          | `include` |        |        |
|                               | `GET`    | `/books/:id`                        | `fields` |          | `include` |        |        |
|                               | `PATCH`  | `/books/:id`                        | `fields` |          | `include` |        |        |
|                               | `DELETE` | `/books/:id`                        |          |          |           |        |        |
| `books.related_author`        | `GET`    | `/books/:id/author`                 | `fields` |          | `include` |        |        |
| `books.related_chapters`      | `GET`    | `/books/:id/chapters`               | `fields` | `filter` | `include` | `page` | `sort` |
| `books.relationship_author`   | `GET`    | `/books/:id/relationships/author`   |          |          |           |        |        |
|                               | `PATCH`  | `/books/:id/relationships/author`   |          |          |           |        |        |
| `books.relationship_chapters` | `GET`    | `/books/:id/relationships/chapters` |          | `filter` |           | `page` | `sort` |
|                               | `PATCH`  | `/books/:id/relationships/chapters` |          |          |           |        |        |
|                               | `POST`   | `/books/:id/relationships/chapters` |          |          |           |        |        |
|                               | `DELETE` | `/books/:id/relationships/chapters` |          |          |           |        |        |

```python
request = JSONAPIRequest(
    type='books',
    id='1',
    relationship_name='author',
    data=request.data,
    query_params=request.args
)
request.type                 # the resource type, e.g. `"books"`
request.resource             # the `Resource` object of the requested resource type
request.id                   # the ID of the requested individual resource, e.g. `"1"`, or `None` if not applicable for this request
request.relationship_name    # the name of the requested relationship, e.g. `"author"`, or `None` if not applicable for this request
request.relationship         # the `Relationship` object of the requested relationship, or `None` if not applicable for this request
request.related_type         # the resource type of the relationship, e.g. `"authors"`, or `None` if not applicable for this request
request.related_resource     
request.fields               # parsed `fields` query parameter, e.g. `{"authors": {"name"}, "books": {"title", "author"}}`
request.filter
request.include              # parsed `include` query parameter, e.g. `{"comments": {"author": {}}, "author": {}}`
request.page                 # parsed `page` query parameter, an instance of `Pagination` class
request.sort                 # parsed `sort` query parameter, e.g. `["-created", "title"]`
request.self_link            # the requested URL
request.json                 # JSON-encoded content of the request body
```

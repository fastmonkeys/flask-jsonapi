- JSON API serialization needs to know how to construct URLs for different
  resources. URL generation must be customizable for:
    - resource collections
        - Default: "/:type"
        - Example "/photos"
    - individual resources
        - Default: "/:type/:id"
        - Example "/photos/1"
    - relationships
        - Default: "/:type/:id/relationships/:relationship"
        - Example: "/photos/1/relationships/comments"
    - related resources
        - Default: "/:type/:id/:relationship"
        - Example: "/photos/1/comments"
- JSON API deserialization needs to be able to transform resource identifier
  objects to the actual resource object. This must be customizable.


Resource MUST have:
    - type
    - schema for serialization/deserialization
    - repository for CRUD

Resource instance MUST have:
    - id
        - serializable to a string -- `str(id)`
        - can parse from string -- `type_name(id_as_str)`

- How does authentication and authorization work?
- How to define what actions (fetch, save, update, delete, etc.) are available for each resource?
- Validation
    - How to validate a complete resource (i.e. when creating a resouce)?
    - How to validate a partial resource?
        - when updating a resource
        - when replacing a to-one relationship
        - when replacing a to-many relationship
        - when adding to to-many relationship
        - when removing from to-many relationship
        - use signals/hooks and leave as user's responsibility?
    - How to validate relationships?
        - Does the related resource exist?
            - Schema needs to be able to access the related resource's
              repository to fetch the related resource.
        - Is this resource instance allowed to be set to the relation?
            - just add a validator to the relationship field in the schema

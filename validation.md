Validation
----------

Operations that need validation:

- create
- update
- replace to-one relationship
- replace to-many relationship
- add to to-many relationship
- remove from to-many relationship

Possible validations related to attributes:

- required
- is the value of correct type and format?
- coerce the json value to proper python object
- dependencies to other fields in the resource, e.g. start date cannot be after end date

Possible validations related to to-one relationships:

- required (can the relationship be null?)
- is the resource of correct type? does the given resource exist? (these should probably be validated automatically by the json:api library)
- does the related resource fulfill certain requirements? (e.g. does the given target belong to the same organization as the template)
- dependencies to other fields in the resource, e.g. salesperson1 must be different from saleperson2

Possible validations related to to-many relationships:

- minimum/maximum number of related resources


Solution:

Option A:
  - pre-validation
    - validate attributes and relationships before they are assigned to the object
  - post-validation
    - validate the object after all attributes and relationships have been assigned, but before the resource is saved to the database

Option B:
    - model layer responsible for validation, the library will catch any exceptions raised when setting an attribute

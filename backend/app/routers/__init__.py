from uuid import UUID


# Define a custom JSON schema for PydanticObjectId
def custom_pydantic_object_id_schema(schema: dict, handler):
    # Call the handler to process the schema and then modify it
    base_schema = handler(schema)
    base_schema.update({"type": "string", "format": "objectid", "example": "507f1f77bcf86cd799439011"})
    return base_schema


# Create a custom subclass of UUID
class CustomUUID(UUID):
    @staticmethod
    def __get_pydantic_json_schema__(schema: dict, handler):
        return custom_pydantic_object_id_schema(schema, handler)

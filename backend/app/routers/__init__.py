#from uuid import UUID

#TODO Its not working in reson of Pydantic V2

# Define a custom JSON schema for PydanticObjectId
#def custom_pydantic_object_id_schema(schema: dict):
#    return {
#        "type": "string",
#        "format": "objectid",
#        "example": "507f1f77bcf86cd799439011"
#    }

# Register the custom schema with Pydantic
#UUID.__get_pydantic_json_schema__ = custom_pydantic_object_id_schema

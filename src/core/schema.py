from pydantic import BaseModel, ConfigDict


class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

import datetime

from pydantic import BaseModel, ConfigDict

from src.utilities.formatters.datetime_formatter import format_datetime_into_isoformat
from src.utilities.formatters.field_formatter import format_dict_key_to_camel_case

class BaseSchemaModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        json_encoders={
            datetime.datetime: format_datetime_into_isoformat
        },
        alias_generator=format_dict_key_to_camel_case
    )
from typing import Optional

from pydantic import BaseModel, Field


class XPathTestRequest(BaseModel):
    base_xml: str = Field(min_length=1, max_length=500_000)
    xpath_expression: str = Field(min_length=1, max_length=2_000)
    position: str = Field(default="inside")
    inherited_xml: Optional[str] = Field(default="", max_length=200_000)

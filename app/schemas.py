from pydantic import BaseModel
from typing import List


class Recipient(BaseModel):
    name: str


class GenerationRequest(BaseModel):
    event_name: str
    certificate_title: str
    issue_date: str
    recipients: List[Recipient]
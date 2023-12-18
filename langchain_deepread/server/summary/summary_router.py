import logging
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from typing import Any
from langchain_deepread.server.utils.auth import authenticated
from langchain_deepread.server.summary.summary_service import (
    SummaryService,
    SummaryResponse,
)
from langchain_deepread.server.utils.model import RestfulModel

logger = logging.getLogger(__name__)

summary_router = APIRouter(prefix="/v1", dependencies=[Depends(authenticated)])


class SummaryBody(BaseModel):
    documents: str
    one_words_length: int = Field(default=30, description="One-sentence summary length")
    title_length: int = Field(default=10, description="Article Title length")
    outline_nums: int = Field(default=3, description="Article reading outline nums")
    tag_nums: int = Field(default=10, description="Article Tag nums")
    qa_nums: int = Field(default=3, description="Article QA nums")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "documents": "xxx",
                    "one_words_length": 30,
                    "title_length": 10,
                    "outline_nums": 3,
                    "tag_nums": 10,
                    "qa_nums": 3,
                }
            ]
        }
    }


@summary_router.post(
    "/summary",
    response_model=RestfulModel[SummaryResponse | None],
    tags=["Summary"],
)
def summary(request: Request, body: SummaryBody) -> RestfulModel:
    """
    Summarize the article based on the given content and requirements
    """
    service = request.state.injector.get(SummaryService)
    return RestfulModel(data=service.summary(**body.model_dump()))

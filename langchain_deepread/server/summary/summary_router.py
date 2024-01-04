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
    content_nums: int = Field(
        default=5, description="Summary of the main points of the article"
    )
    one_content_length: int = Field(
        default=20, description="Minimum length of article points"
    )
    title_length: int = Field(default=10, description="Article Title length")
    section_title_length: int = Field(default=10, description="Paragraph heading")
    section_list_length: int = Field(
        default=2, description="Paragraph sum up the number of ideas"
    )
    one_section_length: int = Field(
        default=20, description=" length of paragraph summarizing ideas"
    )
    min_section_nums: int = Field(default=5, description="Minimum number of paragraphs")
    max_section_nums: int = Field(
        default=10, description="Maximum number of paragraphs"
    )
    tag_nums: int = Field(default=10, description="Maximum Article Tag nums")
    qa_nums: int = Field(default=3, description="Minimum Article QA nums")
    recommend_nums: int = Field(default=3, description="Minimum Article recommend nums")
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "documents": "xxxx",
                    "one_words_length": 30,
                    "content_nums": 5,
                    "one_content_length": 20,
                    "title_length": 10,
                    "section_title_length": 10,
                    "section_list_length": 2,
                    "one_section_length": 20,
                    "min_section_nums": 5,
                    "max_section_nums": 10,
                    "tag_nums": 10,
                    "qa_nums": 3,
                    "recommend_nums": 3,
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

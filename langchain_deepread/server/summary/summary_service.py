from injector import inject, singleton
from langchain_deepread.components.llm.llm_component import LLMComponent
from langchain.schema.output_parser import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.runnable import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableLambda,
)
from langchain_deepread.server.summary.summary_prompt import (
    SummaryParam,
    MergeSummaryParam,
    SummarizationPromptTemplate,
    MergeSummarizationPromptTemplate,
)
from langchain.callbacks import get_openai_callback
from pydantic import BaseModel, Field
import json
import logging
from langchain.text_splitter import CharacterTextSplitter
import tiktoken
from langchain_deepread.settings.settings import Settings

logger = logging.getLogger(__name__)

"""
summary: "One-sentence summary"
content: "Main points of the article"
title: "Article Title"
outline: "Article reading outline"
tags: "Article Tags"
qa: "Article QA"
"""


class GPTResponse(BaseModel):
    summary: str
    content: list[str]
    title: str
    outline: list[dict]
    tags: list[str]
    qa: list[str]


class TokenInfo(BaseModel):
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0


class SummaryResponse(BaseModel):
    gptresponse: GPTResponse = Field(description="gpt response summary")
    token_info: TokenInfo = Field(description="Token Info")


@singleton
class SummaryService:
    @inject
    def __init__(self, llm_component: LLMComponent, settings: Settings) -> None:
        self.llm_service = llm_component
        self.max_summary_length = 14500  # 14500个Token长度

    def summary(self, **kwargs) -> SummaryResponse | None:
        # 获取全文长度
        doc_length = self.num_tokens_from_string(kwargs["documents"])
        print(doc_length)
        if doc_length <= self.max_summary_length:
            return self.short_summary(**kwargs)

        return self.long_summary(doc_length, **kwargs)

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self.llm_service.modelname)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    """
    短片文章总结
    """

    def short_summary(self, **kwargs) -> SummaryResponse | None:
        output_parser = StrOutputParser()
        resobj = None
        try:
            sp = SummaryParam(**kwargs)
            chain = SummarizationPromptTemplate | self.llm_service.llm | output_parser

            with get_openai_callback() as cb:
                ret = chain.invoke(sp.model_dump())
                gptresponse = json.loads(ret)
                tokeninfo = TokenInfo(
                    total_tokens=cb.total_tokens,
                    prompt_tokens=cb.prompt_tokens,
                    completion_tokens=cb.completion_tokens,
                    successful_requests=cb.successful_requests,
                    total_cost=cb.total_cost,
                )
                resobj = SummaryResponse(
                    token_info=tokeninfo, gptresponse=GPTResponse(**gptresponse)
                )
        except Exception as e:
            logger.exception(e)
        return resobj

    """
    长篇文章总结
    """

    def long_summary(self, doc_length: int, **kwargs) -> SummaryResponse | None:
        text_splitter = None
        if doc_length <= 16000:
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                model_name=self.llm_service.modelname,
                separator="\n",
                chunk_size=9000,
                chunk_overlap=0,
            )
        elif 16000 < doc_length and doc_length <= 20000:
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                model_name=self.llm_service.modelname,
                separator="\n",
                chunk_size=11000,
                chunk_overlap=0,
            )
        elif 20000 < doc_length and doc_length <= 24000:
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                model_name=self.llm_service.modelname,
                separator="\n",
                chunk_size=13000,
                chunk_overlap=0,
            )
        else:
            text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
                model_name=self.llm_service.modelname,
                separator="\n",
                chunk_size=11000,
                chunk_overlap=0,
            )

        docs = text_splitter.split_text(kwargs.pop("documents"))
        for res in docs:
            print(res)
            print()
        print("--------------")
        sp_list = []
        for doc in docs:
            sp = SummaryParam(documents=doc, **kwargs)
            sp_list.append(sp.model_dump())

        resobj = None
        try:
            summary_chain = (
                SummarizationPromptTemplate | self.llm_service.llm | StrOutputParser()
            )

            merge_chain = (
                MergeSummarizationPromptTemplate
                | self.llm_service.llm
                | StrOutputParser()
            )

            with get_openai_callback() as cb:
                summary_res_list = summary_chain.batch(sp_list)
                print(len(summary_res_list))
                for res in summary_res_list:
                    print(res)
                    print()
                print("------------------")
                merge_doc = ""
                for summary_res in summary_res_list:
                    merge_doc += "\n<div>\n" + summary_res + "\n</div>\n"
                sp = SummaryParam(documents=merge_doc, **kwargs)
                print(MergeSummarizationPromptTemplate.invoke(sp.model_dump()))
                ret = merge_chain.invoke(sp.model_dump())  # 合并总结内容
                print(ret)
                gptresponse = json.loads(ret)
                print(gptresponse)
                tokeninfo = TokenInfo(
                    total_tokens=cb.total_tokens,
                    prompt_tokens=cb.prompt_tokens,
                    completion_tokens=cb.completion_tokens,
                    successful_requests=cb.successful_requests,
                    total_cost=cb.total_cost,
                )
                print(tokeninfo)

                resobj = SummaryResponse(
                    token_info=tokeninfo, gptresponse=GPTResponse(**gptresponse)
                )

        except Exception as e:
            logger.exception(e)
        return resobj
        # merge_list = []
        # for i in range(len(summary_res_list) / 2):
        #     msp = MergeSummaryParam(
        #         fisrt_summary=summary_res_list[i * 2],
        #         second_summary=summary_res_list[i * 2 + 1],
        #     )
        #     merge_list.append[msp.model_dump()]

        # merge_res_list = merge_chain.batch(merge_list)

        # if len(summary_res_list) % 2:
        # 奇数个

from langchain.prompts import StringPromptTemplate
from langchain.prompts import ChatPromptTemplate
from pydantic import v1 as pydantic_v1
from pydantic import BaseModel


class SummaryParam(BaseModel):
    documents: str
    one_words_length: int = 30
    title_length: int = 10
    outline_nums: int = 3
    tag_nums: int = 10
    qa_nums: int = 3
    # output_format: str


SUMMARY_PROMPT = """\
# Role: 一个中文文章总结专家，擅长进行微信公众号、小红书等在线文章总结

## Language: 中文

## Workflow
1. 分析文章##Article Content的内容
3. 输出针对这篇文章的一句话总结，长度不超过{one_words_length}个字,记录为summary
4. 按列表输出针对这篇文章的关键信息点,个数必须大于5个,记录为content
5. 输出针对这篇文章的文章标题，长度不超过{title_length}个字,记录为title
6. 必须采用MarkDown格式,按H2标题或列表形式,分要点输出针对这篇文章的大纲, H2标题段落一定大于{outline_nums}段,记录为outline
7. 按列表输出针对这篇文章的标签，不超过{tag_nums}个
8. 按列表输出针对这篇文章的{qa_nums}个QA问答,记录为qa

## Output format
<div>
The output should be formatted as a JSON instance that conforms to the JSON schema below.
summary: str
content: list[str]
title: str
outline: str
tags: list[str]
qa: list[str]
As an example, for the schema
{{"summary": "", "content": ["", ""], "title": "", "outline": "", "tags": ["", ""], "qa": ["Q:xxx\\nA:xxx\\n"]}}
</div>

## Article Content
<div>
{documents}
</div>

## Start
作为一个 #Role, 你默认使用的是##Language,你不需要介绍自己,请根据##Workflow开始工作,你必须遵守输出格式##Output format
"""

SummarizationPromptTemplate = ChatPromptTemplate.from_template(SUMMARY_PROMPT)


# class SummarizationPromptTemplate(StringPromptTemplate, pydantic_v1.BaseModel):
#     # 文档总结PROMPT
#     SUMMARY_PROMPT = """\
#     # Role: 一个中文文章总结专家，擅长进行微信公众号、小红书等在线文章总结

#     ## Language: 中文

#     ## Workflow
#     1. 分析文章##Article Content的内容
#     3. 输出针对这篇文章的一句话总结，长度不超过{one_words_length}个字，记录为summary
#     4. 按列表输出针对这篇文章的关键信息点，记录为content
#     5. 输出针对这篇文章的文章标题，长度不超过{title_length}个字，记录为title
#     6. 采用MarkDown格式，按H2以上标题或列表形式，分要点输出针对这篇文章的大纲, 大纲段落一定大于{outline_nums}段，记录为outline
#     7. 按列表输出针对这篇文章的标签，不超过{tag_nums}个
#     8. 按列表输出针对这篇文章的{qa_nums}个QA问答，记录为qa


#     ## Output format
#     <div>
#     {output_format}
#     </div>

#     ## Article Content
#     <div>
#     {documents}
#     </div>

#     ## Start
#     作为一个 #Role, 你默认使用的是##Language，你不需要介绍自己，请根据##Workflow开始工作，你必须遵守输出格式##Output format
#     """

#     @pydantic_v1.validator("input_variables")
#     def validate_input_variables(cls, v):
#         """Validate that the input variables are correct."""
#         if (
#             len(v) != 7
#             or "documents" not in v
#             or "one_words_length" not in v
#             or "title_length" not in v
#             or "outline_nums" not in v
#             or "tag_nums" not in v
#             or "qa_nums" not in v
#             or "output_format" not in v
#         ):
#             raise ValueError(
#                 "(documents one_words_length title_length outline_nums tag_nums qa_nums output_format) must be the only input_variable."
#             )
#         return v

#     def format(self, **kwargs) -> str:
#         prompt = self.SUMMARY_PROMPT.format(
#             documents=kwargs["documents"],
#             one_words_length=kwargs["one_words_length"],
#             title_length=kwargs["title_length"],
#             outline_nums=kwargs["outline_nums"],
#             tag_nums=kwargs["tag_nums"],
#             qa_nums=kwargs["qa_nums"],
#             output_format=kwargs["output_format"],
#         )
#         return prompt

#     def _prompt_type(self):
#         return "summarization-documents"


class MergeSummaryParam(BaseModel):
    documents: str
    one_words_length: int = 30
    title_length: int = 10
    outline_nums: int = 3
    tag_nums: int = 10
    qa_nums: int = 3


# 合并总结Prompt
MERGE_SUMMARY_PROMPT = """\
# Role: 一位文章总结专家

## Language: 中文

## Json Content
{documents}

## Output format
<div>
The output should be formatted as a JSON instance that conforms to the JSON schema below.
summary: str
content: list[str]
title: str
outline: str
tags: list[str]
qa: list[str]
As an example, for the schema
{{"summary": "", "content": ["", ""], "title": "", "outline": "", "tags": ["", ""], "qa": ["Q:xxx\\nA:xxx\\n"]}}
</div>

## Workflow
1. ##Json Content的内容为一篇文章的多个总结部分
2. 将多个summary含义融合输出为1个summary,长度不能超过{one_words_length}个字符
3. 将多个content按上下顺序合并成一个,个数必须大于5个
4. 将多个title含义融合输出为1个title,长度不能超过{title_length}个字符
5. 将多个outline按上下顺序拼接成一个,必须采用MarkDown格式,按H2以上标题或列表形式,分要点输出针对这篇文章的大纲, 大纲段落一定大于{outline_nums}段,记录为outline
6. 将多个tags含义融合,严格限定不超过{tag_nums}个tag
7. 将多个qa含义融合,严格限定输出{qa_nums}条QA记录
8. 输出格式保持##Output format不变,返回合并后的json

## Start
作为一个 #Role, 你默认使用的是##Language,你不需要介绍自己,请根据##Workflow开始工作,你必须遵守输出格式##Output format
"""

MergeSummarizationPromptTemplate = ChatPromptTemplate.from_template(
    MERGE_SUMMARY_PROMPT
)


# class MergeSummarizationPromptTemplate(StringPromptTemplate, pydantic_v1.BaseModel):
#     # 合并总结Prompt
#     MERGE_SUMMARY_PROMPT = """\
#     # Role: 一位文章总结专家

#     ## Language: 中文

#     ## Json Content
#     <div>
#     {fisrt_summary}
#     </div>

#     <div>
#     {second_summary}
#     </div>

#     ## Output format
#     <div>
#     {output_format}
#     </div>

#     ## Workflow
#     1. ##Json Content的内容为一篇文章的上下两部分
#     2. 将两个summary含义融合输出为1个summary，长度不能超过30个字符
#     3. 将两个content按上下顺序合并成一个
#     4. 将两个title含义融合输出为1个title，长度不能超过10个字符
#     5. 将两个outline按上下顺序合并成一个,采用MarkDown格式，按H2以上标题或列表形式输出, 输出的大纲段落一定大于3段
#     6. 将两个tags含义融合，严格限定不超过10个tag
#     7. 将两个qa含义融合,严格限定输出3条QA记录
#     8. 输出格式保持##Output format不变,返回合并后的json

#     ## Start
#     作为一个 #Role, 你默认使用的是##Language，你不需要介绍自己，请根据##Workflow开始工作，你必须遵守输出格式##Output format
#     """

#     @pydantic_v1.validator("input_variables")
#     def validate_input_variables(cls, v):
#         """Validate that the input variables are correct."""
#         if (
#             len(v) != 3
#             or "fisrt_summary" not in v
#             or "second_summary" not in v
#             or "output_format" not in v
#         ):
#             raise ValueError(
#                 "(fisrt_summary second_summary output_format) must be the only input_variable."
#             )
#         return v

#     def format(self, **kwargs) -> str:
#         prompt = self.MERGE_SUMMARY_PROMPT.format(
#             fisrt_summary=kwargs["fisrt_summary"],
#             second_summary=kwargs["second_summary"],
#             output_format=kwargs["output_format"],
#         )
#         return prompt

#     def _prompt_type(self):
#         return "merge-summarization-documents"


# if __name__ == "__main__":
#     sp = SummaryParam(documents="xxxx", output_format="aaa")
#     s = SummarizationPromptTemplate(
#         input_variables=[
#             "documents",
#             "one_words_length",
#             "title_length",
#             "outline_nums",
#             "tag_nums",
#             "qa_nums",
#             "output_format",
#         ]
#     )
#     print(s.format(**sp.model_dump()))

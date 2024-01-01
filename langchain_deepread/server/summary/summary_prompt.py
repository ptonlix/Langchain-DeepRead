from langchain.prompts import StringPromptTemplate
from langchain.prompts import ChatPromptTemplate
from pydantic import v1 as pydantic_v1
from pydantic import BaseModel
from langchain.prompts import HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_core.messages import SystemMessage
import datetime


class SummaryParam(BaseModel):
    documents: str
    one_words_length: int = 30
    content_nums: int = 5
    one_content_length: int = 20
    title_length: int = 10
    section_title_length: int = 10
    section_list_length: int = 2
    one_section_length: int = 20
    min_section_nums: int = 5
    max_section_nums: int = 10
    tag_nums: int = 10
    qa_nums: int = 3
    recommend_nums: int = 3
    datetime: str = str(datetime.date.today())
    # output_format: str


SUMMARY_PROMPT = """\
# Role: 一个中文文章总结专家，擅长进行微信公众号、小红书等在线文章总结

## Language: 中文

## Workflow
1. 分析文章##Article Content的内容
3. 输出针对这篇文章的一句话总结，长度不超过{one_words_length}个字,记录为summary
4. 按列表输出针对这篇文章的关键信息点,个数必须大于{content_nums}个,每个长度必须大于{one_content_length}个字,记录为content
5. 输出针对这篇文章的文章标题，长度不超过{title_length}个字,记录为title
6. 分析文章的主要段落,输出每一个段落的主题,记录为section_title,长度大于{section_title_length}个字;\
    按列表输出每一个段落的关键信息,记录为section_list,列表项必须大于{section_list_length}个,长度必须大于{one_section_length}个字;\
        将一个段落主题和关键信息组合成一个对象,将全部对象组成一个列表输出,记录为outline。outline列表对象包含个数一定大于{min_section_nums}个和小于{max_section_nums}个。
7. 按列表输出针对这篇文章的标签，不超过{tag_nums}个
8. 按列表输出针对这篇文章的{qa_nums}个QA问答,记录为qa
9. 按列表输出针对这篇文章的{recommend_nums}个阅读推荐语,记录为recommends

## Output format
<div>
The output should be formatted as a JSON instance that conforms to the JSON schema below.
summary: str
content: list[str]
title: str
outline: list[dict]
tags: list[str]
qa: list[str]
recommends: list[str]
As an example, for the schema
{{"summary": "", "content": ["", ""], "title": "",  "outline":[{{"section_title":"", "section_list":["",""]}}],"tags": ["", ""], "qa": ["Q:xxx\\nA:xxx\\n"],"recommends":["", ""]}}
</div>

## Article Content
<div>
{documents}
</div>

## Start
作为一个 #Role, 你默认使用的是##Language,你不需要介绍自己,请根据##Workflow开始工作,你必须遵守输出格式##Output format
"""
SummarizationPromptTemplate = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are ChatGPT, a large language model trained by OpenAI.\n"
            "Knowledge cutoff: 2022-01\n"
            "Current date: {datetime}"
        ),
        HumanMessagePromptTemplate.from_template(SUMMARY_PROMPT),
    ]
)


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
outline: list[dict]
tags: list[str]
qa: list[str]
recommends: list[str]
As an example, for the schema
{{"summary": "", "content": ["", ""], "title": "",  "outline":[{{"section_title":"", "section_list":["",""]}}],, "tags": ["", ""], "qa": ["Q:xxx\\nA:xxx\\n"],"recommends":["", ""]}}
</div>

## Workflow
1. ##Json Content的内容为一篇文章的多个总结部分
2. 将多个summary含义融合输出为1个summary,长度不能超过{one_words_length}个字符
3. 将多个content按上下顺序合并成一个,个数必须大于{content_nums}个,每个长度必须大于{one_content_length}个字
4. 将多个title含义融合输出为1个title,长度不能超过{title_length}个字符
5. 将多个outline按上下顺序合并成一个, section_title长度大于{section_title_length}个字;\
    section_list中列表项必须大于{section_list_length}个,长度必须大于{one_section_length}个字;\
        outline列表对象包含个数一定大于{min_section_nums}个和小于{max_section_nums}个
6. 将多个tags含义融合,严格限定不超过{tag_nums}个tag
7. 将多个qa含义融合,严格限定输出{qa_nums}条QA记录
8. 将多个recommends含义融合,严格限定输出{recommend_nums}条recommend
9. 输出格式保持##Output format不变,返回合并后的json

## Start
作为一个 #Role, 你默认使用的是##Language,你不需要介绍自己,请根据##Workflow开始工作,你必须遵守输出格式##Output format
"""

MergeSummarizationPromptTemplate = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are ChatGPT, a large language model trained by OpenAI.\n"
            "Knowledge cutoff: 2022-01\n"
            "Current date: {datetime}"
        ),
        HumanMessagePromptTemplate.from_template(MERGE_SUMMARY_PROMPT),
    ]
)

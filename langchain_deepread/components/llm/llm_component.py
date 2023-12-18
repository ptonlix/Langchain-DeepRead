import logging

from injector import inject, singleton
from langchain.chat_models import ChatOpenAI
from langchain.llms.base import BaseLLM
from langchain.llms.fake import FakeListLLM
from langchain_deepread.settings.settings import Settings


logger = logging.getLogger(__name__)


@singleton
class LLMComponent:
    llm: BaseLLM

    @inject
    def __init__(self, settings: Settings) -> None:
        llm_mode = settings.llm.mode
        logger.info("Initializing the LLM in mode=%s", llm_mode)
        self.modelname = settings.openai.modelname
        match settings.llm.mode:
            case "local":
                ...  # Todo
            case "openai":
                openai_settings = settings.openai
                self.llm = ChatOpenAI(
                    temperature=openai_settings.temperature,
                    model_name=openai_settings.modelname,
                    api_key=openai_settings.api_key,
                    openai_api_base=openai_settings.api_base,
                    model_kwargs={"response_format": {"type": "json_object"}},
                )
            case "mock":
                self.llm = FakeListLLM(
                    responses=[
                        '{\n  "summary": "习近平和彭丽媛在河内会见越共总书记阮富仲夫妇，共同构建中越命运共同体。",\n  "content": [\n    "习近平和彭丽媛会见越共总书记阮富仲夫妇",\n    "习近平发表重要讲话，提出对两国青年的希望"\n  ],\n  "title": "中越友好",\n  "outline": "## 习近平和彭丽媛会见越共总书记阮富仲夫妇\\n## 习近平发表重要讲话，提出对两国青年的希望",\n  "tags": ["中越友好", "国际关系", "青年交流"],\n  "qa": [\n    "Q: 习近平在会见中提出了对两国青年的哪些希望？\\nA: 希望他们成为中越友好征程的领跑者，为构建具有战略意义的中越命运共同体贡献力量。",\n    "Q: 会见中提到的中越友好的根基和未来分别是什么？\\nA: 友好的根基在人民，未来在青年。",\n    "Q: 会见中提到的亚太地区长治久安的重要性是什么？\\nA: 亚太地区长治久安对两国安身立命至关重要，开放包容、合作共赢是人间正道。"\n  ]\n}'
                    ]
                )

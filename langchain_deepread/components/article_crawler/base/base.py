from typing import Optional
import requests
import html2text
import time

from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

from parsel import Selector
import logging
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.remote.webdriver import BaseWebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from fake_useragent import UserAgent
import tiktoken
from langchain_deepread.settings.settings import settings

logger = logging.getLogger(__name__)


class Article(BaseModel):
    """文章属性"""

    title: str = Field(description="文章标题")
    author: str = Field(description="文章作者")
    content: str = Field(description="文章正文")
    source: str = Field(description="文章来源")
    token_num: int = Field(description="文章Token总数")


def retry(max_retries=3, delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    result = func(*args, **kwargs)
                    return result  # 如果成功执行函数，直接返回结果
                except NoSuchElementException:
                    logger.warning(f"{func.__name__} Element Empty")
                except Exception as e:
                    logger.exception(e)

                retries += 1
                time.sleep(delay)  # 可以根据需要调整重试之间的等待时间

            return None  # 如果达到最大重试次数仍未成功，返回 None

        return wrapper

    return decorator


class AbstractArticleCrawler(ABC):
    """
    获取文章标题
    """

    @abstractmethod
    def get_article_title(self) -> str | None:
        ...

    """
    获取文章作者
    """

    @abstractmethod
    def get_article_author(self) -> str | None:
        ...

    """
    获取文章内容
    """

    @abstractmethod
    def get_article_content(self) -> str | None:
        ...


class Method:
    """Set of supported crawler."""

    HTTP = "http"
    WEBDRIVER = "webdriver"


class ArticleCrawerBase(AbstractArticleCrawler):
    def __init__(self, source: Optional[str] = "base"):
        self._articleobj = None
        self._source = source
        self._token_model = settings().openai.modelname

    """
    获取文章来源
    """

    def get_article_source(self) -> str | None:
        return self._source

    """
    获取文章标题
    """

    def get_article_title(self) -> str | None:
        return "title"

    """
    获取文章作者
    """

    def get_article_author(self) -> str | None:
        return "author"

    """
    获取文章内容
    """

    def get_article_content(self) -> str | None:
        return "content"

    """
    获取文章token
    """

    def num_tokens_from_string(self, string: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.encoding_for_model(self._token_model)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    """
    获取文章内容
    """

    def _get_article(self) -> Article:
        content = self.get_article_content()
        token_num = self.num_tokens_from_string(content)
        return Article(
            title=self.get_article_title(),
            author=self.get_article_author(),
            content=content,
            source=self.get_article_source(),
            token_num=token_num,
        )

    @property
    def article(self) -> Article | None:
        if not self._articleobj:
            try:
                self._articleobj = self._get_article()
            except Exception as e:
                logger.exception(e)
        return self._articleobj

    """
    刷新文章内容,以便获取新的文章
    """

    def refresh(self):
        self._articleobj = None


class ArticleCrawlerHTTP(ArticleCrawerBase):
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Document</title>
</head>
<body>
{article}
</body>
</html>
"""

    def __init__(
        self,
        title_xpath: str = "",
        author_xpath: str = "",
        content_tag: str = "",
        content_soup: dict = None,
        source: Optional[str] = "http",
    ) -> None:
        super().__init__(source=source)
        self.title_xpath = title_xpath
        self.author_xpath = author_xpath
        self.content_tag = content_tag
        self.content_soup = content_soup

    """
    通过HTTP请求文章
    """

    def article_http(self, url: str) -> Article | None:
        response = requests.get(url=url, headers={"user-agent": UserAgent().random})
        response.encoding = "utf-8"
        self.content_html = response.text if response.status_code == 200 else None
        return self.article

    @property
    def title(self) -> str | None:
        return self.article.title if self.article else None

    @retry()
    def get_article_title(self) -> str | None:
        s = Selector(self.content_html)
        title = s.xpath(self.title_xpath).get()
        if not title:
            logger.error("get Article Title Element Empty")
        return title

    @property
    def author(self) -> str | None:
        return self.article.author if self.article else None

    @retry()
    def get_article_author(self) -> str | None:
        s = Selector(self.content_html)
        author = s.xpath(self.author_xpath).get()
        if not author:
            logger.error("get Article Author Element Empty")
        return author

    @property
    def content(self) -> str | None:
        return self.article.content if self.article else None

    @retry()
    def get_article_content(self) -> str | None:
        soup = BeautifulSoup(self.content_html, "lxml")
        content = soup.find(self.content_tag, **self.content_soup)
        if not content:
            logger.warning("get Article Content Element Empty")
            return content
        h = html2text.HTML2Text()
        h.ignore_images = True
        h.ignore_links = True
        h.body_width = 80
        try:
            html_text = self.HTML_TEMPLATE.format(article=content)
            md = h.handle(html_text)
            markdown_text = self.strip_empty_lines(md)
            return markdown_text
        except Exception as e:
            logger.exception(e)
            return None

    def strip_empty_lines(self, text: str) -> str:
        # 使用 splitlines() 方法将字符串拆分成行
        lines = text.splitlines()

        # 使用列表推导式剔除空行
        non_empty_lines = [line for line in lines if line.strip()]

        # 使用换行符连接非空行
        result_string = "\n".join(non_empty_lines)
        return result_string


"""
利用webdriver 获取
"""


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    def delete_instance():
        if cls in instances:
            del instances[cls]

    get_instance.delete_instance = delete_instance
    return get_instance


@singleton
class WebDriverChrome(webdriver.Chrome):
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )  # 隐藏selenium 特征
        options.add_argument("--disable-extensions")  # 隐藏selenium 特征
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        super().__init__(options=options)


class ArticleCrawlerWebDriver(ArticleCrawerBase):
    def __init__(
        self,
        title_xpath: str = "",
        author_xpath: str = "",
        content_xpath: str = "",
        source: Optional[str] = "webdriver",
        webdriver: BaseWebDriver = WebDriverChrome(),
    ) -> None:
        super().__init__(source=source)
        self.title_xpath = title_xpath
        self.author_xpath = author_xpath
        self.content_xpath = content_xpath
        self.webdriver_chrome = webdriver

    def article_webdriver(self, url) -> Article | None:
        try:
            # 更新UserAgent
            self.webdriver_chrome.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {"userAgent": UserAgent().random},
            )
        except Exception as e:
            logger.warning(e)
            self.webdriver_chrome.quit()
            time.sleep(3)
            WebDriverChrome.delete_instance()  # 删除单例子
            self.webdriver_chrome = WebDriverChrome()
        finally:
            self.webdriver_chrome.get(url)
            return self.article

    """
    获取文章标题
    """

    @property
    def title(self) -> str | None:
        return self.article.title if self.article else None

    @retry()
    def get_article_title(self) -> str | None:
        return self.webdriver_chrome.find_element(
            By.XPATH,
            self.title_xpath,
        ).text

    """
    获取文章作者
    """

    @property
    def author(self) -> str | None:
        return self.article.author if self.article else None

    @retry()
    def get_article_author(self) -> str | None:
        return self.webdriver_chrome.find_element(
            By.XPATH,
            self.author_xpath,
        ).text

    """
    获取文章内容
    """

    @property
    def content(self) -> str | None:
        return self.article.content if self.article else None

    @retry()
    def get_article_content(self) -> str | None:
        return self.webdriver_chrome.find_element(
            By.XPATH,
            self.content_xpath,
        ).text


if __name__ == "__main__":
    # import re

    # a = ArticleCrawlerHTTP(
    #     "//h1[@class='Post-Title']/text()",
    #     "//a[@data-za-detail-view-element_name='User']/text()",
    #     content_tag="div",
    #     content_soup={"class_": re.compile(r"RichText ztext Post-RichText(\s\w+)?")},
    # )
    # a.article_http("")
    # print(a.article)

    a = ArticleCrawlerWebDriver(
        title_xpath='//*[@id="activity-name"]',
        author_xpath='//*[@id="js_name"]',
        content_xpath='//*[@id="js_content"]',
    )
    b = ArticleCrawlerWebDriver(
        title_xpath='//*[@id="activity-name"]',
        author_xpath='//*[@id="js_name"]',
        content_xpath='//*[@id="js_content"]',
    )
    art = b.article_webdriver("https://mp.weixin.qq.com/s/YWbtLl9Sdfh5jOAgdrEa7A")
    if art:
        print(art.title)
        print(art.author)
        print(art.content)

    b.refresh()
    art = b.article_webdriver("https://mp.weixin.qq.com/s/YWbtLl9Sdfh5jOAgdrEa7A")
    if art:
        print(art.title)
        print(art.author)
        print(art.content)

    print("end")

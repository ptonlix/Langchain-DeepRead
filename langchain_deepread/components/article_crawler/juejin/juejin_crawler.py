from langchain_deepread.components.article_crawler.base.base import (
    ArticleCrawlerWebDriver,
)


class JJCrawler(ArticleCrawlerWebDriver):
    def __init__(
        self,
        title_xpath: str = '//h1[@class="article-title"]',
        author_xpath: str = '//div[@class="author-info-box"]/div[1]/a/span',
        content_xpath: str = '//*[@id="article-root"]',
        source: str = "稀土掘金",
    ):
        super().__init__(
            title_xpath=title_xpath,
            author_xpath=author_xpath,
            content_xpath=content_xpath,
            source=source,
        )


if __name__ == "__main__":
    jj = JJCrawler()
    art = jj.article_webdriver(url="https://juejin.cn/post/6844904154897317902")
    print(art)
    jj.refresh()
    art = jj.article_webdriver(url="https://juejin.cn/post/7321551188092485684")
    print(art)
    jj.refresh()

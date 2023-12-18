"""Exceptions that may happen in article_crawler code."""

from typing import Optional
from typing import Sequence


class ArticleCrawlerException(Exception):
    """Base article_crawler exception."""

    def __init__(
        self,
        msg: Optional[str] = None,
        stacktrace: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__()
        self.msg = msg
        self.stacktrace = stacktrace

    def __str__(self) -> str:
        exception_msg = f"Message: {self.msg}\n"
        if self.stacktrace:
            stacktrace = "\n".join(self.stacktrace)
            exception_msg += f"Stacktrace:\n{stacktrace}"
        return exception_msg


class NotSupportDomainException(ArticleCrawlerException):
    """Crawler sites not supported"""

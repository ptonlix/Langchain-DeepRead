# from typing import Union
# from fastapi.responses import JSONResponse, Response
# from fastapi import status


# def reponse(*, code=200, data: Union[list, dict, str], message="Success") -> Response:
#     return JSONResponse(
#         status_code=status.HTTP_200_OK,
#         content={
#             "code": code,
#             "message": message,
#             "data": data,
#         },
#     )

from pydantic import BaseModel
from typing import Generic, TypeVar


T = TypeVar("T")  # 泛型类型 T


class RestfulModel(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "success"
    data: T

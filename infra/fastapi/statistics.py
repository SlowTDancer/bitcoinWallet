from __future__ import annotations

from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

from constants import ADMIN_API_KEY
from core.admin_checker import check_admin
from core.errors import InvalidAdminAPIKeyError
from infra.fastapi.dependables import TransactionStatisticRepositoryDependable

statistic_api = APIRouter(tags=["Statistics"])


class StatisticItemResponse(BaseModel):
    transactions_number: int
    platform_profit: float


class StatisticItemResponseEnvelope(BaseModel):
    statistics: StatisticItemResponse


@statistic_api.get(
    "/statistics",
    status_code=200,
    response_model=StatisticItemResponseEnvelope,
    responses={
        401: {
            "content": {
                "application/json": {
                    "example": {"error": {"message": "Invalid admin API key <key>"}}
                }
            }
        },
    },
)
def get_transactions(
    transaction_statistics: TransactionStatisticRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> JSONResponse | dict[str, StatisticItemResponse]:
    try:
        check_admin(api_key)
    except InvalidAdminAPIKeyError:
        return JSONResponse(
            status_code=401,
            content={"error": {"message": f"Invalid admin API key <{api_key}>"}},
        )

    statistics = transaction_statistics.get_statistics()
    return {
        "statistics": StatisticItemResponse(
            transactions_number=statistics.get_transactions_number(),
            platform_profit=statistics.get_platform_profit())
    }

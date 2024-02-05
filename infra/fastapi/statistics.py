from __future__ import annotations

from typing import Dict
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

from constants import ADMIN_API_KEY
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
        404: {
            "content": {
                "application/json": {
                    "example": {"error": {"message": "Invalid API key"}}
                }
            }
        },
    },
)
def get_transactions(
    transaction_statistics: TransactionStatisticRepositoryDependable,
    api_key: UUID = Header(alias="api_key"),
) -> JSONResponse | dict[str, StatisticItemResponse]:
    if api_key != ADMIN_API_KEY:
        return JSONResponse(
            status_code=404,
            content={"error": {"message": "Invalid API key"}},
        )

    statistics = transaction_statistics.get_statistics()
    return {
        "statistics": StatisticItemResponse(
            transactions_number=statistics.get_transactions_number(),
            platform_profit=statistics.get_platform_profit())
    }

from typing import Union

from starlette import status
from fastapi import APIRouter, Depends

from dns_system.apps.domains.middleware import auth_middleware
from dns_system.apps.domains import selectors as domain_selectors
from dns_system.apps.domains.schemas import SuccessResponseModel, FailResponseModel

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, response_model=Union[SuccessResponseModel, FailResponseModel],
            dependencies=[Depends(auth_middleware)])
async def get_domains():
    try:
        domains = await domain_selectors.domain.list()
        domains_list = [domain.domain_name for domain in domains]
        return SuccessResponseModel(payloads={"domains": domains_list})
    except Exception as e:
        error_message = str(e)
        return FailResponseModel(message=error_message)

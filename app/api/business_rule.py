from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user
from app.database.models import User
from app.schemas.business_rule import (
    BusinessRuleCreate,
    BusinessRuleResponse,
    BusinessRuleUpdate,
)
from app.services.business_rule_service import (
    create_business_rule,
    delete_business_rule,
    get_connection_business_rules,
    get_user_business_rule,
    get_user_business_rules,
    serialize_business_rule,
    update_business_rule,
)


router = APIRouter(
    prefix="/business-rules",
    tags=["Business Rules"],
)


@router.post(
    "",
    response_model=BusinessRuleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rule(
    request: BusinessRuleCreate,
    current_user: User = Depends(get_current_user),
):
    try:
        rule = create_business_rule(
            user_id=current_user.user_id,
            connection_id=request.connection_id,
            title=request.title,
            description=request.description,
            table_names=request.table_names,
            column_names=request.column_names,
        )

        return serialize_business_rule(rule)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "",
    response_model=list[BusinessRuleResponse],
)
def list_rules(
    connection_id: int | None = None,
    current_user: User = Depends(get_current_user),
):
    rules = get_user_business_rules(
        user_id=current_user.user_id,
        connection_id=connection_id,
    )

    return [
        serialize_business_rule(rule)
        for rule in rules
    ]


@router.get(
    "/{rule_id}",
    response_model=BusinessRuleResponse,
)
def get_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
):
    rule = get_user_business_rule(
        user_id=current_user.user_id,
        rule_id=rule_id,
    )

    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business rule not found.",
        )

    return serialize_business_rule(rule)


@router.put(
    "/{rule_id}",
    response_model=BusinessRuleResponse,
)
def update_rule(
    rule_id: int,
    request: BusinessRuleUpdate,
    current_user: User = Depends(get_current_user),
):
    try:
        rule = update_business_rule(
            user_id=current_user.user_id,
            rule_id=rule_id,
            title=request.title,
            description=request.description,
            table_names=request.table_names,
            column_names=request.column_names,
        )

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Business rule not found.",
            )

        return serialize_business_rule(rule)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
):
    deleted = delete_business_rule(
        user_id=current_user.user_id,
        rule_id=rule_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business rule not found.",
        )
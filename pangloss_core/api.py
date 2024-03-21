import typing
import uuid

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pangloss_core.model_setup.model_manager import ModelManager
from pangloss_core.exceptions import PanglossNotFoundError
from pangloss_core.users import User, get_current_active_user


class ErrorResponse(BaseModel):
    detail: str


class ListResponse[T](typing.TypedDict):
    results: typing.List[T]
    page: int
    count: int
    totalPages: int
    next: str | None
    previous: str | None


def setup_api_routes(_app: FastAPI, settings: BaseSettings) -> FastAPI:

    api_router = APIRouter(prefix="/api")
    for model in ModelManager._registered_models:
        router = APIRouter(prefix=f"/{model.__name__}", tags=[model.__name__])

        def _list(model):

            async def list(
                request: Request,
                current_user: typing.Annotated[User, Depends(get_current_active_user)],
                q: typing.Optional[str] = "",
                page: int = 1,
                pageSize: int = 10,
            ) -> ListResponse[model.Reference]:

                result = await model.get_list(q=q, page=page, page_size=pageSize)

                result["next"] = (
                    str(
                        request.url.replace_query_params(
                            q=q, page=page + 1, pageSize=pageSize
                        )
                    )
                    if page + 1 <= result["totalPages"]
                    else None
                )
                result["previous"] = (
                    str(
                        request.url.replace_query_params(
                            q=q, page=page - 1, pageSize=pageSize
                        )
                    )
                    if page - 1 >= 1
                    else None
                )
                return result

            return list

        router.add_api_route(
            "/",
            endpoint=_list(model),
            methods={"get"},
            name=f"{model.__name__}.List",
            operation_id=f"{model.__name__}List",
        )

        if not model.__abstract__:

            def _get(model):
                async def get(uid: uuid.UUID) -> model.View:  # type: ignore

                    try:
                        result = await model.View.get(uid=uid)
                    except PanglossNotFoundError:
                        raise HTTPException(status_code=404, detail="Item not found")
                    return result

                return get

            router.api_route(
                "/{uid}",
                methods=["get"],
                name=f"{model.__name__}.View",
                operation_id=f"{model.__name__}View",
            )(_get(model))

            if model.__create__:

                def _create(model):
                    async def create(entity: model) -> model.Reference:  # type: ignore
                        result = await entity.create()
                        return result

                    return create

                router.api_route(
                    "/new",
                    methods=["post"],
                    name=f"{model.__name__}.Create",
                    operation_id=f"{model.__name__}Create",
                )(_create(model))

            if model.__edit__:

                def _get_edit(model):
                    async def get_edit(uid: uuid.UUID) -> model.Edit:  # type: ignore

                        try:
                            result = await model.Edit.get(uid=uid)
                        except PanglossNotFoundError:
                            raise HTTPException(
                                status_code=404, detail="Item not found"
                            )
                        return result

                    return get_edit

                router.add_api_route(
                    "/edit",
                    endpoint=_get_edit(model),
                    methods={"get"},
                    name=f"{model.__name__}.EditGet",
                    operation_id=f"{model.__name__}EditGet",
                )

                def _post_edit(model):
                    async def post_edit(
                        uid: uuid.UUID, entity: model.Edit
                    ) -> model.Reference:

                        # Should not be using the endpoint to send different update objects!
                        if entity.uid != uid:
                            raise HTTPException(status_code=400, detail="Bad request")

                        try:
                            result = await entity.write_edit()
                        except PanglossNotFoundError:
                            raise HTTPException(
                                status_code=404, detail="Item not found"
                            )
                        return result

                    return post_edit

                router.add_api_route(
                    "/edit/{uid}",
                    endpoint=_post_edit(model),
                    methods={"patch"},
                    name=f"{model.__name__}.EditPatch",
                    operation_id=f"{model.__name__}EditPatch",
                )

            if model.__delete__:

                def _delete(model):
                    async def delete(uid: uuid.UUID) -> None:
                        raise HTTPException(
                            status_code=501, detail="Not implemented yet"
                        )

                    return delete

                router.add_api_route(
                    "/{uid}",
                    endpoint=_delete(model),
                    methods={"delete"},
                    name=f"{model.__name__}.Delete",
                )

        api_router.include_router(router)
    _app.include_router(api_router)
    return _app

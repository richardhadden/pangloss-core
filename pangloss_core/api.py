import typing
import uuid

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from pydantic_settings import BaseSettings

from pangloss_core.model_setup.model_manager import ModelManager
from pangloss_core.exceptions import PanglossNotFoundError


class ErrorResponse(BaseModel):
    detail: str


def setup_api_routes(_app: FastAPI, settings: BaseSettings) -> FastAPI:
    api_router = APIRouter(prefix="/api")
    for model in ModelManager._registered_models:
        router = APIRouter(prefix=f"/{model.__name__}", tags=[model.__name__])

        def _list(model):
            async def list() -> typing.List[model.Reference]:  # type:ignore
                return []

            return list

        router.add_api_route(
            "/", endpoint=_list(model), methods={"get"}, name=f"{model.__name__}.List"
        )

        if not model.__abstract__:

            def _get(model):
                async def get(uid: uuid.UUID) -> model.View:  # type: ignore
                    print("Getting", model, model.View, uid)
                    try:
                        result = await model.View.get(uid=uid)
                    except PanglossNotFoundError:
                        raise HTTPException(status_code=404, detail="Item not found")
                    return result

                return get

            router.api_route("/{uid}", methods=["get"], name=f"{model.__name__}.View")(
                _get(model)
            )

            def _create(model):
                async def create(entity: model) -> model.Reference:  # type: ignore
                    result = await entity.create()
                    return result

                return create

            router.api_route("/new", methods=["post"], name=f"{model.__name__}.Create")(
                _create(model)
            )

            def _get_edit(model):
                async def get_edit(uid: uuid.UUID) -> model.Edit:  # type: ignore
                    print(uid)
                    try:
                        result = await model.Edit.get(uid=uid)
                    except PanglossNotFoundError:
                        raise HTTPException(status_code=404, detail="Item not found")
                    return result

                return get_edit

            router.add_api_route(
                "/edit",
                endpoint=_get_edit(model),
                methods={"get"},
                name=f"{model.__name__}.Edit",
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
                        raise HTTPException(status_code=404, detail="Item not found")
                    return result

                return post_edit

            router.add_api_route(
                "/edit/{uid}",
                endpoint=_post_edit(model),
                methods={"patch"},
                name=f"{model.__name__}.Edit",
            )

        api_router.include_router(router)
    _app.include_router(api_router)
    return _app

from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from infrastructure.repositories import event_publisher
from settings import get_settings
from logger import get_logger
from core.exceptions import (
    NotFoundError,
    DuplicateEntryError,
    AlreadyExistsError,
    InvalidCredentialsError,
    TokenExpiredError,
    InvalidTokenError,
    InvalidRequestError,
)
from interface.routers import router
from infrastructure.event_publisher_singleton import event_publisher


config = get_settings()
logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация настроек до запуска сервиса"""
    logger.info(app)
    await event_publisher.start()
    yield
    await event_publisher.stop()


app = FastAPI(
    title=config.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description=config.project_description,
    version=config.project_version,
    lifespan=lifespan,
    debug=config.is_debug_mode,
)


@app.middleware("http")
async def custom_exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except NotFoundError as e:
        return JSONResponse(status_code=404, content={"detail": str(e)})
    except DuplicateEntryError as e:
        return JSONResponse(status_code=409, content={"detail": str(e)})
    except AlreadyExistsError as e:
        return JSONResponse(status_code=409, content={"detail": str(e)})
    except InvalidCredentialsError as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})
    except TokenExpiredError as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})
    except InvalidTokenError as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})
    except InvalidRequestError as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal Server Error"}
        )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

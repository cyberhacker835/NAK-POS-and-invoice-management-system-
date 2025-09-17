from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, businesses, products, customers, invoices, uploads, export
from .db import Base, engine


def create_app() -> FastAPI:
    app = FastAPI(title="UAE Multi-Business POS & Invoice API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(businesses.router, prefix="/api/businesses", tags=["businesses"])
    app.include_router(products.router, prefix="/api/products", tags=["products"])
    app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
    app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
    app.include_router(uploads.router, prefix="/api/uploads", tags=["uploads"])
    app.include_router(export.router, prefix="/api/export", tags=["export"])

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok"}

    return app


Base.metadata.create_all(bind=engine)
app = create_app()


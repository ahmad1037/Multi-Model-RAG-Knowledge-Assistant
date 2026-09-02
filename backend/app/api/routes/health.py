from fastapi import APIRouter, HTTPException, status
from sqlalchemy import text
from app.db.session import engine

router = APIRouter(
    prefix="/health",
    tags=["Health"],
)


@router.get("")
async def health_check():
    return {
        "status": "healthy",
        "service": "Multi-Model RAG Knowledge Assistant",
    }

@router.get("/live")
def liveness():
    return {
        "status": "ok",
        "service": "multimodal-rag-backend",
    }


@router.get("/ready")
def readiness():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

            pgvector_version = connection.scalar(
                text(
                    """
                    SELECT extversion
                    FROM pg_extension
                    WHERE extname = 'vector'
                    """
                )
            )

        return {
            "status": "ready",
            "database": "connected",
            "pgvector": pgvector_version,
        }

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service dependencies are not ready.",
        )
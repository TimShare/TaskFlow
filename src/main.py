import logging
import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "interface.main:app",
        host="0.0.0.0",
        port=8010,
        log_level=logging.DEBUG,
        reload=True,
        use_colors=True,
    )

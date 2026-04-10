import uvicorn
from fastapi.responses import RedirectResponse
from openenv.core.env_server import create_fastapi_app

from models import SupportAction, SupportObservation
from server.environment import InboxPilotEnvironment

app = create_fastapi_app(
    InboxPilotEnvironment,
    SupportAction,
    SupportObservation,
)


@app.get("/")
def root():
    return RedirectResponse(url="/docs")


def main() -> None:
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=7860,
        reload=False,
    )


if __name__ == "__main__":
    main()
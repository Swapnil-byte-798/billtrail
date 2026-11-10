import os
from fastapi import Depends, Request
from pydantic import BaseModel, ConfigDict
from .runtime import Fault, make_app
from .service import InvoiceService

app, auth, reviewer = make_app("BillTrail")


def service():
    return InvoiceService(
        os.path.join(os.environ.get("DATA_DIR", ".data"), "billtrail.db")
    )


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approved: bool
    correction: dict | None = None


@app.post("/documents", dependencies=[Depends(auth)])
async def upload(request: Request, filename: str):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > 20_000_000:
            raise Fault("Document exceeds 20 MB.", 413)
    return service().ingest(filename, bytes(data))


@app.post("/documents/{identifier}/process", dependencies=[Depends(auth)])
def process(identifier: str):
    return service().process(identifier)


@app.get("/documents/{identifier}", dependencies=[Depends(auth)])
def get(identifier: str):
    return service().get(identifier)


@app.post("/documents/{identifier}/review", dependencies=[Depends(reviewer)])
def review(identifier: str, decision: Decision):
    return service().review(identifier, decision.approved, decision.correction)


@app.post("/outbox/dispatch", dependencies=[Depends(auth)])
def dispatch():
    return service().dispatch()

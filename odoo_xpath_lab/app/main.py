from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.schemas import XPathTestRequest
from app.xpath_service import apply_xpath


app = FastAPI(
    title="Odoo XPath Lab",
    description="Validate Odoo XML and simulate XPath inheritance operations.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/test-xpath")
async def test_xpath(payload: XPathTestRequest):
    return apply_xpath(
        base_xml=payload.base_xml,
        xpath_expression=payload.xpath_expression,
        position=payload.position,
        inherited_xml=payload.inherited_xml or "",
    )

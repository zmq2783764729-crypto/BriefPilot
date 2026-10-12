import asyncio

from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import DomainError
from app.main import create_app


def test_lifespan_and_offline_startup_do_not_require_api_keys():
    application = create_app(Settings(_env_file=None, llm_api_key="private-value"))

    async def exercise_application():
        async with application.router.lifespan_context(application):
            assert application.state.started
            async with AsyncClient(
                transport=ASGITransport(app=application), base_url="http://testserver"
            ) as client:
                response = await client.get("/health/live")
                assert response.status_code == 200
                assert application.state.settings.agent_mode == "fake"
                assert "private-value" not in response.text
                assert "private-value" not in str(application.state.settings)

    asyncio.run(exercise_application())

    assert not application.state.started


def test_error_contract_does_not_echo_invalid_request_values():
    application = create_app(Settings(_env_file=None))

    class Payload(BaseModel):
        quantity: int

    @application.post("/test-payload")
    async def validate_payload(payload: Payload):
        return payload

    @application.get("/test-domain-error")
    async def fail_with_domain_error():
        raise DomainError("scope_conflict", "Scope changed", status_code=409)

    async def exercise_errors():
        async with application.router.lifespan_context(application):
            async with AsyncClient(
                transport=ASGITransport(app=application), base_url="http://testserver"
            ) as client:
                invalid = await client.post(
                    "/test-payload", json={"quantity": "private-request-value"}
                )
                assert invalid.status_code == 422
                assert invalid.json()["error"]["code"] == "validation_error"
                assert "private-request-value" not in invalid.text
                assert (await client.get("/test-domain-error")).status_code == 409
                assert (await client.get("/missing")).json()["error"]["code"] == "http_error"

    asyncio.run(exercise_errors())

from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import Cookie, Depends, FastAPI, Header, HTTPException, Query, Request, Response
from fastapi.responses import StreamingResponse

from .approvals import ApprovalRepository
from .artifacts import ArtifactRepository
from .auth import AuthService, Principal
from .config import BrowserSettings
from .db import BrowserDatabase
from .models import (
    ConversationCreateRequest,
    ConversationResponse,
    ApprovalDecisionRequest,
    ApprovalResponse,
    ArtifactResponse,
    ExperienceResponse,
    LoginRequest,
    MessageCreateRequest,
    PrincipalResponse,
    MemoryResponse,
    RunResponse,
)
from .memory_api import MemoryPort, MemoryProjectionService
from .runs import RunProjection, RunRepository
from .sse import EventStream
from .static import install_spa_routes


def create_app(
    settings: BrowserSettings,
    *,
    static_root: Path | None = None,
    artifact_root: Path | None = None,
    memory_port: MemoryPort | None = None,
) -> FastAPI:
    database = BrowserDatabase(settings.database_path)
    auth = AuthService(database, settings)
    runs = RunRepository(database)
    events = EventStream(database)
    approvals = ApprovalRepository(database)
    artifacts = ArtifactRepository(database, artifact_root or settings.database_path.parent / "browser-artifacts")
    memory = MemoryProjectionService(memory_port) if memory_port is not None else None
    app = FastAPI(title="Agent Browser Control Plane", version="1.0.0")
    app.state.database = database
    app.state.auth = auth
    app.state.runs = runs
    app.state.events = events
    app.state.approvals = approvals
    app.state.artifacts = artifacts
    app.state.memory = memory

    def require_principal(agent_session: str | None = Cookie(default=None)) -> Principal:
        if not agent_session:
            raise HTTPException(status_code=401, detail="authentication required")
        try:
            with database.lock:
                return auth.authenticate(agent_session)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail="authentication required") from exc

    def require_command_principal(
        principal: Principal = Depends(require_principal),
        agent_session: str | None = Cookie(default=None),
        x_csrf_token: str | None = Header(default=None),
    ) -> Principal:
        if not agent_session or not x_csrf_token:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        try:
            with database.lock:
                auth.verify_csrf(agent_session, x_csrf_token)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail="CSRF validation failed") from exc
        return principal

    def _run_response(projection: RunProjection) -> RunResponse:
        return RunResponse(**projection.__dict__)

    @app.post("/api/v1/auth/login", response_model=PrincipalResponse)
    def login(request: LoginRequest, response: Response) -> PrincipalResponse:
        try:
            with database.lock:
                session = auth.login(request.tenant_id, request.username, request.password)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="invalid credentials") from exc
        response.set_cookie(
            "agent_session",
            session.session_token,
            httponly=True,
            secure=settings.secure_cookies,
            samesite="strict",
            max_age=settings.session_ttl_seconds,
            path="/",
        )
        response.set_cookie(
            "agent_csrf",
            session.csrf_token,
            httponly=False,
            secure=settings.secure_cookies,
            samesite="strict",
            max_age=settings.session_ttl_seconds,
            path="/",
        )
        return PrincipalResponse(
            tenant_id=session.principal.tenant_id,
            user_id=session.principal.user_id,
            role=session.principal.role,
        )

    @app.get("/api/v1/auth/me", response_model=PrincipalResponse)
    def me(principal: Principal = Depends(require_principal)) -> PrincipalResponse:
        return PrincipalResponse(tenant_id=principal.tenant_id, user_id=principal.user_id, role=principal.role)

    @app.get("/api/v1/experience", response_model=ExperienceResponse)
    def experience(principal: Principal = Depends(require_principal)) -> ExperienceResponse:
        surfaces = list(settings.surfaces)
        if principal.role != "admin":
            surfaces = [surface for surface in surfaces if surface not in {"settings", "access"}]
        return ExperienceResponse(profile=settings.experience_profile, surfaces=surfaces, role=principal.role)

    @app.post("/api/v1/conversations", response_model=ConversationResponse, status_code=201)
    def create_conversation(
        request: ConversationCreateRequest,
        principal: Principal = Depends(require_command_principal),
    ) -> ConversationResponse:
        try:
            with database.lock:
                conversation_id = runs.create_conversation(principal, request.title)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return ConversationResponse(id=conversation_id, title=request.title.strip())

    @app.post("/api/v1/conversations/{conversation_id}/messages", response_model=RunResponse, status_code=202)
    def send_message(
        conversation_id: str,
        request: MessageCreateRequest,
        principal: Principal = Depends(require_command_principal),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> RunResponse:
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Idempotency-Key is required")
        try:
            with database.lock:
                projection = runs.send_message(
                    principal,
                    conversation_id,
                    request.text,
                    idempotency_key,
                    settings.experience_profile,
                )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return _run_response(projection)

    @app.get("/api/v1/runs/{run_id}", response_model=RunResponse)
    def get_run(run_id: str, principal: Principal = Depends(require_principal)) -> RunResponse:
        with database.lock:
            projection = runs.get_run(principal, run_id)
        if projection is None:
            raise HTTPException(status_code=404, detail="not found")
        return _run_response(projection)

    @app.post("/api/v1/runs/{run_id}/cancel", response_model=RunResponse)
    def cancel_run(run_id: str, principal: Principal = Depends(require_command_principal)) -> RunResponse:
        try:
            with database.lock:
                return _run_response(runs.request_cancel(principal, run_id))
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="not found") from exc

    @app.get("/api/v1/runs/{run_id}/events")
    async def run_events(
        run_id: str,
        request: Request,
        after: int = Query(default=0, ge=0),
        live: bool = Query(default=True),
        principal: Principal = Depends(require_principal),
    ) -> StreamingResponse:
        try:
            with database.lock:
                initial = events.replay(principal, run_id, after=after)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="not found") from exc

        async def project_events():
            cursor = after
            pending = initial
            while True:
                if pending:
                    for event in pending:
                        cursor = max(cursor, event.sequence)
                        yield events.encode(event)
                elif not live:
                    break
                else:
                    yield events.heartbeat()
                if not live or await request.is_disconnected():
                    break
                await asyncio.sleep(1)
                with database.lock:
                    pending = events.replay(principal, run_id, after=cursor)

        return StreamingResponse(
            project_events(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
        )

    @app.get("/api/v1/approvals", response_model=list[ApprovalResponse])
    def list_approvals(principal: Principal = Depends(require_principal)) -> list[ApprovalResponse]:
        with database.lock:
            return [
                ApprovalResponse(
                    id=item.id, run_id=item.run_id, tool_name=item.tool_name, tool_version=item.tool_version,
                    target=item.target, risk=item.risk, evidence_refs=list(item.evidence_refs),
                    action_fingerprint=item.action_fingerprint, expires_at=item.expires_at, decision=item.decision,
                )
                for item in approvals.list(principal)
            ]

    @app.post("/api/v1/approvals/{approval_id}/decision", status_code=204)
    def decide_approval(
        approval_id: str,
        request: ApprovalDecisionRequest,
        principal: Principal = Depends(require_command_principal),
    ) -> None:
        try:
            with database.lock:
                approvals.decide(principal, approval_id, request.decision)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="not found") from exc

    @app.get("/api/v1/artifacts", response_model=list[ArtifactResponse])
    def list_artifacts(principal: Principal = Depends(require_principal)) -> list[ArtifactResponse]:
        with database.lock:
            return [ArtifactResponse(**item.__dict__) for item in artifacts.list(principal)]

    @app.get("/api/v1/artifacts/{artifact_id}/download")
    def download_artifact(artifact_id: str, principal: Principal = Depends(require_principal)) -> Response:
        try:
            with database.lock:
                metadata = artifacts.metadata(principal, artifact_id)
                data = artifacts.read(principal, artifact_id)
        except (KeyError, FileNotFoundError) as exc:
            raise HTTPException(status_code=404, detail="not found") from exc
        return Response(
            content=data,
            media_type=metadata.media_type,
            headers={"Content-Disposition": artifacts.content_disposition(metadata), "X-Content-Type-Options": "nosniff"},
        )

    def require_memory() -> MemoryProjectionService:
        if memory is None:
            raise HTTPException(status_code=503, detail="Memory adapter is not configured")
        return memory

    @app.get("/api/v1/memory", response_model=list[MemoryResponse])
    def list_memory(principal: Principal = Depends(require_principal)) -> list[MemoryResponse]:
        return [MemoryResponse(**item) for item in require_memory().list(principal)]

    @app.delete("/api/v1/memory/{record_id}", status_code=204)
    def delete_memory(record_id: str, principal: Principal = Depends(require_command_principal)) -> None:
        if not require_memory().delete(principal, record_id):
            raise HTTPException(status_code=404, detail="not found")

    @app.get("/api/v1/memory/export")
    def export_memory(principal: Principal = Depends(require_principal)) -> Response:
        return Response(
            content=require_memory().export(principal),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="memory-export.json"', "X-Content-Type-Options": "nosniff"},
        )

    @app.post("/api/v1/auth/logout", status_code=204)
    def logout(
        response: Response,
        agent_session: str | None = Cookie(default=None),
        x_csrf_token: str | None = Header(default=None),
    ) -> None:
        if not agent_session or not x_csrf_token:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        try:
            with database.lock:
                auth.verify_csrf(agent_session, x_csrf_token)
                auth.logout(agent_session)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail="CSRF validation failed") from exc
        response.delete_cookie("agent_session", path="/")
        response.delete_cookie("agent_csrf", path="/")

    if static_root is not None:
        install_spa_routes(app, static_root)
    return app

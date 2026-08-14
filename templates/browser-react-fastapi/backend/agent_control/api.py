from __future__ import annotations

from fastapi import Cookie, FastAPI, Header, HTTPException, Response

from .auth import AuthService
from .config import BrowserSettings
from .db import BrowserDatabase
from .models import LoginRequest, PrincipalResponse


def create_app(settings: BrowserSettings) -> FastAPI:
    database = BrowserDatabase(settings.database_path)
    auth = AuthService(database, settings)
    app = FastAPI(title="Agent Browser Control Plane", version="1.0.0")
    app.state.database = database
    app.state.auth = auth

    @app.post("/api/v1/auth/login", response_model=PrincipalResponse)
    def login(request: LoginRequest, response: Response) -> PrincipalResponse:
        try:
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
    def me(agent_session: str | None = Cookie(default=None)) -> PrincipalResponse:
        if not agent_session:
            raise HTTPException(status_code=401, detail="authentication required")
        try:
            principal = auth.authenticate(agent_session)
        except PermissionError as exc:
            raise HTTPException(status_code=401, detail="authentication required") from exc
        return PrincipalResponse(tenant_id=principal.tenant_id, user_id=principal.user_id, role=principal.role)

    @app.post("/api/v1/auth/logout", status_code=204)
    def logout(
        response: Response,
        agent_session: str | None = Cookie(default=None),
        x_csrf_token: str | None = Header(default=None),
    ) -> None:
        if not agent_session or not x_csrf_token:
            raise HTTPException(status_code=403, detail="CSRF validation failed")
        try:
            auth.verify_csrf(agent_session, x_csrf_token)
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail="CSRF validation failed") from exc
        auth.logout(agent_session)
        response.delete_cookie("agent_session", path="/")
        response.delete_cookie("agent_csrf", path="/")

    return app

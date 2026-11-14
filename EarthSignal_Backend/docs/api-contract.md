# API contract

All routes are prefixed with `/api`. OpenAPI is available at `/docs`.

Auth-protected routes require `Authorization: Bearer <JWT>`. Private investigations and jobs are always filtered by the authenticated `owner_id`.

The catalog and stored scientific outputs are public read-only. Mutations use POST with Pydantic validation. Error responses use FastAPI's structured `detail` format.

See README for route table and example payloads.

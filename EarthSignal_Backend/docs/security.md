# Security

- Passwords are hashed with Argon2; plaintext passwords are never persisted.
- JWTs are signed with `SECRET_KEY` and expire.
- The default development key must be replaced before production.
- User investigation/job reads enforce ownership.
- Atlas credentials are read from `.env`; never commit or upload `.env`.
- CORS is restricted to configured origins.
- Do not expose raw exception traces or database credentials in API responses.
- For production, terminate TLS at a trusted reverse proxy and set secure secret management.

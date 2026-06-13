/** JWT verification for Socket.IO handshakes.
 *
 * Clients pass the access token issued by the API gateway in the Socket.IO
 * handshake (`auth.token`). We verify it with the *same* access secret the
 * gateway signs with, so the two services share one identity without a network
 * round-trip on every connection.
 */
import jwt from "jsonwebtoken";

export type UserRole = "admin" | "analyst" | "viewer" | "citizen";

export interface AccessTokenClaims {
  sub: string;
  role: UserRole;
  email?: string;
}

export class AuthError extends Error {}

export function verifyAccessToken(token: string, secret: string): AccessTokenClaims {
  let decoded: unknown;
  try {
    decoded = jwt.verify(token, secret);
  } catch (err) {
    throw new AuthError(err instanceof Error ? err.message : "invalid token");
  }
  if (typeof decoded !== "object" || decoded === null) {
    throw new AuthError("malformed token payload");
  }
  const claims = decoded as Record<string, unknown>;
  if (typeof claims.sub !== "string" || typeof claims.role !== "string") {
    throw new AuthError("token missing sub/role");
  }
  return {
    sub: claims.sub,
    role: claims.role as UserRole,
    email: typeof claims.email === "string" ? claims.email : undefined,
  };
}

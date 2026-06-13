import jwt from "jsonwebtoken";

import { AuthError, verifyAccessToken } from "../src/auth";

const SECRET = "test-secret";

describe("verifyAccessToken", () => {
  it("accepts a valid token and returns claims", () => {
    const token = jwt.sign({ sub: "user-1", role: "analyst", email: "a@b.c" }, SECRET);
    expect(verifyAccessToken(token, SECRET)).toEqual({
      sub: "user-1",
      role: "analyst",
      email: "a@b.c",
    });
  });

  it("rejects a token signed with the wrong secret", () => {
    const token = jwt.sign({ sub: "u", role: "viewer" }, "other-secret");
    expect(() => verifyAccessToken(token, SECRET)).toThrow(AuthError);
  });

  it("rejects a token missing sub/role", () => {
    const token = jwt.sign({ email: "a@b.c" }, SECRET);
    expect(() => verifyAccessToken(token, SECRET)).toThrow(/sub\/role/);
  });

  it("rejects a malformed token", () => {
    expect(() => verifyAccessToken("garbage", SECRET)).toThrow(AuthError);
  });
});

import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({
    status: "ok",
    service: "frontend",
    version: "0.1.0",
  });
}

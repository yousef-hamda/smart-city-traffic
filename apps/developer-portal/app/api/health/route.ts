import { NextResponse } from "next/server";

export function GET() {
  return NextResponse.json({
    status: "ok",
    service: "developer-portal",
    version: "0.1.0",
  });
}

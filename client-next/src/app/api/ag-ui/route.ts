import { NextRequest } from "next/server";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8002";

export async function POST(request: NextRequest) {
    const body = await request.json();

    const backendRes = await fetch(`${BACKEND_URL}/ag-ui`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    // If JSON response (cancel actions)
    const contentType = backendRes.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
        const data = await backendRes.json();
        return Response.json(data);
    }

    // Proxy SSE stream
    if (!backendRes.body) {
        return new Response("No response body", { status: 502 });
    }

    return new Response(backendRes.body, {
        status: 200,
        headers: {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            Connection: "keep-alive",
        },
    });
}

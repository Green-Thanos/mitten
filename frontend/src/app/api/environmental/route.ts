// app/api/environmental/route.ts
import { type NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const FASTAPI_BASE_URL =
  process.env.FASTAPI_BASE_URL?.replace(/\/$/, "") || "https://mitten-1.onrender.com";

export async function POST(request: NextRequest) {
  try {
    const body = (await request.json()) as { query?: string };

    if (!body?.query || typeof body.query !== "string") {
      return NextResponse.json(
        { error: "Query is required and must be a string" },
        { status: 400 }
      );
    }

    const url = `${FASTAPI_BASE_URL}/api/v1/endpoint`;

    const ac = new AbortController();
    const to = setTimeout(() => ac.abort(), 15000);

    const fastApiResponse = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: body.query }),
      cache: "no-store",
      signal: ac.signal,
    }).catch((e) => {
      throw new Error(`Could not reach FastAPI at ${url} — ${e.message}`);
    });

    clearTimeout(to);

    if (!fastApiResponse.ok) {
      let detail: unknown = null;
      try {
        detail = await fastApiResponse.json();
      } catch {
        detail = await fastApiResponse.text();
      }
      return NextResponse.json(
        { error: "FastAPI returned an error", status: fastApiResponse.status, detail },
        { status: fastApiResponse.status }
      );
    }

    const data = await fastApiResponse.json();

    // OPTIONAL: if your front-end expects different shape, adapt here.
    // Example: FastAPI returns `locations` but UI expects a visualization block.
    // const adapted = adaptToEnvironmentalResult(data);

    return NextResponse.json(data, { status: 200 });
  } catch (err: any) {
    console.error("API route error:", err);
    return NextResponse.json(
      { error: "Internal server error", detail: String(err?.message ?? err) },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json(
    { message: "Use POST to submit environmental queries" },
    { status: 405 }
  );
}

/** Example adapter if you need to match your EnvironmentalResult interface */
// function adaptToEnvironmentalResult(api: any) {
//   return {
//     id: api.id,
//     originalQuery: api.originalQuery,
//     category: api.category,
//     summary: api.summary,
//     sources: api.sources ?? [],
//     charities: api.charities ?? [],
//     visualizations: api.locations
//       ? [
//           {
//             type: "pinpoints",
//             data: api.locations.map((p: any) => ({
//               lat: p.latitude,
//               lng: p.longitude,
//               label: p.name,
//               description: p.description,
//             })),
//             metadata: {
//               title: "Locations",
//               description: "Points referenced by the analysis",
//               source: "FastAPI",
//               lastUpdated: new Date().toISOString().slice(0, 10),
//             },
//           },
//         ]
//       : [],
//     shareableUrl: api.shareableUrl ?? "",
//     generatedAt: new Date().toISOString(),
//   };
// }

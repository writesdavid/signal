/**
 * Signal subscribe worker
 * Accepts POST { email } → adds contact to Resend audience
 * Deploy: wrangler deploy
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: CORS });
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: CORS });
    }

    let email;
    try {
      const body = await request.json();
      email = (body.email || "").trim().toLowerCase();
    } catch {
      return new Response("Invalid JSON", { status: 400, headers: CORS });
    }

    if (!email || !email.includes("@")) {
      return new Response("Invalid email", { status: 400, headers: CORS });
    }

    const res = await fetch(
      `https://api.resend.com/audiences/${env.RESEND_AUDIENCE_ID}/contacts`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${env.RESEND_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, unsubscribed: false }),
      }
    );

    if (!res.ok) {
      const err = await res.text();
      console.error("Resend error:", err);
      return new Response("Failed to subscribe", { status: 502, headers: CORS });
    }

    return new Response(JSON.stringify({ ok: true }), {
      headers: { ...CORS, "Content-Type": "application/json" },
    });
  },
};

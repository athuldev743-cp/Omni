import httpx, asyncio

async def test(code):
    app_id = "1270370071163693"
    secret = "cb528c7dfa5a55402d69095a9cc6dd7d"
    
    uris = [
        "",
        "https://www.facebook.com/connect/login_success.html",
        "https://omni-flame-two.vercel.app",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for uri in uris:
            r = await client.get(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={"client_id": app_id, "client_secret": secret, "code": code, "redirect_uri": uri}
            )
            print(f"'{uri}' → {r.text[:150]}")
            if r.is_success:
                print("✅ WORKS!")

code = input("Paste fresh code: ")
asyncio.run(test(code))
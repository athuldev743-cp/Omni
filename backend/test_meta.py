import httpx, asyncio

async def test(code):
    app_id = "1270370071163693"
    secret = "cb528c7dfa5a55402d69095a9cc6dd7d"
    
    uris = [
        "https://omni-flame-two.vercel.app/",
        "https://omni-flame-two.vercel.app",
    ]
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for uri in uris:
            r = await client.get(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={"client_id": app_id, "client_secret": secret, "code": code, "redirect_uri": uri}
            )
            print(f"'{uri}':\n  {r.text[:200]}\n")
            if r.is_success:
                print("✅ THIS URI WORKS!")
                return

code = input("Paste ONLY the code (starting with AQ...) → ")
asyncio.run(test(code))
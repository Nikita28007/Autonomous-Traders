import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

load_dotenv(override=True)

bot_token_telegram = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id_telegram = os.getenv("TELEGRAM_CHAT_ID")
mcp = FastMCP("push_server")


class PushModelArgs(BaseModel):
    message: str = Field(description="A message to push")

@mcp.tool()
def push_telegram(args: PushModelArgs):
    """Send a push notification with this response message"""
    print(f"Push: {args.message}")
    response = requests.post(
        f"https://api.telegram.org/bot{bot_token_telegram}/sendMessage",
        json={
            "chat_id": chat_id_telegram,
            "text": args.message,
        },
        timeout=10,
    )
    response.raise_for_status()
    return "Notification sent"
        

if __name__ == "__main__":
    mcp.run(transport="stdio")

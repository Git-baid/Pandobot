import asyncio
import random
import mouse
import threading
import secrets
from pathlib import Path
from pynput.keyboard import Key, Controller

from twitchAPI.twitch import Twitch
from twitchAPI.oauth import UserAuthenticator
from twitchAPI.type import AuthScope, ChatEvent
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.chat import Chat, ChatMessage, EventData

from playsound import playsound

meow_folder = Path("MeowSounds")

TARGET_CHANNEL = "pandobon"
APP_ID = secrets.APP_ID
APP_SECRET = secrets.APP_SECRET
USER_SCOPE = [
    AuthScope.CHAT_READ, 
    AuthScope.CHAT_EDIT,
    AuthScope.CHANNEL_READ_REDEMPTIONS
]

# global chat variable to be used in event handlers
chat = None
keyboard = None

async def on_ready(ready_event: EventData):
    # Join the target channel's chat
    await ready_event.chat.join_room(TARGET_CHANNEL)
    # await chat.send_message(TARGET_CHANNEL, "bot is online 👀")
    print("pandobot ready!")

async def on_redeem(data):
    print("REWARD REDEEMED!")
    print(f"User: {data.event.user_name}")
    print(f"Reward: {data.event.reward.title}")
    print(f"Input: {data.event.user_input}")

    match data.event.reward.title:
        case "Click":
            print("Clicking mouse!")
            mouse.click("left")
        case "Right Click":
            print("Right clicking mouse!")
            mouse.click("right")
        case "Keypress":
            print(f"Pressing {data.event.user_input[0].lower()} key!")
            try:
                keyboard.press(data.event.user_input[0].lower())
                await asyncio.sleep(0.1)
                keyboard.release(data.event.user_input[0].lower())
            except Exception as e:
                await chat.send_message(TARGET_CHANNEL, f"Error pressing \"{data.event.user_input[0].lower()}\", make sure it's a valid key")
                print(f"Error occurred while pressing key: {e}")
        case "Meow :3":
            print("Meowing!")
            # Play random sound from meow folder
            await play_sound(str(random.choice(list(meow_folder.glob("*.mp3")))))

async def on_message(message: ChatMessage): 
    print(f"{message.user.name}: {message.text}")

async def play_sound(sound_file):
    # Play the sound in a separate thread to avoid blocking the event loop
    threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()

async def run_bot():
    print("Starting pandobot...")
    #Authenticate with Twitch
    bot = await Twitch(APP_ID, APP_SECRET)
    auth = UserAuthenticator(bot, USER_SCOPE)
    token, refresh_token = await auth.authenticate()
    await bot.set_user_authentication(token, USER_SCOPE, refresh_token)
    
    users = bot.get_users(logins=[TARGET_CHANNEL])
    async for user in users:
        broadcaster_id = user.id
        break

    print("Broadcaster ID:", broadcaster_id)

    # EventSub Websocket
    eventsub = EventSubWebsocket(bot)
    eventsub.start()

    global chat
    chat = await Chat(bot)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)
    chat.start()

    await eventsub.listen_channel_points_custom_reward_redemption_add(
    broadcaster_id,
    on_redeem
    )

    # start keyboard controller
    global keyboard
    keyboard = Controller()

    try:
        while True:
            await asyncio.sleep(60)
    finally:
        await bot.close()

asyncio.run(run_bot())
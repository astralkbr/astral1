import asyncio
from telethon import TelegramClient, events

api_id = '25181522'
api_hash = '1831affd3f6a37f2f0cc4cd5eaf19587'
phone_number = '+998930864265'

# List of group and channel usernames
group_usernames = ['JAHON_ASA', 'astral_me', 'test_1chat']  # Replace with correct usernames
channel_usernames = ['JAHON_AD', 'efootballmobileuz', 'test_1asad']  # Replace with correct usernames

client = TelegramClient('session_name', api_id, api_hash)

# Messages to send for each channel
channel_messages = {
    'JAHON_AD': '9860160102638386 chek shart',
    'efootballmobileuz': 'Asadbekdan otib korchi, admin tan omaguncha komentda 1 bolaman 😂',
    'test_1asad': '1 manu',
}

@client.on(events.NewMessage(chats=group_usernames))
async def handle_group_message(event):
    # Check if the message is forwarded
    if event.message.forward and event.message.forward.chat:
        forward_username = event.message.forward.chat.username
        if forward_username in channel_usernames:
            post_id = event.message.id
            chat_id = event.chat_id

            # Select the appropriate message to send based on the forwarded channel's username
            comment_text = channel_messages.get(forward_username, 'Default message')

            # Reply to the message in the group
            await client.send_message(chat_id, comment_text, reply_to=post_id)
            print(f"Message sent: {comment_text} - Channel: {forward_username}")

async def main():
    await client.start(phone_number)
    print("TelegramClient started.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())

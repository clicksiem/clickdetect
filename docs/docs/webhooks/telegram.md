# Telegram Hook

Send alerts to a Telegram chat via a [Telegram Bot](https://core.telegram.org/bots/api).

## Config

```yaml
webhooks:
    telegram_hook:
        type: telegram # required
        token: "123456:ABC-DEF..." # required — Telegram bot token
        chat_id: "-1001234567890" # required — target chat or channel ID
        verify: false # optional default(false) — SSL verification
        timeout: 10 # optional default(10)
        template: '...' # optional default(DEFAULT_TEMPLATE)
```

## Notes

- Create a bot via [@BotFather](https://t.me/BotFather) to obtain the `token`.
- `chat_id` can be a user ID, group ID, or channel ID (use a negative number for groups/channels).
- Messages are sent as plain text via the `sendMessage` Telegram API endpoint.

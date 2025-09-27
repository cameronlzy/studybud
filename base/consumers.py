from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from redis.asyncio import Redis
import json, time

def room_presence_keys(room_id, user_id=None):
    base = f"presence:room:{room_id}"
    return {
        "members": f"{base}:members",                          # SET of user_ids (strings)
        "counts":  f"{base}:user:{user_id}:count" if user_id else None,  # INT counter per user
    }

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # require auth
        if isinstance(self.scope["user"], AnonymousUser):
            await self.close()
            return

        self.user = self.scope["user"]
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.group_name = f"room_{self.room_id}"

        # Redis client (reused)
        self.r = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=True)

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # add to presence (with ref count so multi-tabs work)
        await self._presence_increment()

        # send current presence snapshot to everyone
        await self._broadcast_presence()

    async def disconnect(self, code):
        try:
            await self._presence_decrement()
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self._broadcast_presence()
        finally:
            if hasattr(self, "r"):
                await self.r.close()

    async def receive(self, text_data):
        data = json.loads(text_data or "{}")
        if "ping" in data:
            # optional: keepalive hook if you want to track last_seen
            await self.r.setex(f"last_seen:user:{self.user.id}", 120, int(time.time()))
            return

        # existing chat handling…
        body = (data.get("body") or "").strip()
        if not body:
            return
        msg = await self._save_message(self.user.id, self.room_id, body)

        await self.channel_layer.group_send(
            self.group_name,
            {"type": "chat.message", "message": msg},
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat",
            "message": event["message"],
        }))

    async def presence_update(self, event):
        # fan-out presence snapshot
        await self.send(text_data=json.dumps({
            "type": "presence",
            "users": event["users"],        # list of {id, username, profile_img}
            "count": len(event["users"]),
        }))

    # ---------- presence helpers ----------

    async def _presence_increment(self):
        keys = room_presence_keys(self.room_id, self.user.id)
        # incr per-user count; add to set when it becomes 1
        new_count = await self.r.incr(keys["counts"])
        if new_count == 1:
            await self.r.sadd(room_presence_keys(self.room_id)["members"], str(self.user.id))

    async def _presence_decrement(self):
        keys = room_presence_keys(self.room_id, self.user.id)
        # if no key, nothing to do
        if not await self.r.exists(keys["counts"]):
            return
        new_count = await self.r.decr(keys["counts"])
        if new_count <= 0:
            pipe = self.r.pipeline()
            pipe.delete(keys["counts"])
            pipe.srem(room_presence_keys(self.room_id)["members"], str(self.user.id))
            await pipe.execute()

    async def _broadcast_presence(self):
        user_ids = await self.r.smembers(room_presence_keys(self.room_id)["members"])
        users = await self._users_payload(user_ids)
        await self.channel_layer.group_send(
            self.group_name,
            {"type": "presence.update", "users": users},
        )

    @database_sync_to_async
    def _users_payload(self, user_ids):
        from django.contrib.auth import get_user_model
        from .models import Profile
        User = get_user_model()
        qs = User.objects.filter(id__in=list(user_ids)).select_related("profile")
        result = []
        for u in qs:
            img = getattr(getattr(u, "profile", None), "profile_img", None)
            result.append({
                "id": u.id,
                "username": u.username,
                "profile_img": (img.url if img else None),
            })
        return result

    @database_sync_to_async
    def _save_message(self, user_id, room_id, body):
        from .models import Room, Message
        room = Room.objects.get(id=room_id)
        msg = Message.objects.create(user_id=user_id, room=room, body=body)
        u = msg.user
        img = getattr(getattr(u, "profile", None), "profile_img", None)
        return {
            "id": msg.id,
            "user": u.id,
            "username": u.username,
            "body": msg.body,
            "created": msg.created.isoformat(),
            "profile_img": (img.url if img else None),
        }
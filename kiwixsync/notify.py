import asyncio
import logging

from decouple import config

__all__ = ["notify"]


async def _send(message):
    homeserver = config("MATRIX_HOMESERVER", default=None)
    user = config("MATRIX_USER", default=None)
    password = config("MATRIX_PASSWORD", default=None)
    room_id = config("MATRIX_ROOM_ID", default=None)

    if not all([homeserver, user, password, room_id]):
        logging.debug("Matrix notification skipped: MATRIX_* env vars not configured.")
        return

    try:
        from nio import AsyncClient, JoinError, LoginError, RoomSendError
    except ImportError:
        logging.warning(
            "MATRIX_* env vars are set but matrix-nio is not installed. "
            "Install it with: pip install matrix-nio"
        )
        return

    client = AsyncClient(homeserver, user)
    try:
        login_resp = await client.login(password)
        if isinstance(login_resp, LoginError):
            logging.warning("Matrix login failed: %s", login_resp)
            return

        join_resp = await client.join(room_id)
        if isinstance(join_resp, JoinError):
            logging.debug("Matrix join skipped (likely already joined): %s", join_resp)

        send_resp = await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message},
        )
        if isinstance(send_resp, RoomSendError):
            logging.warning("Matrix notification failed: %s", send_resp)
    finally:
        await client.close()


def notify(message):
    """Send a Matrix notification. No-ops silently if MATRIX_* env vars are
    unset, or if matrix-nio is not installed (an optional dependency —
    see requirements-notify.txt)."""
    try:
        asyncio.run(_send(message))
    except Exception:
        logging.exception("Matrix notification failed unexpectedly.")

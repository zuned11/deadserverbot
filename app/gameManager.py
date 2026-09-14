import asyncio
import logging

logs = logging.getLogger(__name__)

# stand the server down once no players have been seen for this long
AFK_TIMEOUT_SECONDS = 25 * 60

# how often main() polls the server while it is running
POLL_INTERVAL_SECONDS = 60

SERVER_STATUSES: list[str] = [
    "STOPPED",
    "STARTING",
    "RUNNING",
    "STOPPING",
]


class GameManager:
    def __init__(self, notify=None):
        # defaults to be updated later
        self.status: bool = "STOPPED"
        self.ip: str = None
        self.afk_seconds: int = 0

        # optional callback used to push shutdown notices back to Discord
        self.notify = notify

    def get_status(self) -> str:
        return self.status

    def is_running(self) -> bool:
        return self.status == "RUNNING"

    def start(self) -> str:
        if self.is_running():
            return self.get_status()

        # TODO: hetzner.start_server() / create_server(); pick up the fixed IP
        self.status = "STARTING"
        self.afk_seconds = 0
        logs.info("starting server")
        return "starting server"

    def stop(self) -> str:
        """Manually stop the server. Same path the AFK timer uses."""
        if not self.running:
            return "server already stopped"

        # TODO: hetzner.delete_server()
        self.running = False
        self.afk_seconds = 0
        logs.info("stopping server")
        return "stopping server"

    def restart(self) -> str:
        if self.is_running:
            self.stop()

        return self.start()

    def get_players(self) -> list[str]:
        """Current players on the server. Dummy list until the game API exists."""
        # TODO: query the Valheim server for connected players
        return []

    def get_player_count(self) -> int:
        return len(get_players())

    # --- internal ------------------

    def _afk_increment(self) -> None:
        """Track time without players; reset as soon as someone is on."""
        if not self.running:
            self.afk_seconds = 0
            return

        if self.get_players():
            self.afk_seconds = 0
            return

        self.afk_seconds += POLL_INTERVAL_SECONDS

    async def main(self) -> None:
        """Loop checking server status until the server is idle for too long."""
        while self.running:
            self._afk_increment()

            if self.afk_seconds >= AFK_TIMEOUT_SECONDS:
                await self._afk_shutdown()
                return

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    async def _afk_shutdown(self) -> None:
        logs.info("no players for %ss, shutting down", self.afk_seconds)
        self.stop()

        if self.notify is not None:
            await self.notify("server stopped: no players for 25 minutes")

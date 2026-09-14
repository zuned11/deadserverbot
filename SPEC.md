# Game Server Management Bot

This project seeks to better enable hosting a game server (Valheim specifically) by enabling automatic startup/stand down via Discord/afk timers. A Discord bot enables the users to stand the server back up whenever they go to play and it is down. The list of documented functions is not comprehensive, and there is room to add to it.

There are four components:

1. Discord
2. Hetzner (VPS/Cloud provider)
3. GameManager
4. RemoteHost (remote command execution on the VPS)

The Discord piece is merely a bot capable of receiving and sending messages to users and commands to the Hetzner and GameManager components. The Hetzner piece is solely responsible for infrastructural updates, like creating/deleting server instances, assigning a fixed IP address, and attaching the Volume (persistent storage) as needed. The RemoteHost piece is responsible for executing commands on a running VPS over SSH (container setup, start/stop, ports, mounts). The GameManager owns the lifecycle of the game server: it orchestrates Hetzner and RemoteHost, tracks player counts, and stands the server down once it is AFK for a period of more than 25 minutes.

## Architecture

### Layering and dependency direction

The dependency arrow points one way: `Discord → GameManager → { Hetzner, RemoteHost }`.

- `GameManager` imports **neither** `discord` **nor** any SSH transport details. It receives its collaborators (`hetzner`, `remote`) by constructor injection and emits events through an injected async callback.
- `Hetzner` knows only the cloud API (resources: instance, IP, volume). It knows nothing about SSH or game state.
- `RemoteHost` knows only how to run commands against a host it is given (connection details injected). It knows nothing about game state, player counts, or status strings.
- `Discord` is the composition-facing adapter: it holds a reference to the single `GameManager` instance, translates commands into calls, and formats/receives events.

No module imports upward. The callback from `GameManager` back into Discord is a function value injected by the composition root, **not** a back-import — so there is no circular dependency.

### Async model

One event loop, owned by `discord.py` (`bot.run()`). All components live on that loop.

- `RemoteHost` is **async** (`asyncssh`), so long remote operations (`podman pull`, provisioning) yield to the loop instead of blocking it. While a `start` is in flight, the bot still answers other commands and the AFK poll keeps ticking.
- `GameManager` is **async**, since it is called by async command handlers and calls into async `RemoteHost`.
- `Hetzner` uses the synchronous `hcloud` client and stays **sync**. `GameManager` bridges it with `await asyncio.to_thread(...)`. Do not asyncify `hcloud`.
- No `asyncio.run()` inside any component; startup work is done in `bot.setup_hook`, background loops are `asyncio.create_task`.

### Events / notifications out of GameManager

GameManager communicates state changes back to Discord through a single injected async callback (`on_event`), invoked via a private `_emit()` on GameManager:

```
async def _emit(self, event):
    logs.info("event: %s", event)
    if self._on_event is not None:
        await self._on_event(event)
```

- `_emit` always logs, so GameManager runs headless (tests, CLI) with no listener.
- The Discord layer supplies the implementation in `setup_hook` and resolves the target channel from `DISCORD_CHANNEL_ID` there — **never** from a captured `ctx`.
- Emit **structured events**, not pre-formatted strings; the Discord layer owns message wording. (A plain string is an acceptable interim shortcut.)
- Both commanded outcomes and unsolicited events (AFK shutdown, crash) flow through this same path.

### State transitions

`GameManager.status` is the single source of truth, one of `STOPPED | STARTING | RUNNING | STOPPING`. Transitions are guarded by an `asyncio.Lock`:

- Acquire the lock only to check-and-set the transition (`STOPPED → STARTING`), **not** across the multi-minute provisioning work; otherwise a concurrent `stop` blocks for the whole start.
- `start` on an already-`STARTING` server reports that; on `RUNNING` it returns status.
- OPEN: semantics of `stop` arriving during `STARTING` (queue / reject / cancel the start task).

## Discord API

Using the Discord API we are able to allow any user to request the server be stood up with either a message or slash command. In general, it is merely an interface which calls into other components to retrieve statuses and invoke functions.

- `discord.py` manages the API components, including auth/login, and the parsing of messages. This is a **thin, stateless adapter**: it holds no game state and no logic beyond translating commands and formatting events. All game state lives in GameManager.
- Implemented as a `commands.Bot` subclass (`ServerBot`) with the single `GameManager` injected; commands are methods. Avoid a module-level global `bot` — it prevents injection and testing.
- OPEN: prefix commands (`!odin start`, matches current code) vs slash commands (needs a command tree + sync). Recommend prefix first.

### Command List

- `status` - get current state of the server. Uses the server's health endpoint for checking.
- `stop` - manually stop server. Should call the same shutdown as the AFK timer.
- `start` - If the server is stopped, start it. If it is started, send the `status` result. Immediate ack ("Starting server, please wait..."); GameManager announces completion via `_emit`.
- `restart` - If the server is running, stop, then start it. If it is not running, start it.
- `players` - TODO: see if this is possible - return list of players on the server at that time

## Hetzner API

- `hetzner.py` manages the Cloud Services, aiming to stand up and shut down the server instance as necessary. Synchronous `hcloud` client.

### Command List

- `get_status` - get server healthcheck status
- `get_servers` - get all servers the user can access
- `get_ip` - get server IP address
- `delete_server` - shutdown the server gracefully - should be used whenever possible
- `force_stop_server` - shutdown the server aggressively
- `start_server` - If server is not up, start it
- `restart_game_server` - Command specifically to restart container running game

## RemoteHost

- `remoteHost.py` exposes an async interface for running arbitrary commands on a host over SSH, so all remote execution flows through one place. It receives connection details (host/IP, key) and knows nothing above it.
- Provisioning steps for a fresh instance (pull `lloesche/valheim-docker`, write the Podman quadlet, mount the volume dir, open ports, enable/start the unit) are exposed as lifecycle helpers over the same SSH channel (`provision`, `start`, `stop`), which must be idempotent so they are safe to re-run on a cold start.
- OPEN: if `RemoteHost` grows to serve several callers, split the raw transport (`run`) from the provisioning steps.
- OPEN: handle SSH readiness after instance boot (retry connect, or gate on `cloud-init status --wait`).
- OPEN: whether first-boot provisioning is pushed into cloud-init via `hcloud`'s `user_data` (removing most setup commands from runtime) or driven over SSH each cold start.

## Game Manager

- `gameManager.py` manages the core logic of the game instance: it owns the single Valheim server lifecycle, starts it when inactive, and stands it down when AFK for a period of time. It orchestrates `Hetzner` and `RemoteHost`, and emits events to Discord via the injected `_emit` callback.
- It does not know about Discord, SSH, or hcloud types.

### Command List

- `main` - Loop checking server status
- `get_players` - Check player count
- `_afk_increment` - if no players, increment a stateful tracking variable for time without logged on user
- `_afk_shutdown` - stop the server and emit the "no players for 25 minutes" notice
- `start` / `stop` / `restart` - lifecycle transitions (orchestrate Hetzner + RemoteHost), guarded by the lock

### Lifecycle example (cold start after AFK cull)

1. User runs `start` in the tracked channel → bot sends "Starting server, please wait..."
2. `GameManager.start()` checks/sets `STOPPED → STARTING` under the lock.
3. Hetzner: ensure instance exists, obtain the fixed IP, attach the persistent volume.
4. RemoteHost: `provision(ip)` (idempotent), then `start(ip)`.
5. `status = RUNNING`; `_emit("server is up")` → bot sends the message to `DISCORD_CHANNEL_ID`.

## App Loop

- `main.py` is the composition root only: build GameManager, Hetzner, RemoteHost, and the bot; inject dependencies; wire `gm.on_event`; then `bot.run(token)` — which **is** the process's event loop. No loop logic lives in `main.py`.

### Module map

- `app/discordClient.py` — `ServerBot(commands.Bot)`, commands, event formatting, channel resolution.
- `app/hetzner.py` — sync cloud API wrapper.
- `app/remoteHost.py` — async SSH remote execution + provisioning helpers.
- `app/gameManager.py` — stateful lifecycle owner, AFK tracking, orchestration, `_emit`.
- `main.py` — composition root.

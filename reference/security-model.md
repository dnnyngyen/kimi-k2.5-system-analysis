# Security Notes

Kimi's security model assumes container isolation. Within that boundary, the environment is surprisingly permissive. This isn't necessarily a flaw; rather, it's a design choice with trade-offs worth understanding.

---

## The Open Ports

Two services listen on all interfaces with no authentication. Port 8888 runs a FastAPI server that controls the Python kernel. The CORS configuration accepts requests from any origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Anyone who can reach the container network can restart the kernel, interrupt running code, or inspect internal state. The endpoints are straightforward REST calls with no tokens or secrets. Port 9223 exposes Chrome's DevTools Protocol, the debugging interface that allows page inspection, JavaScript execution, network interception, and screenshot capture. Again, no authentication.

These would be serious vulnerabilities in a production web service. In Kimi's case, they're internal to a container that users can't directly reach. The assumption is that the container network is isolated and only trusted components connect. Whether that assumption holds depends on the broader infrastructure. Container networking can be complex, and CORS `allow_origins=["*"]` is the kind of configuration that becomes a problem when network topology changes.

---

## The Chromium Flags

Chrome launches with `--no-sandbox`, which disables the browser's process isolation sandbox. Normally, Chrome's sandbox is a defense-in-depth measure against browser exploits. If malicious content compromises the renderer process, the sandbox limits what that process can access.

Containers often require `--no-sandbox` because Chrome's sandbox conflicts with container security features. You're trading browser-level sandboxing for container-level sandboxing. This is a known trade-off in containerized browser automation. The risk depends on what content the browser visits. If it's loading user-specified URLs with potentially malicious JavaScript, the missing sandbox is more concerning than if it's rendering trusted content.

---

## The Filesystem Model

The workspace has three zones with different permissions. `/mnt/okcomputer/upload/` is read-only—this is where user files land, and the agent can read what you upload but can't modify the originals. `/mnt/okcomputer/output/` is read-write, where deliverables go so the agent can create files you download. `/mnt/okcomputer/.store/` is append-only, used for things like web search citations that accumulate during a session. The agent can add records but can't edit previous entries.

This is a reasonable permission model for an agent workspace. Uploaded files are protected from modification. Outputs are clearly separated from inputs. Audit logs can't be tampered with.

---

## The Isolation Boundary

The container blocks external network access. Running `curl google.com` times out; `requests.get()` gets connection refused. Web access goes through the browser tools, which presumably have their own controls. The agent can visit web pages through Playwright but can't make arbitrary HTTP requests from Python.

Process isolation is also in place. The agent runs as a non-root user with dropped capabilities. It can't `ptrace` other processes or mount filesystems.

---

## What Does This Mean?

The security model is: isolate the container, and within that isolation, let the agent do its work. Internal services don't need authentication because they're not reachable from outside. Chrome doesn't need a sandbox because the container provides isolation. The agent has broad filesystem access because it needs to actually do things.

This is a defensible architecture. It's also a brittle one. The safety properties depend on the isolation boundary holding. If someone finds a way to reach port 8888 from outside the container, the unauthenticated kernel control becomes a problem.

Defense in depth would suggest adding authentication to the internal services even though they're "not reachable." In practice, that's additional complexity for a scenario that shouldn't happen. The trade-off is reasonable either way: you're betting on your isolation being robust versus hedging against it failing.

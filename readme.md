## Helpful commands
```bash
Set-ExecutionPolicy Unrestricted -Scope Process

.venv\scripts\activate
```

## To spin everything up
```bash
python server.py
```

In a new terminal, cd into the ngrok folder and run
```bash
ngrok http --domain=thorough-quail-wildly.ngrok-free.app 5000
```
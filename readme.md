
## **Installation**

**Download The Server:**

```bash
git clone https://github.com/prashantpandeygit/vecmem.git
cd vecmem
```

**Configure Claude Desktop:**

***Open Claude Desktop Settings → Developer → Edit Config, and add:***

```bash
{
  "mcpServers": {
    "vector-memory": {
      "command": "python",
      "args": ["/vecmem/server.py", "--working-dir", "/vecmem/server.py"]
    }
  }
}
```

**Restart Claude Desktop and look for the MCP integration icon.**


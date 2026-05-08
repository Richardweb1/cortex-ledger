CortexLedger 🧠⛓️
> A decentralized fact-checking platform powered by GenLayer AI. Every fact is verified by multiple AI validators before being permanently stored on-chain.
![CortexLedger](https://img.shields.io/badge/GenLayer-Bradbury%20Testnet-00ff88?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Live-success?style=for-the-badge)
---
🌐 Live Demo
Website: **Website:** [cortex-ledger.vercel.app](https://cortex-ledger.vercel.app)  
Contract: `0xCCC6cfA731ea04Af556d1804CB7e54CE45494B06`  
Network: GenLayer Studio Testnet
---
🧠 What is CortexLedger?
CortexLedger is a decentralized fact-checking platform that uses GenLayer's Intelligent Contracts to verify facts using AI. Unlike traditional fact-checking platforms controlled by a central authority, CortexLedger uses multiple AI validators to reach consensus on whether a submitted fact is genuine and accurate.
Why GenLayer?
Traditional blockchains like Ethereum can only handle exact mathematical computations — they cannot understand natural language or judge the quality of content. GenLayer changes this by introducing Intelligent Contracts — smart contracts powered by LLMs (Large Language Models) that can:
Read and understand natural language
Access real-world information
Make intelligent decisions through AI consensus
Verify facts, content quality, and authenticity
This makes CortexLedger possible — a platform where AI decides what's true, not a company or a person.
---
✨ Features
🤖 AI-Powered Verification — GenLayer validators use LLMs to judge submitted facts
🔒 Immutable Storage — Approved facts are stored permanently on-chain
🌍 Decentralized — No central authority controls what gets approved
⚡ Two Categories — Technology and Science facts only
🚫 No Politics — Political content is automatically rejected
🇬🇧 English Only — Content must be in English
🎨 Beautiful UI — Dark futuristic design
---
🛠️ Tech Stack
Layer	Technology
Smart Contract	Python (GenLayer Intelligent Contract)
Frontend	HTML, CSS, JavaScript (ES6)
Blockchain	GenLayer Studio Testnet
AI Validators	GPT-4, Claude, Gemini (via GenLayer)
Dev Server	Vite
Wallet	MetaMask
---
📁 Project Structure
```
cortex-ledger/
├── public/
│   ├── index.html        # Homepage — shows all verified facts
│   └── submit.html       # Submit page — submit new facts for verification
├── contracts/
│   └── review.py         # GenLayer Intelligent Contract
├── package.json
├── vite.config.js
└── README.md
```
---
 Getting Started
Prerequisites
Node.js v18+
MetaMask browser extension
GenLayer Studio account
Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/cortex-ledger.git

# Navigate to project folder
cd cortex-ledger

# Install dependencies
npm install

# Start development server
npm run dev
```
Open `http://localhost:5173` in your browser.
---
 How to Use
Browsing Facts
Open the homepage
Browse all AI-verified facts
Filter by Technology or Science
Submitting a Fact
Connect your MetaMask wallet
Go to the Submit page
Select a category (Technology or Science)
Enter a title and detailed content
Click "Submit for Verification"
Sign the transaction in MetaMask
Wait for GenLayer AI validators to review (~30 seconds on Studio)
If approved → fact appears on the ledger!
--- How the AI Verification Works
When a user submits a fact, the GenLayer Intelligent Contract:
Sends the fact to multiple AI validator nodes
Each validator independently runs the fact through an LLM prompt
The prompt checks 4 rules:
Is the content in English?
Does it contain political content? (rejected if yes)
Is the category Technology or Science?
Is the fact real, verifiable, and at least 2 sentences long?
Validators reach consensus using GenLayer's Equivalence Principle
If approved → fact is stored on-chain permanently
If rejected → fact is discarded with a reason
This process is completely decentralized — no single entity controls the outcome.
---
Smart Contract
The contract is written in Python using GenLayer Intelligent Contract framework:
```python
# v0.2.16
from genlayer import *
import json

class CortexLedger(gl.Contract):
    verified_ledger: DynArray[str]

    def __init__(self):
        pass

    @gl.public.view
    def get_verified_ledger(self) -> list:
        return list(self.verified_ledger)

    @gl.public.write
    def submit_fact(self, category: str, title: str, content: str) -> None:
        # AI validates the fact using GenLayer's consensus mechanism
        ...
```
---
🌐 Network Configuration
To connect MetaMask to GenLayer Studio:
Setting	Value
Network Name	GenLayer Studio
RPC URL	`https://studio.genlayer.com/api`
Chain ID	`61999`
Currency Symbol	`GEN`
---
 Verification Rules
Facts must pass ALL of the following rules to be approved:
✅ English Only — Content must be written in English
✅ No Politics — No political content, politicians, or government policies
✅ Correct Category — Must be Technology or Science
✅ Quality Check — Must be real, verifiable, and at least 2 sentences long
---

 Acknowledgments
GenLayer : for building the first AI-powered blockchain
GenLayer Docs : for comprehensive documentation
GenLayer Studio : for the development environment
---
thank you all the team GenLayer

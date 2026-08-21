RedShield AIAutomated LLM Red-Teaming & Security Guardrails for CI/CD PipelinesRedShield AI is a production-grade security auditing system that automatically evaluates LLM applications and RAG pipelines for vulnerabilities—such as PII leakage, system prompt extraction, and deep semantic jailbreaks—directly within developer workflows.



Key Engineering HighlightsAsynchronous Fail-Fast Architecture: Optimized evaluation latency by short-circuiting obvious security breaches at deterministic layers (< 5ms) before invoking heavier semantic models.Non-Blocking Webhook Listener: Uses FastAPI Background Tasks to process multi-vector adversarial test suites asynchronously, returning immediate 202 Accepted responses to prevent CI/CD pipeline timeouts.Zero-Cost Local AI Judge: Integrated a local Ollama instance (llama3.2:1b) to act as an offline, privacy-focused semantic evaluator without relying on paid 3rd-party APIs.Live Observability Dashboard: Built a React & Tailwind telemetry dashboard that streams real-time test run metrics, risk scores, and prompt-level inspection breakdown.

 


System Architecture                [ GitHub Push Event ]
                                            │
                                            ▼
                               [ Localtunnel / Ngrok Listener ]
                                            │
                                            ▼
                                 [ FastAPI Webhook Engine ]
                                            │
                                 (Async Background Task)
                                            │
                                            ▼
                         [ Adversarial Attack Suite Execution ]
                                            │
                                            ▼
                    ┌──────────────────────────────────────────────┐
                    │       4-Layer Hybrid Defense Mesh            │
                    ├──────────────────────────────────────────────┤
                    │ Layer 1: Presidio & Shannon Entropy Scanner  │
                    │ Layer 2: Regex & Semantic Pattern Matcher    │
                    │ Layer 3: Anchor-Restricted Refusal Guard     │
                    │ Layer 4: Local Ollama AI Judge (Fallback)    │
                    └──────────────────────────────────────────────┘
                                            │
                                            ▼
                             [ SQLAlchemy / SQLite DB Store ]
                                            │
                                            ▼
                              [ React Telemetry Dashboard ]




4-Layer Security MeshLayerEvaluatorTarget ThreatPrimary BenefitLayer 1Presidio + Shannon EntropyPII (Emails, Keys, API Tokens)Fast execution (< 5ms), zero compute overheadLayer 2Extended Regex RulesSystem Prompt Leaks & OverridesCatch direct prompt injections instantlyLayer 3Anchor-Restricted GuardPartial Compliance & Fake RefusalsValidates initial 100-char response safetyLayer 4Ollama (llama3.2:1b)Complex Jailbreaks & Persona ShiftsDeep contextual semantic analysis Quick Start1. PrerequisitesPython: 3.11+Node.js: 18+Ollama: Installed locally with llama3.2:1b model pulled (ollama pull llama3.2:1b)2. Backend SetupBashcd backend


python -m venv venv
# On Windows:

.\venv\Scripts\Activate.ps1

# On Linux/Mac:

source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000


3. Frontend SetupBashcd frontend

npm install
npm run dev

4. Connect Webhook TunnelBash# In a new terminal tab

npx localtunnel --port 8000


Copy the generated public URL and add it under your GitHub Repository Settings ➔ Webhooks as https://<your-tunnel-url>/api/v1/webhooks/github.Triggering an AuditSimply push a commit to your main branch to trigger the automated security scan:Bashgit commit --allow-empty -m "test: trigger redshield automated security check"

git push origin main

Navigate to http://localhost:5173 to inspect live execution telemetry and vulnerability reports!

# Design Note — Zycus AI Support System

## 1. Production Failure Modes and Mitigations

The system uses a Retrieval-Augmented Generation (RAG) architecture for support ticket triage and account health analysis. A production deployment can fail at several points in this pipeline.

The first failure mode is Knowledge Base retrieval failure. If the vector database is unavailable or retrieval returns poor results, the LLM may not have enough relevant context to make a reliable decision. This can be mitigated by adding retrieval confidence thresholds, monitoring retrieval latency, and providing a controlled fallback response when relevant documents cannot be retrieved.

The second failure mode is LLM/API failure. The Gemini API can experience timeouts, rate limits, quota exhaustion, or temporary service failures. Production code should use retry policies with exponential backoff, timeouts, and circuit breakers. Requests should also be logged with a correlation ID so failed requests can be investigated.

Another failure mode is malformed LLM output. The application currently expects structured JSON from the model. In production, the output should be validated against a strict schema before it is returned to downstream systems. Invalid responses should be retried or routed to a safe fallback instead of being accepted.

Data quality is another important failure mode. Missing account IDs, incorrect ticket timestamps, duplicate records, or inconsistent product names can produce incorrect account-health summaries. Input validation, data-quality checks, and monitoring should therefore be performed before the data reaches the AI pipeline.

---

## 2. Latency vs. Quality Trade-offs

RAG systems have several stages that contribute to latency: embedding, vector retrieval, prompt construction, and LLM generation.

Increasing the number of retrieved documents can improve answer quality because the model receives more context. However, retrieving too many documents increases prompt size, token usage, and response latency. The current system uses a small top-k value to keep the context focused.

For a production system, retrieval quality should be measured rather than simply increasing top-k. A reranker could be introduced to select the most relevant documents before sending them to the LLM.

Model selection also creates a quality-versus-latency trade-off. A larger model may produce better reasoning but can increase response time and cost. A smaller model can be used for simple classification tasks, while more complex cases can be routed to a stronger model.

Caching can also reduce latency. Frequently requested Knowledge Base information can be cached, while embeddings should be generated once and reused rather than recalculated for every request.

The goal should be to maintain sufficient accuracy while keeping response latency predictable for support agents.

---

## 3. Data Sensitivity and PII Handling

Support tickets and account information may contain sensitive business information and personally identifiable information (PII), including customer names, contact information, account identifiers, and internal support details.

The system should follow data-minimization principles. Only information required for the specific AI task should be included in the prompt. Sensitive fields that are not necessary for classification or summarization should be removed or masked before being sent to an external model.

API keys and credentials must never be stored in source code. They should be loaded from environment variables or a secure secrets-management system. The repository should contain only a `.env.example` file with placeholder values.

Access to account and ticket information should also be controlled using role-based access control. Logs should avoid storing complete ticket contents or unnecessary PII. Production logs should contain identifiers and metadata required for troubleshooting while protecting sensitive customer information.

Data retention policies should also define how long prompts, model responses, logs, and customer data are stored.

---

## 4. Scaling to 10× Volume

The current implementation is suitable as a prototype, but production scaling to 10× the current ticket volume would require several architectural changes.

The Knowledge Base should be indexed in a persistent vector database rather than rebuilt unnecessarily for every request. Embeddings should be generated asynchronously when documents are added or updated.

The API layer should be stateless so multiple application instances can run behind a load balancer. Ticket processing can be moved to an asynchronous queue for high-volume workloads. Workers can then process tickets independently and scale horizontally based on queue size.

LLM calls should use controlled concurrency and rate limiting to prevent API quota exhaustion. Caching can reduce repeated retrieval and generation requests.

Observability is also important at scale. The system should track request latency, retrieval latency, LLM latency, error rates, token usage, API failures, retrieval quality, and classification accuracy.

Finally, evaluation should run continuously using a representative test set. This helps detect model changes, Knowledge Base changes, and data distribution changes before they affect production users.

---

## Conclusion

The prototype demonstrates a grounded AI support workflow using ticket data, account data, Knowledge Base retrieval, and LLM-based reasoning. For production, reliability, security, observability, evaluation, and horizontal scalability should be added around the existing RAG pipeline.
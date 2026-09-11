# V7 Architecture Overview

```text
CLI / API
   |
   v
Requirement Agent -----> AI Reasoning Agent
   |                         |
   +------------+------------+
                v
        Dependency Task Graph
                |
       +--------+---------+
       |                  |
 Greenfield           Brownfield
       |                  |
 Architecture       Codebase Reasoning
 Schema              Impact Assessment
 Code                Targeted Change
 Tests               Regression Tests
       |                  |
       +--------+---------+
                v
           Validation
          /     |      \
 Security     SRE    Engineering
 Review       Review     Review
          \     |      /
                v
         Deterministic
          Release Gate
                |
         Human Approval
                |
                v
       Engineering Evidence
```

### Core principle
**AI proposes; deterministic validation and policy constrain; humans approve high-impact decisions.**

### Evidence chain
Requirement → reasoning → task graph → architecture → API/schema → code → tests → validation → security/SRE/engineering reviews → release decision → documentation.

### Production boundary
The prototype deliberately keeps the orchestration process local and deterministic. Production deployment can replace local state/checkpointing with durable workflow infrastructure, use PostgreSQL/Redis, integrate enterprise identity and approvals, and connect the generated deployment contracts to the target platform.

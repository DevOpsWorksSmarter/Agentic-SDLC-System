# V7 Scenario Demonstration

## 1. Greenfield — mandatory URL shortener
**Input:** Build a scalable URL shortener service with APIs, persistence, and analytics.

Expected lifecycle: requirement → decomposition → architecture → schema → analytics → code → tests → validation → security → SRE → engineering review → release gate → documentation.

## 2. Brownfield
**Input:** Enhance the existing URL shortener to support configurable link expiration.

Expected lifecycle: AI reasoning → codebase analysis → impact assessment → targeted code change → regression tests → validation → security/SRE review → engineering review → release gate → documentation.

## 3. Ambiguous
**Input:** Make the service fast and scalable.

The system identifies missing targets and records explicit assumptions such as a 10k RPS capacity target and p99 redirect latency below 50ms. The assumptions are carried into planning and validation rather than silently disappearing.

## Failure/recovery scenario
A task can fail and be retried. Bounded repair is allow-listed; unrecognized repair requests remain human-controlled. Downstream tasks are not allowed to proceed from a failed dependency.

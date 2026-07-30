# PROJECTCONTEXT.md

> **Purpose:** This document provides AI coding agents (Codex, Claude Code, Cursor, Gemini CLI, Cline, Windsurf, etc.) with the architectural context, constraints, and development conventions required to contribute consistently to the FairExplain AI project.

---

# Project Identity

**Project Name:** FairExplain AI

**Project Type:** Enterprise-grade full-stack web application

**Current Status:** MVP Development

**Purpose:**
Build an Explainable AI platform that evaluates scholarship eligibility, reduces the required education loan, and generates transparent AI explanations while ensuring every final decision remains with a human reviewer.

---

# Core Principles

The following principles are **non-negotiable**:

- The Rule Engine is the single source of truth.
- The LLM never calculates scores.
- The LLM never changes decisions.
- AI provides recommendations only.
- Humans make final decisions.

> **The AI recommends. Humans decide.**

---

# What This Project Is

- A deterministic rule-engine application.
- An explainable AI system.
- A modern full-stack web application.
- A portfolio-quality enterprise project.

## What This Project Is NOT

- A chatbot.
- An autonomous loan approval system.
- An AI-first decision engine.
- An application where the LLM performs business logic.

---

# Technology Stack

## Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Hook Form
- TanStack Query
- Recharts

## Backend

- FastAPI
- Python
- SQLAlchemy
- PostgreSQL

## Database

- Neon PostgreSQL

## Deployment

- Frontend → Vercel
- Backend → Railway

## AI Components

- OCR
- Rule Engine
- Gemini/OpenAI
- Fairness Checker

---

# High-Level Architecture

Frontend

↓

REST API

↓

Business Services

↓

Rule Engine

↓

Database

↓

LLM Explanation Layer

↓

PDF Report Generation

---

# Documentation Priority

Always consult these files before implementing new functionality.

1. RULE_ENGINE.md
2. DATA_MODEL.md
3. ARCHITECTURE.md
4. SRS.md
5. PRD.md
6. PROMPTS.md
7. ROADMAP.md
8. README.md
9. CONTEXT.md

If two documents conflict, prefer the most specific one.

---

# Development Philosophy

Always prefer:

- Readability over cleverness
- Maintainability over shortcuts
- Explicit code over hidden magic
- Reusable components over duplication
- Composition over inheritance
- Strong typing over weak typing

---

# Backend Rules

Always:

- Keep business logic inside services.
- Keep routers thin.
- Validate every request.
- Use Pydantic schemas.
- Use SQLAlchemy models.
- Keep calculations outside API routes.

Never:

- Put business logic inside routers.
- Query the database directly from UI code.
- Duplicate rule calculations.

---

# Frontend Rules

Always:

- Build reusable components.
- Separate pages, components, hooks, services, and utilities.
- Keep API logic inside service layers.
- Use strict TypeScript.

Never:

- Hardcode API responses.
- Duplicate forms.
- Place API calls inside reusable UI components.

---

# AI Rules

The AI agent MUST NEVER:

- Calculate scholarship scores.
- Calculate loan eligibility.
- Modify Rule Engine outputs.
- Invent confidence values.
- Infer missing financial data.

The AI agent MAY:

- Explain results.
- Generate UI copy.
- Produce reports.
- Summarize recommendations.

---

# Security Rules

Always:

- Store secrets in environment variables.
- Validate user input.
- Encrypt sensitive data.
- Keep AI provider keys server-side.

Never:

- Commit secrets.
- Expose API keys.
- Call LLM providers directly from the frontend.

---

# Code Quality Standards

Every contribution should be:

- Typed
- Modular
- Testable
- Reusable
- Readable
- Production-ready

Prefer smaller files and reusable abstractions.

---

# UI Guidelines

Style:

- Modern
- Minimal
- Professional
- Accessible

Use:

- Tailwind CSS
- shadcn/ui
- Lucide Icons

Keep animations subtle.

---

# Error Handling

Every API response should include:

- success
- data
- message
- errors

Never expose internal stack traces.

---

# Performance Goals

- API response time under 3 seconds
- Lazy loading where appropriate
- Pagination for large datasets
- Optimistic updates when beneficial

---

# Before Implementing Any Feature

1. Read the relevant documentation.
2. Search the existing codebase.
3. Reuse existing components.
4. Reuse existing services.
5. Avoid architectural rewrites.
6. Keep changes focused.
7. Follow existing naming conventions.

---

# AI Agent Checklist

Before completing any task, verify:

- Project builds successfully.
- No TypeScript errors.
- No lint errors.
- No architecture violations.
- No duplicated logic.
- Rule Engine remains the source of truth.
- No secrets are exposed.
- Documentation stays consistent with the implementation.

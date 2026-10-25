"""
FairExplain AI — Explanation Service
======================================
Coordinates domain telemetry serialization, LLM provider invocation,
guardrail enforcement, and audit persistence in ExplanationReport.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import Application
from app.models.evaluation import ScholarshipEvaluationModel, TuitionAccountSummaryModel
from app.models.explanation_report import AssessmentType, ExplanationReport
from app.repositories.evaluation_repository import EvaluationRepository
from app.repositories.mappers import orm_to_domain_accounting, orm_to_domain_evaluation
from app.services.llm.base import BaseLLMProvider
from app.services.llm.guardrails import GuardrailValidationError, validate_explanation_json
from app.services.llm.prompt_templates import build_input_telemetry
from app.services.llm.template_provider import DeterministicTemplateProvider


class ExplanationService:
    """Orchestrates plain-English explanation generation and guardrails."""

    @classmethod
    async def generate_explanation(
        cls,
        application_id: uuid.UUID,
        db: AsyncSession,
        provider: BaseLLMProvider | None = None,
    ) -> dict[str, Any]:
        """
        Generate, validate, and persist an explainable report for an application.
        Guarantees zero-calculation integrity and demographic neutrality.
        """
        eval_repo = EvaluationRepository(db)

        # 1. Fetch latest evaluation and accounting summary
        eval_model = await eval_repo.get_latest_evaluation(application_id)
        if not eval_model:
            raise ValueError(f"No scholarship evaluation found for application {application_id}.")

        acct_model = await eval_repo.get_tuition_summary(application_id)

        # 2. Convert to domain dataclasses for pure telemetry serialization
        domain_eval = orm_to_domain_evaluation(eval_model)
        domain_acct = orm_to_domain_accounting(acct_model) if acct_model else None

        # 3. Build input telemetry
        telemetry = build_input_telemetry(
            eval_result=domain_eval,
            accounting_summary=domain_acct,
            engine_version="1.0.0-phase1b",
        )

        # 4. Invoke provider with fallback on failure
        active_provider = provider or DeterministicTemplateProvider()
        raw_output = await active_provider.generate_explanation(telemetry)

        # 5. Guardrail validation
        try:
            validated_data = validate_explanation_json(raw_output, telemetry)
        except GuardrailValidationError:
            # Fall back to deterministic template
            fallback = DeterministicTemplateProvider()
            raw_fallback = await fallback.generate_explanation(telemetry)
            validated_data = validate_explanation_json(raw_fallback, telemetry)

        # 6. Store or update ExplanationReport
        stmt = (
            select(ExplanationReport)
            .where(
                ExplanationReport.assessment_id == eval_model.id,
                ExplanationReport.assessment_type == AssessmentType.scholarship,
            )
        )
        res = await db.execute(stmt)
        report = res.scalar_one_or_none()

        if report:
            report.recommendation_text = validated_data["summary_headline"]
            report.reasons = validated_data["reasons"]
            report.confidence_note = validated_data["fairness_attestation"]
            report.fairness_note = validated_data["human_review_notice"]
            report.llm_prompt_version = "v1.0-phase4"
        else:
            report = ExplanationReport(
                assessment_type=AssessmentType.scholarship,
                assessment_id=eval_model.id,
                recommendation_text=validated_data["summary_headline"],
                reasons=validated_data["reasons"],
                confidence_note=validated_data["fairness_attestation"],
                fairness_note=validated_data["human_review_notice"],
                llm_prompt_version="v1.0-phase4",
            )
            db.add(report)

        await db.commit()

        return {
            "application_id": str(application_id),
            "assessment_id": str(eval_model.id),
            "explanation": validated_data,
            "prompt_version": "v1.0-phase4",
        }

    @classmethod
    async def get_explanation(
        cls, application_id: uuid.UUID, db: AsyncSession
    ) -> dict[str, Any] | None:
        """Fetch existing explanation report for application."""
        eval_repo = EvaluationRepository(db)
        eval_model = await eval_repo.get_latest_evaluation(application_id)
        if not eval_model:
            return None

        stmt = select(ExplanationReport).where(
            ExplanationReport.assessment_id == eval_model.id,
            ExplanationReport.assessment_type == AssessmentType.scholarship,
        )
        res = await db.execute(stmt)
        report = res.scalar_one_or_none()
        if not report:
            return None

        return {
            "application_id": str(application_id),
            "assessment_id": str(eval_model.id),
            "explanation": {
                "summary_headline": report.recommendation_text,
                "reasons": report.reasons,
                "fairness_attestation": report.confidence_note,
                "human_review_notice": report.fairness_note,
            },
            "prompt_version": report.llm_prompt_version,
        }

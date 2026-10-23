"""
FairExplain AI — Tuition Accounting Engine
==========================================
Deterministic calculation of payable tuition, confirmed award allocations,
independent waiver allowance tracking, program/institutional caps, and unapplied surplus.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from app.domain.enums import AwardStatus, AwardType
from app.domain.exceptions import (
    IncompatibleAwardsError,
    InvalidMonetaryValueError,
    MissingAwardPriorityError,
    TiedAwardPriorityError,
)
from app.domain.models import (
    AwardAllocationResult,
    AwardSpecification,
    InstitutionalCap,
    TuitionAccountSummary,
    quantize_currency,
)


def calculate_tuition_accounting(
    gross_eligible_tuition: Decimal | int | float | str,
    awards: Sequence[AwardSpecification],
    institutional_cap: InstitutionalCap | None = None,
) -> TuitionAccountSummary:
    """
    Deterministically allocate confirmed scholarship awards against gross tuition.

    Key Invariants:
    1. remaining_payable and remaining_waiver_allowance are tracked independently.
    2. Only awards with status CONFIRMED reduce payable tuition.
    3. Confirmed awards are processed in strictly ascending priority order.
    4. Missing or tied priority on confirmed awards raises an explicit exception.
    5. Incompatible confirmed awards raise an IncompatibleAwardsError.
    6. Effective reduction never exceeds remaining payable tuition or remaining waiver allowance.
    7. Unapplied surplus is reported separately and is never automatically converted into cash.
    """
    gross_tuition = quantize_currency(gross_eligible_tuition)
    if gross_tuition < Decimal("0.00"):
        raise InvalidMonetaryValueError("Gross eligible tuition cannot be negative.")

    # 1. Determine initial waiver allowance
    is_cap_configured = (
        institutional_cap is not None
        and (
            institutional_cap.max_waiver_amount is not None
            or institutional_cap.max_waiver_percentage is not None
        )
    )
    if institutional_cap is not None:
        effective_cap = institutional_cap.calculate_effective_cap(gross_tuition)
    else:
        # If no institutional cap is configured, allowance is gross eligible tuition
        effective_cap = gross_tuition

    # Initial state
    remaining_payable = gross_tuition
    remaining_waiver_allowance = min(gross_tuition, effective_cap)

    # 2. Partition into confirmed vs unconfirmed awards
    confirmed_awards: list[AwardSpecification] = []
    unconfirmed_awards: list[AwardSpecification] = []

    for award in awards:
        if award.status == AwardStatus.CONFIRMED:
            confirmed_awards.append(award)
        else:
            unconfirmed_awards.append(award)

    # 3. Validate priority on confirmed awards
    seen_priorities: dict[int, AwardSpecification] = {}
    for award in confirmed_awards:
        if award.priority is None:
            raise MissingAwardPriorityError(
                f"Confirmed award '{award.award_id}' (program '{award.program_id}') "
                "lacks an explicit priority rank."
            )
        if type(award.priority) is not int or award.priority <= 0:
            raise MissingAwardPriorityError(
                f"Confirmed award '{award.award_id}' priority must be a positive integer, "
                f"got: {award.priority!r}"
            )
        if award.priority in seen_priorities:
            prior_award = seen_priorities[award.priority]
            raise TiedAwardPriorityError(
                f"Confirmed awards '{prior_award.award_id}' and '{award.award_id}' "
                f"share tied priority rank {award.priority}. "
                "Priority must be strictly unique across confirmed awards."
            )
        seen_priorities[award.priority] = award

    # 4. Check compatibility / exclusivity between confirmed awards
    for i, a1 in enumerate(confirmed_awards):
        for a2 in confirmed_awards[i + 1 :]:
            if (
                a2.program_id in a1.incompatible_programs
                or a1.program_id in a2.incompatible_programs
            ):
                raise IncompatibleAwardsError(
                    f"Incompatible confirmed awards detected: '{a1.award_id}' "
                    f"(program '{a1.program_id}') and '{a2.award_id}' "
                    f"(program '{a2.program_id}') are mutually exclusive."
                )

    # 5. Sort confirmed awards by priority ascending (1 is highest priority)
    confirmed_awards.sort(key=lambda a: a.priority)  # type: ignore[arg-type]

    # 6. Allocate confirmed awards
    allocations: list[AwardAllocationResult] = []
    total_effective_reduction = Decimal("0.00")
    total_unapplied_surplus = Decimal("0.00")

    for award in confirmed_awards:
        # Calculate nominal amount
        if award.award_type == AwardType.FIXED_AMOUNT:
            if award.amount is None:
                raise InvalidMonetaryValueError(
                    f"Award '{award.award_id}' specifies FIXED_AMOUNT but has no amount defined."
                )
            nominal_amount = award.amount
        elif award.award_type == AwardType.PERCENTAGE_OF_TUITION:
            if award.percentage is None:
                raise InvalidMonetaryValueError(
                    f"Award '{award.award_id}' specifies PERCENTAGE_OF_TUITION but has no percentage defined."
                )
            nominal_amount = quantize_currency(
                gross_tuition * (award.percentage / Decimal("100.00"))
            )
        else:
            raise InvalidMonetaryValueError(
                f"Unsupported award type: '{award.award_type}'"
            )

        # Apply program-level cap
        if award.max_award_cap is not None:
            capped_amount = min(nominal_amount, award.max_award_cap)
        else:
            capped_amount = nominal_amount

        # Calculate effective reduction
        effective_reduction = min(
            capped_amount, remaining_payable, remaining_waiver_allowance
        )
        unapplied_surplus = capped_amount - effective_reduction

        # Determine cap reason if surplus exists
        cap_reason = None
        if unapplied_surplus > Decimal("0.00"):
            if is_cap_configured and remaining_waiver_allowance < remaining_payable:
                cap_reason = "Institutional waiver cap reached"
            elif remaining_payable < remaining_waiver_allowance:
                cap_reason = "Remaining payable tuition reached zero"
            elif is_cap_configured and effective_cap < gross_tuition:
                # Tie: both equal, but institutional cap strictly constrained gross tuition
                cap_reason = "Institutional waiver cap reached"
            else:
                # Unconstrained or cap >= gross tuition: tuition exhaustion is primary
                cap_reason = "Remaining payable tuition reached zero"

        # Update running balances
        remaining_payable = quantize_currency(remaining_payable - effective_reduction)
        remaining_waiver_allowance = quantize_currency(
            remaining_waiver_allowance - effective_reduction
        )

        total_effective_reduction = quantize_currency(
            total_effective_reduction + effective_reduction
        )
        total_unapplied_surplus = quantize_currency(
            total_unapplied_surplus + unapplied_surplus
        )

        allocations.append(
            AwardAllocationResult(
                award_id=award.award_id,
                program_id=award.program_id,
                title=award.title,
                priority=award.priority,  # type: ignore[arg-type]
                status=award.status,
                nominal_amount=nominal_amount,
                capped_amount=capped_amount,
                effective_reduction=effective_reduction,
                unapplied_surplus=unapplied_surplus,
                cap_reason=cap_reason,
            )
        )

    return TuitionAccountSummary(
        gross_eligible_tuition=gross_tuition,
        institutional_cap_applied=effective_cap,
        total_effective_reduction=total_effective_reduction,
        remaining_payable_tuition=remaining_payable,
        remaining_waiver_allowance=remaining_waiver_allowance,
        total_unapplied_surplus=total_unapplied_surplus,
        confirmed_allocations=allocations,
        unconfirmed_awards=unconfirmed_awards,
    )

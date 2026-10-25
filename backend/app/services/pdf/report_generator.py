"""
FairExplain AI — Assessment & Decision Support PDF Compiler
=============================================================
Compiles official, tamper-evident PDF assessment reports with embedded SHA-256 audit digest.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.services.llm.prompt_templates import MANDATORY_HUMAN_REVIEW_NOTICE
from app.services.pdf.hasher import compute_audit_hash


def generate_assessment_pdf(data: dict[str, Any]) -> tuple[bytes, str]:
    """
    Generate downloadable PDF document in-memory.
    Returns (pdf_bytes, sha256_checksum).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=12,
    )
    section_heading = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyDark",
        parent=styles["Normal"],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
    )
    bold_style = ParagraphStyle(
        "BoldDark",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    disclaimer_style = ParagraphStyle(
        "Disclaimer",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#dc2626"),
        fontName="Helvetica-Oblique",
    )
    hash_style = ParagraphStyle(
        "HashStyle",
        parent=styles["Normal"],
        fontSize=7,
        leading=9,
        fontName="Courier",
        textColor=colors.HexColor("#475569"),
    )

    story = []

    # 1. Header & Title
    story.append(Paragraph("FairExplain AI — Assessment & Decision Support Report", title_style))
    app_id = data.get("application_id", "N/A")
    created_at = data.get("created_at", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    story.append(
        Paragraph(
            f"Application Reference: <b>{app_id}</b> &nbsp;|&nbsp; Generated: {created_at}",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

    # 2. Applicant Profile Table
    story.append(Paragraph("1. Applicant Profile & Verified Data", section_heading))
    applicant = data.get("applicant", {})
    academic = data.get("academic", {})
    financial = data.get("financial", {})

    profile_data = [
        [
            Paragraph("<b>Applicant Name:</b>", body_style),
            Paragraph(str(applicant.get("name", "N/A")), body_style),
            Paragraph("<b>Email:</b>", body_style),
            Paragraph(str(applicant.get("email", "N/A")), body_style),
        ],
        [
            Paragraph("<b>CGPA:</b>", body_style),
            Paragraph(f"{academic.get('cgpa', 'N/A')} / 10.0", body_style),
            Paragraph("<b>Active Backlogs:</b>", body_style),
            Paragraph(str(academic.get("backlogs", 0)), body_style),
        ],
        [
            Paragraph("<b>Household Income:</b>", body_style),
            Paragraph(f"₹{Decimal(str(financial.get('household_income', 0))):,.2f} / yr", body_style),
            Paragraph("<b>Existing Monthly EMI:</b>", body_style),
            Paragraph(f"₹{Decimal(str(financial.get('existing_emi', 0))):,.2f} / mo", body_style),
        ],
    ]
    t_profile = Table(profile_data, colWidths=[120, 150, 120, 150])
    t_profile.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(t_profile)
    story.append(Spacer(1, 10))

    # 3. Scholarship Determination & Tuition Accounting
    story.append(Paragraph("2. Deterministic Scholarship & Tuition Accounting", section_heading))
    scholarship = data.get("scholarship", {})
    tuition = scholarship.get("tuition_accounting", {})

    acct_data = [
        [
            Paragraph("<b>Eligibility Outcome:</b>", bold_style),
            Paragraph(str(scholarship.get("status", "ELIGIBLE")).upper(), bold_style),
            Paragraph("<b>Gross Annual Tuition:</b>", body_style),
            Paragraph(f"₹{Decimal(str(tuition.get('gross_eligible_tuition', 0))):,.2f}", body_style),
        ],
        [
            Paragraph("<b>Fee Reductions Applied:</b>", body_style),
            Paragraph(f"₹{Decimal(str(tuition.get('total_effective_reduction', 0))):,.2f}", body_style),
            Paragraph("<b>Remaining Payable Tuition:</b>", bold_style),
            Paragraph(f"₹{Decimal(str(tuition.get('remaining_payable_tuition', 0))):,.2f}", bold_style),
        ],
        [
            Paragraph("<b>Unapplied Award Surplus:</b>", body_style),
            Paragraph(f"₹{Decimal(str(tuition.get('total_unapplied_surplus', 0))):,.2f}", body_style),
            Paragraph("<b>Institutional Policy Cap:</b>", body_style),
            Paragraph(f"₹{Decimal(str(tuition.get('institutional_cap_applied', 0))):,.2f}", body_style),
        ],
    ]
    t_acct = Table(acct_data, colWidths=[130, 140, 140, 130])
    t_acct.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(t_acct)
    story.append(Spacer(1, 10))

    # 4. Loan Affordability Check
    loan = data.get("loan", {})
    if loan:
        story.append(Paragraph("3. Education Loan Serviceability Check", section_heading))
        loan_data = [
            [
                Paragraph("<b>Loan Outcome:</b>", bold_style),
                Paragraph(str(loan.get("outcome", "ELIGIBLE")).upper(), bold_style),
                Paragraph("<b>Post-Scholarship Loan:</b>", body_style),
                Paragraph(f"₹{Decimal(str(loan.get('post_scholarship_loan_amount', 0))):,.2f}", body_style),
            ],
            [
                Paragraph("<b>Monthly Debt Capacity:</b>", body_style),
                Paragraph(f"₹{Decimal(str(loan.get('available_monthly_capacity', 0))):,.2f}", body_style),
                Paragraph("<b>Estimated Monthly EMI:</b>", body_style),
                Paragraph(f"₹{Decimal(str(loan.get('estimated_emi', 0))):,.2f}", body_style),
            ],
        ]
        t_loan = Table(loan_data, colWidths=[130, 140, 140, 130])
        t_loan.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(t_loan)
        story.append(Spacer(1, 10))

    # 5. Explainable AI Narrative
    story.append(Paragraph("4. Explainable AI Narrative & Findings", section_heading))
    explanation = data.get("explanation", {})
    headline = explanation.get("summary_headline", "Recommendation generated.")
    story.append(Paragraph(f"<b>Summary:</b> {headline}", body_style))
    story.append(Spacer(1, 4))

    reasons = explanation.get("reasons", [])
    if reasons:
        story.append(Paragraph("<b>Key Supporting Factors:</b>", body_style))
        for r in reasons:
            story.append(Paragraph(f"• {r}", body_style))
        story.append(Spacer(1, 4))

    acct_exp = explanation.get("accounting_explanation")
    if acct_exp:
        story.append(Paragraph(f"<b>Accounting Rationale:</b> {acct_exp}", body_style))
        story.append(Spacer(1, 8))

    # 6. Human Governance Notice
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#fca5a5"), spaceAfter=6))
    story.append(Paragraph(f"<b>NOTICE OF HUMAN AUTHORITY:</b> {MANDATORY_HUMAN_REVIEW_NOTICE}", disclaimer_style))
    story.append(Spacer(1, 10))

    # 7. Cryptographic Audit Footprint
    audit_hash = compute_audit_hash(data)
    story.append(
        Paragraph(
            f"CRYPTOGRAPHIC AUDIT DIGEST (SHA-256):<br/>{audit_hash}",
            hash_style,
        )
    )

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes, audit_hash

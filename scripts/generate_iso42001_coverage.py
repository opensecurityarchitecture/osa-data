#!/usr/bin/env python3
"""Generate ISO/IEC 42001:2023 (AI Management System) coverage analysis JSON.

Reads all SP 800-53 Rev 5 control files via _manifest.json, builds reverse
mappings from iso_42001_2023 clause IDs to controls, then produces a
framework-coverage JSON with expert coverage assessments.

Output: data/framework-coverage/iso-42001-2023.json
"""

import json
import os
import re
from collections import defaultdict

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTROLS_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'controls')
COVERAGE_DIR = os.path.join(SCRIPT_DIR, '..', 'data', 'framework-coverage')
OUTPUT_FILE = os.path.join(COVERAGE_DIR, 'iso-42001-2023.json')

FRAMEWORK_ID = "iso_42001_2023"
FRAMEWORK_KEY = "iso_42001_2023"


def natural_sort_key(s):
    """Sort key that handles mixed alpha-numeric clause IDs naturally."""
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r'(\d+)', s)
    ]


def load_manifest():
    with open(os.path.join(CONTROLS_DIR, '_manifest.json')) as f:
        return json.load(f)


def build_reverse_mappings():
    """Read every control JSON and build clause -> [control_ids] mapping."""
    manifest = load_manifest()
    reverse = defaultdict(list)

    for ctrl_entry in manifest['controls']:
        ctrl_file = os.path.join(CONTROLS_DIR, ctrl_entry['file'])
        with open(ctrl_file) as f:
            ctrl = json.load(f)
        clauses = ctrl.get('compliance_mappings', {}).get(FRAMEWORK_KEY, [])
        for clause_id in clauses:
            reverse[clause_id].append(ctrl['id'])

    # Sort control lists
    for clause_id in reverse:
        reverse[clause_id] = sorted(reverse[clause_id])

    return reverse


# ---- Expert clause definitions ----
# Each clause has: id, title, coverage_pct, rationale, gaps
# Controls are filled from reverse mappings automatically.

CLAUSE_DEFINITIONS = [
    {
        "id": "A.2.2",
        "title": "AI policy",
        "coverage_pct": 70,
        "rationale": "AC-01 and PL-01/PL-02 cover security policy and planning. General policy frameworks apply, but AI-specific policy elements are not addressed.",
        "gaps": "ISO 42001 A.2.2 requires an AI-specific policy covering responsible AI principles, ethical use, and AI governance. SP 800-53 policies are security/privacy-focused and do not address AI ethics, fairness, or responsible AI commitments."
    },
    {
        "id": "A.2.3",
        "title": "AI roles and responsibilities",
        "coverage_pct": 65,
        "rationale": "AC-01 and PL-01 assign security roles and responsibilities. Applicable to AI roles in a general sense.",
        "gaps": "ISO 42001 requires AI-specific roles such as AI system owner, AI ethics officer, and AI risk manager. SP 800-53 defines security roles but not AI governance, AI ethics, or AI-specific accountability structures."
    },
    {
        "id": "A.2.4",
        "title": "Monitoring, measurement, and review of AI systems",
        "coverage_pct": 55,
        "rationale": "CA-07 continuous monitoring; PL-03 plan update; RA-04 risk assessment update. These cover security monitoring and review cycles.",
        "gaps": "ISO 42001 requires monitoring AI system performance, bias drift, model accuracy, and fairness metrics over time. SP 800-53 monitoring focuses on security events and vulnerabilities, not AI-specific performance degradation, concept drift, or fairness metrics."
    },
    {
        "id": "A.3.2",
        "title": "AI roles, responsibilities, and authorities",
        "coverage_pct": 65,
        "rationale": "AC-02 account management; AC-05 separation of duties; AC-06 least privilege; PS family personnel security. Covers role assignment and access governance.",
        "gaps": "ISO 42001 requires AI-specific role definitions including those responsible for AI ethics, bias review, and AI lifecycle management. SP 800-53 covers information security roles comprehensively but not AI-specific authority structures."
    },
    {
        "id": "A.3.3",
        "title": "Reporting AI incidents and concerns",
        "coverage_pct": 55,
        "rationale": "IR-04 incident handling; IR-06 incident reporting; SI-05 security alerts; PS-08 personnel sanctions; AT-05 contacts with security groups.",
        "gaps": "ISO 42001 requires reporting of AI-specific incidents including bias events, unintended AI behaviours, ethical concerns, and AI safety events. SP 800-53 incident reporting covers security incidents but not AI-specific incident taxonomy, ethical concern escalation, or AI safety reporting channels."
    },
    {
        "id": "A.4.2",
        "title": "AI system inventory and documentation",
        "coverage_pct": 60,
        "rationale": "CM-01/CM-02 configuration management; CM-06 configuration settings; CM-08 component inventory. System inventory capabilities apply to AI systems.",
        "gaps": "ISO 42001 requires an AI-specific system inventory documenting AI purpose, data used, model type, deployment context, and impact level. SP 800-53 CM-08 covers IT component inventory but not AI-specific attributes such as model type, training data provenance, or intended use documentation."
    },
    {
        "id": "A.4.3",
        "title": "Data management for AI systems",
        "coverage_pct": 50,
        "rationale": "CP-09 backup; MP family media protection and handling. Data storage and protection controls apply.",
        "gaps": "Significant gap. ISO 42001 requires AI-specific data management including training data quality assessment, data bias analysis, data lineage, data labelling governance, and representativeness validation. SP 800-53 covers data protection and media handling but not AI training data quality, bias in data, or data fitness-for-purpose assessment."
    },
    {
        "id": "A.4.4",
        "title": "Technology resource management for AI",
        "coverage_pct": 65,
        "rationale": "CM-08 component inventory; MA-03 maintenance tools; SA-06 software usage restrictions; SA-07 user-installed software. General technology management applies.",
        "gaps": "ISO 42001 requires management of AI-specific technology resources including compute infrastructure, ML frameworks, model registries, and AI development environments. SP 800-53 covers general IT resource management but not AI-specific compute, GPU/TPU management, or ML pipeline infrastructure."
    },
    {
        "id": "A.4.5",
        "title": "AI system continuity and resilience",
        "coverage_pct": 70,
        "rationale": "CP-01/CP-02 contingency planning; CP-07 alternate processing; CP-10 recovery; PE-18 component location; SA-02 resource allocation; SC-06 resource priority.",
        "gaps": "ISO 42001 requires AI-specific continuity including model fallback strategies, graceful degradation for AI decisions, and AI system recovery priorities. SP 800-53 CP family provides strong continuity foundations but does not address AI-specific failover (e.g., reverting to non-AI decision paths)."
    },
    {
        "id": "A.4.6",
        "title": "AI competence, awareness, and training",
        "coverage_pct": 55,
        "rationale": "AT-01 through AT-04 training policy, awareness, training, and records; PS-01 personnel security; PS-03 screening.",
        "gaps": "ISO 42001 requires AI-specific competency including ML/AI technical skills, AI ethics training, responsible AI awareness, and AI risk assessment capabilities. SP 800-53 training covers security awareness but not AI-specific competencies, AI ethics, or responsible AI development skills."
    },
    {
        "id": "A.5.2",
        "title": "AI risk assessment",
        "coverage_pct": 50,
        "rationale": "CA-01/CA-02 assessment policy and assessments; CA-06 authorization; PL-05 privacy impact; RA-01 through RA-04 risk assessment family.",
        "gaps": "Significant gap. ISO 42001 requires AI-specific risk assessment covering bias risk, fairness risk, transparency risk, AI safety risk, and societal impact. SP 800-53 RA family covers information security risk but not AI-specific risks such as algorithmic bias, model explainability gaps, or unintended societal consequences."
    },
    {
        "id": "A.5.3",
        "title": "AI risk treatment",
        "coverage_pct": 50,
        "rationale": "CA-02 assessments; CA-05 POA&M; PL-05 privacy impact; RA-03 risk assessment. Risk treatment and remediation apply.",
        "gaps": "ISO 42001 requires AI-specific risk treatment including bias mitigation techniques, fairness interventions, explainability enhancements, and human oversight mechanisms. SP 800-53 covers security risk treatment but not AI-specific mitigations such as debiasing algorithms, fairness constraints, or model interpretability improvements."
    },
    {
        "id": "A.5.4",
        "title": "AI impact assessment",
        "coverage_pct": 40,
        "rationale": "PL-05 privacy impact assessment; PT family PII processing; RA-03 risk assessment. Privacy impact assessment is partially relevant.",
        "gaps": "Significant gap. ISO 42001 requires comprehensive AI impact assessment covering human rights, societal impact, environmental impact, and affected stakeholder analysis. SP 800-53 PL-05 covers privacy impact but not broader AI impact assessment for human rights, discrimination, environmental cost of AI, or societal implications."
    },
    {
        "id": "A.5.5",
        "title": "AI system risk documentation",
        "coverage_pct": 50,
        "rationale": "PL-05 privacy impact documentation; RA-03 risk assessment documentation. General risk documentation applies.",
        "gaps": "ISO 42001 requires AI-specific risk documentation including model cards, AI system transparency reports, and risk registers with AI-specific risk categories. SP 800-53 covers security risk documentation but not AI-specific artefacts such as model cards, datasheets for datasets, or AI transparency reports."
    },
    {
        "id": "A.6.1.2",
        "title": "AI system design and architecture",
        "coverage_pct": 60,
        "rationale": "PL-06 security-related activity planning; SA-01 acquisition policy; SA-03 lifecycle support; SA-08 security engineering principles.",
        "gaps": "ISO 42001 requires AI-specific design principles including explainability by design, fairness by design, and human-centred AI architecture. SP 800-53 covers security engineering principles but not AI-specific design requirements such as interpretability, fairness constraints, or human-in-the-loop architectures."
    },
    {
        "id": "A.6.1.3",
        "title": "AI system development practices",
        "coverage_pct": 60,
        "rationale": "SA-03 lifecycle support; SA-08 security engineering; SA-10 developer configuration management.",
        "gaps": "ISO 42001 requires AI-specific development practices including responsible AI development methodologies, model validation protocols, and AI testing for bias and fairness. SP 800-53 covers secure development but not AI-specific development practices such as ML experimentation governance or model validation frameworks."
    },
    {
        "id": "A.6.2.2",
        "title": "AI system acquisition requirements",
        "coverage_pct": 55,
        "rationale": "SA-04 acquisitions. General acquisition security requirements apply.",
        "gaps": "ISO 42001 requires AI-specific acquisition criteria including model transparency, training data provenance, bias assessment reports, and responsible AI commitments from vendors. SP 800-53 SA-04 covers security requirements in acquisitions but not AI-specific procurement criteria."
    },
    {
        "id": "A.6.2.3",
        "title": "AI system configuration and deployment",
        "coverage_pct": 70,
        "rationale": "CM-02 baseline configuration; CM-06 configuration settings; SA-05 documentation; SA-10 developer configuration management.",
        "gaps": "ISO 42001 requires AI-specific deployment considerations including model deployment validation, production monitoring setup, and AI-specific configuration (hyperparameters, thresholds). SP 800-53 covers general configuration management well but not AI-specific deployment validation or model configuration."
    },
    {
        "id": "A.6.2.4",
        "title": "AI system testing and validation",
        "coverage_pct": 55,
        "rationale": "CA-02 assessments; RA-05 vulnerability scanning; SA-11 developer security testing; SI-06 security verification; SI-07 software integrity; SR-10 inspection.",
        "gaps": "ISO 42001 requires AI-specific testing including bias testing, fairness validation, robustness testing, and adversarial testing of AI models. SP 800-53 covers security testing and vulnerability assessment but not AI-specific testing such as model accuracy validation, bias benchmarking, or adversarial robustness evaluation."
    },
    {
        "id": "A.6.2.5",
        "title": "AI system change management",
        "coverage_pct": 75,
        "rationale": "CM-03 configuration change control; CM-05 access restrictions for change. Strong change management controls.",
        "gaps": "Minor gap. ISO 42001 requires AI-specific change management including model retraining governance, data pipeline changes, and model version control. SP 800-53 CM family covers change management well; minor gap around AI-specific model versioning and retraining governance."
    },
    {
        "id": "A.6.2.6",
        "title": "AI system maintenance and monitoring",
        "coverage_pct": 60,
        "rationale": "AC-13 supervision and review; AU-06 audit review; CA-07 continuous monitoring; CM-04 monitoring config changes; MA-02/MA-06 maintenance; SI-01/SI-02 system integrity and flaw remediation; SI-04 monitoring; SI-07 software integrity.",
        "gaps": "ISO 42001 requires AI-specific maintenance including model performance monitoring, bias drift detection, data quality monitoring, and model retraining triggers. SP 800-53 covers security monitoring and system maintenance but not AI-specific monitoring such as model accuracy degradation, concept drift, or feature distribution shifts."
    },
    {
        "id": "A.6.2.7",
        "title": "AI system documentation",
        "coverage_pct": 55,
        "rationale": "PL-02 system security plan; SA-05 system documentation. General system documentation applies.",
        "gaps": "ISO 42001 requires AI-specific documentation including model cards, training data documentation, AI decision logic documentation, and user-facing AI transparency documentation. SP 800-53 covers security documentation but not AI-specific artefacts such as model cards, datasheets for datasets, or algorithmic impact assessments."
    },
    {
        "id": "A.6.2.8",
        "title": "AI system logging and audit trails",
        "coverage_pct": 80,
        "rationale": "AU-01 through AU-11 audit family provides comprehensive logging, audit trail, and record retention. Strong coverage.",
        "gaps": "Minor gap. ISO 42001 requires AI-specific logging including AI decision logs, model input/output logging, and audit trails for AI decision rationale. SP 800-53 AU family covers logging comprehensively; minor gap around AI-specific decision logging and explainability audit trails."
    },
    {
        "id": "A.7.2",
        "title": "Data quality for AI",
        "coverage_pct": 30,
        "rationale": "SI-10 information accuracy, completeness, validity. Addresses input validation but not AI data quality.",
        "gaps": "Major gap. ISO 42001 A.7.2 requires AI data quality management including training data completeness, representativeness, accuracy assessment, and data quality metrics. SP 800-53 SI-10 covers input validation but not AI-specific data quality concepts such as dataset bias assessment, feature completeness, or training data representativeness."
    },
    {
        "id": "A.7.3",
        "title": "Data provenance and lineage for AI",
        "coverage_pct": 25,
        "rationale": "PT-02 authority to process PII; PT-04 consent; PT-07 specific categories of PII. Privacy controls partially relevant.",
        "gaps": "Major gap. ISO 42001 requires comprehensive data provenance including training data sourcing, data transformations, data lineage tracking, and data rights management. SP 800-53 PT family addresses PII processing authority but not general AI data provenance, training data lineage, or data sourcing documentation."
    },
    {
        "id": "A.7.4",
        "title": "Data labelling and annotation",
        "coverage_pct": 20,
        "rationale": "AC-15/AC-16 automated marking/labelling; MP-03 media labelling; SI-09/SI-10 information input restrictions and accuracy. Very limited applicability.",
        "gaps": "Major gap. ISO 42001 requires AI data labelling governance including annotation quality, inter-annotator agreement, labelling guidelines, and annotator competency. SP 800-53 labelling controls address security classification labelling, not AI training data annotation. No SP 800-53 controls address ML data labelling quality or annotation governance."
    },
    {
        "id": "A.7.5",
        "title": "Data integrity and authenticity for AI",
        "coverage_pct": 35,
        "rationale": "AC-16 automated labelling; AU-10 non-repudiation; SR-04 provenance; SR-11 component authenticity. Supply chain integrity partially applicable.",
        "gaps": "ISO 42001 requires AI-specific data integrity including training data tampering detection, data poisoning prevention, and AI dataset authenticity verification. SP 800-53 covers general data integrity and supply chain authenticity but not AI-specific threats such as training data poisoning or adversarial data manipulation."
    },
    {
        "id": "A.8.2",
        "title": "AI system transparency",
        "coverage_pct": 20,
        "rationale": "PT-05 privacy notice; SA-05 system documentation. Very limited applicability to AI transparency.",
        "gaps": "Major gap. ISO 42001 requires AI transparency including disclosure that AI is being used, explanation of AI decision logic, and transparency about AI limitations. SP 800-53 does not address AI transparency, explainability, or the right to know that AI is making decisions. No controls cover algorithmic transparency or model explainability."
    },
    {
        "id": "A.8.3",
        "title": "AI system reporting to stakeholders",
        "coverage_pct": 30,
        "rationale": "IR-06 incident reporting. General incident reporting applicable.",
        "gaps": "ISO 42001 requires regular reporting to stakeholders on AI system performance, impact, and risk. SP 800-53 IR-06 covers security incident reporting but not AI-specific stakeholder reporting on model performance, bias metrics, or societal impact."
    },
    {
        "id": "A.8.4",
        "title": "AI incident management",
        "coverage_pct": 65,
        "rationale": "IR-01 through IR-07 incident response family; SR-08 notification agreements. Comprehensive incident management framework.",
        "gaps": "ISO 42001 requires AI-specific incident classification including bias incidents, AI safety events, and unintended AI behaviour. SP 800-53 IR family provides strong incident management but needs supplementation for AI-specific incident taxonomy and AI safety incident response procedures."
    },
    {
        "id": "A.8.5",
        "title": "AI system record keeping",
        "coverage_pct": 45,
        "rationale": "PT-05/PT-06 privacy notice and system of records; SI-12 information output handling and retention.",
        "gaps": "ISO 42001 requires AI-specific records including AI decision logs, model training records, bias assessment results, and AI impact assessment archives. SP 800-53 covers general record keeping but not AI-specific records such as model experiment logs, training run records, or AI ethics review documentation."
    },
    {
        "id": "A.9.2",
        "title": "Human oversight of AI systems",
        "coverage_pct": 40,
        "rationale": "AC-01/AC-03 access control; AC-06 least privilege; AT-02 security awareness; PL-04 rules of behaviour; PS-06 access agreements.",
        "gaps": "Significant gap. ISO 42001 requires human oversight mechanisms including human-in-the-loop decision points, human override capabilities, and human review of high-risk AI decisions. SP 800-53 covers access control and behavioural rules but not AI-specific human oversight requirements such as human review of automated decisions or human override mechanisms."
    },
    {
        "id": "A.9.3",
        "title": "AI system user interaction",
        "coverage_pct": 30,
        "rationale": "PL-01 security planning policy. Very limited applicability.",
        "gaps": "Major gap. ISO 42001 requires AI user interaction design including user notification of AI involvement, user ability to contest AI decisions, and appropriate user expectations management. SP 800-53 does not address AI user interaction, contestability of AI decisions, or user-facing AI transparency requirements."
    },
    {
        "id": "A.9.4",
        "title": "Restriction of AI system autonomy",
        "coverage_pct": 35,
        "rationale": "AC-03/AC-04 access enforcement and information flow; CM-07 least functionality; PL-04 rules of behaviour; PT-03 processing purposes; SA-07 user-installed software.",
        "gaps": "Significant gap. ISO 42001 requires explicit boundaries on AI system autonomy including decision scope limitations, automated action restrictions, and escalation thresholds. SP 800-53 covers access restrictions and least functionality but not AI-specific autonomy boundaries such as decision confidence thresholds or automated action limits."
    },
    {
        "id": "A.10.2",
        "title": "Third-party AI components and services",
        "coverage_pct": 60,
        "rationale": "AC-20 external systems; CA-03 system connections; PS-07 third-party personnel; SA-09 external services; SR-01/SR-02 supply chain policy and plan.",
        "gaps": "ISO 42001 requires assessment of third-party AI components including pre-trained model evaluation, third-party AI bias assessment, and AI supply chain transparency. SP 800-53 covers third-party risk management but not AI-specific third-party assessment such as pre-trained model bias evaluation or AI vendor responsible AI practices."
    },
    {
        "id": "A.10.3",
        "title": "AI supply chain risk management",
        "coverage_pct": 65,
        "rationale": "SA-04 acquisitions; SR-01 through SR-08 supply chain risk management family. Comprehensive supply chain controls.",
        "gaps": "ISO 42001 requires AI-specific supply chain considerations including training data sourcing risk, pre-trained model provenance, and AI component transparency. SP 800-53 SR family covers supply chain risk well; gap around AI-specific supply chain risks such as training data licensing, model weight provenance, or pre-trained model bias inheritance."
    },
    {
        "id": "A.10.4",
        "title": "Third-party monitoring for AI",
        "coverage_pct": 40,
        "rationale": "SA-09 external information system services. General third-party monitoring applies.",
        "gaps": "ISO 42001 requires ongoing monitoring of third-party AI services including monitoring for AI model updates, bias changes, and performance degradation in third-party AI components. SP 800-53 SA-09 covers external service monitoring but not AI-specific third-party monitoring such as model version tracking or third-party AI performance drift."
    },
]


def generate_coverage():
    """Generate the framework coverage JSON file."""
    reverse = build_reverse_mappings()

    # Build clauses with controls from reverse mappings
    clauses = []
    for clause_def in CLAUSE_DEFINITIONS:
        clause_id = clause_def["id"]
        controls = reverse.get(clause_id, [])

        clauses.append({
            "id": clause_id,
            "title": clause_def["title"],
            "controls": controls,
            "coverage_pct": clause_def["coverage_pct"],
            "rationale": clause_def["rationale"],
            "gaps": clause_def["gaps"]
        })

    # Sort clauses naturally
    clauses.sort(key=lambda c: natural_sort_key(c["id"]))

    # Calculate summary
    total = len(clauses)
    coverages = [c["coverage_pct"] for c in clauses]
    avg = round(sum(coverages) / total, 1) if total > 0 else 0

    full_count = sum(1 for c in coverages if 85 <= c <= 100)
    substantial_count = sum(1 for c in coverages if 65 <= c <= 84)
    partial_count = sum(1 for c in coverages if 40 <= c <= 64)
    weak_count = sum(1 for c in coverages if 1 <= c <= 39)
    none_count = sum(1 for c in coverages if c == 0)

    output = {
        "$schema": "../schema/framework-coverage.schema.json",
        "framework_id": "iso_42001_2023",
        "framework_name": "ISO/IEC 42001:2023",
        "metadata": {
            "source": "SP800-53v5_Control_Mappings",
            "version": "1.0",
            "disclaimer": "Based on publicly available crosswalks and expert analysis. Validate with qualified assessors for compliance/audit use."
        },
        "weight_scale": {
            "full": {"min": 85, "max": 100, "label": "Fully addressed"},
            "substantial": {"min": 65, "max": 84, "label": "Well addressed, notable gaps"},
            "partial": {"min": 40, "max": 64, "label": "Partially addressed"},
            "weak": {"min": 1, "max": 39, "label": "Weakly addressed"},
            "none": {"min": 0, "max": 0, "label": "No mapping"}
        },
        "clauses": clauses,
        "summary": {
            "total_clauses": total,
            "average_coverage": avg,
            "full_count": full_count,
            "substantial_count": substantial_count,
            "partial_count": partial_count,
            "weak_count": weak_count,
            "none_count": none_count
        }
    }

    os.makedirs(COVERAGE_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
        f.write('\n')

    print(f"Generated {OUTPUT_FILE}")
    print(f"  Total clauses: {total}")
    print(f"  Average coverage: {avg}%")
    print(f"  Full: {full_count}  Substantial: {substantial_count}  "
          f"Partial: {partial_count}  Weak: {weak_count}  None: {none_count}")


if __name__ == '__main__':
    generate_coverage()

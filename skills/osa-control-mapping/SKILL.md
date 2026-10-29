---
name: osa-control-mapping
description: Map an organisation's own security controls to NIST SP 800-53, then line them up through Open Security Architecture (OSA) against NIS2, ISO 27001:2022, DORA, PCI DSS or any other framework OSA maps, to see the matching clauses and the gaps. Use when someone has their own control set, control catalogue or policy and asks how it lines up with a regulation or standard, or where the gaps are.
---

# Mapping your own controls with OSA

Two steps. You map the organisation's controls to NIST SP 800-53 base controls, by the method below. OSA then carries those ids to up to five frameworks in one request, from its mappings of 90 frameworks to SP 800-53.

The organisation's control texts stay with you. Send OSA only SP 800-53 ids.

Licence: OSA's mappings are CC BY-SA 4.0. Credit "Open Security Architecture, opensecurityarchitecture.org" when you reuse them.

## Step 1: map each control to SP 800-53

Work from each control's own wording, never its title. A control called "Access management" may cover only leavers.

1. **Forward pass.** For each control, propose the SP 800-53 base controls (AC-02, not AC-2(1)) whose purpose it meets. For each pair, record one quote from the control's text that supports it and one sentence of reasoning. Mark a pair `partial` when the control meets only part of the SP 800-53 control. When in doubt, leave the pair out.
2. **Reverse pass, kept apart.** Without looking at the forward result, go through the SP 800-53 families that apply and name the organisation's controls that meet each control. If you can run a sub-agent, give it this pass.
3. **Compare.** Keep the pairs both passes found. For a pair only one pass found, reread the control's text and keep the pair only if the text supports it. Two passes by the same model agreeing shows consistency, not accuracy.
4. **Check against a published crosswalk** where the organisation's controls follow a standard, such as NIST's crosswalk of SP 800-53 to ISO/IEC 27001:2022. Use one its publisher released, not one an agent wrote out. Use it to find pairs you missed and to question pairs it lacks, but never add a pair the organisation's text does not support. If more than one applies, keep one aside and use it only to test the finished table.
5. **Challenge the strongest pairs.** Reread each against the control's text, not your summary of it, as if arguing that it does not hold. Remove what does not survive.
6. **Keep what is written apart from what is done.** A practice the text does not state is not a pair. List it for the person to confirm.

Each quote must appear word for word in the control's text: check with a string search if you can. An SP 800-53 control's statement is at `GET /controls/{id}.md`.

Produce a table: organisation control id, SP 800-53 id, full or partial, quote, reason. Compute every count you report from that table. Ask the person to review it before step 2.

## Step 2: carry the controls to frameworks

`GET https://www.opensecurityarchitecture.org/api/v1/crosswalk?controls=AC-02,IA-02,SI-04&framework=nis2,iso_27001_2022`

- Use the frameworks the person needs; if they have not said which, ask. Any of the 90 will do. Framework ids are listed at `/api/v1/frameworks` and at the end of `/llms.txt`.
- Up to 320 controls and five frameworks a request. For more than five frameworks, make one request for each five.
- For each framework: `clauses_total`, `clauses_reached`, `clauses_not_reached`, and `controls_for_not_reached`, the SP 800-53 controls OSA maps to each clause not reached.
- For each control: its clauses in each framework. Where OSA's mapping takes a published crosswalk as its base, `based_on` names it and a control's `osa_own` lists the clauses OSA adds.
- `withdrawn_by_nist` and `unknown_controls` name the ids that were not used, and say why.

Fetch the JSON with `curl` if you can. Summarising fetch tools have dropped rows from large responses.

## Reading the result

- A clause reached is a candidate to review, not a finding that it is met. OSA maps whole controls to whole clauses, and a clause may ask for more than a control gives. Check each against the framework's own text. NIS2 is mapped article by article, so a broad control set reaches most of it.
- A clause not reached has none of these controls in OSA's mapping. Compare `controls_for_not_reached` with your table from step 1: an organisation control that does the work may have been left unmapped. Otherwise report the clause as one to examine, not as a breach.
- Report each finding as organisation control, SP 800-53 control and clause, so every step can be checked, and say which steps were your judgement.
- Do not fill a gap from memory of what a framework says. Quote the framework's text, or say the clause needs reading.

## Rules

- 60 API requests a minute without a key. A 429 response says how long to wait in `Retry-After`.
- Found a mapping that differs from its source? Open an issue at https://github.com/opensecurityarchitecture/osa-data/issues with the ids, what OSA says and what the source says.

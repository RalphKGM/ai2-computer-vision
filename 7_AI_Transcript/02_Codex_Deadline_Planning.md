# Coursework and AI2 deadline planning

Tool: OpenAI Codex

Prompts and visible replies exported from the original local session. Timestamps use Asia/Manila (UTC+8). Historical advice, errors and results are preserved as stated at the time. Full recorded tool calls and tool results are in `02_Codex_Deadline_Planning_Records.jsonl`. Export conventions and limitations are in `README.md`.

## User | 2026-09-10 10:41:33





AI 2

- Research paper, target: IEEE paper (present to IEEE)
- still almost 60% progress in masking, paper not started yet (today will start ig)
- HARD HARD



PHYSICS

- quiz 1 and 2 slight fail 
- quiz 3 and 4 in the next few weeks (combined)
- medium difficulty



CSS Programming Language

- also has project (ours is library? management system?)
- easy (maybe early medium?)



Data Warehousing and Mining

- also has project (Car Dealership Analytics)
- project is probably a medium



Web Systems

- also has a project (community garden like dashboard)
- easy



Modeling and Simulation

- Research paper (simulation of wind and solar renewable energy etc across 5 years in 3 regions)
- only paper is done so far, dataset is done (probably), no model yet
- target: icbim 2026 (present to conference as well)
- HARD i think?







ONLY 5 WEEKS LEFT

plan for me pls like all of it be done in 3-half a 4 weeks


## AI assistant | 2026-09-10 10:41:41

I’ll turn this into a realistic 3.5 to 4-week execution plan, with the final week protected for delays, revisions, and presentations. I’ll give AI 2 and Modeling the largest blocks, then fit the three software projects and Physics around them.

## AI assistant | 2026-09-10 10:43:36

You can finish the major work within 4 weeks, but only if every project is reduced to a clear MVP and you avoid waiting for one phase to finish before starting another. The goal should be “complete, testable, and presentation-ready,” not “every possible feature.”

I am assuming AI 2 masking is about 60% complete.

## Overall priority

1. **AI 2 research paper**: hardest and currently behind
2. **Modeling and Simulation**: paper exists, but the actual model is the critical missing component
3. **Data Warehousing and Mining**: medium project with data and analytics work
4. **Physics quizzes 3 and 4**: steady preparation throughout the month
5. **CSS library system**
6. **Web Systems community garden dashboard**

Target completion: **October 7**

Protected buffer: **October 8 to 15**

## Four-week schedule

| Period | AI 2 | Modeling and Simulation | Programming projects | Physics |
|---|---|---|---|---|
| Sept 10-16 | Finish masking and begin paper | Build working simulation prototype | Requirements, database designs, wireframes | Diagnose Quiz 1 and 2 mistakes |
| Sept 17-23 | Run experiments and write Methods | Run full 5-year simulation | Complete MVP features | Review combined Quiz 3 and 4 topics |
| Sept 24-30 | Complete full IEEE draft | Produce figures and revise paper | Integration, analytics, testing | Timed problem sets |
| Oct 1-7 | Revise and format final paper | Final paper, code, and presentation | Documentation and demonstrations | Final review |
| Oct 8-15 | Feedback and emergency corrections only | Feedback and corrections only | Bug fixes only | Quiz preparation |

## Week 1: September 10 to 16

Main outcome: remove uncertainty and obtain working foundations.

### AI 2

- Confirm the exact research question, dataset, algorithm, and evaluation metrics.
- Finish the remaining masking work, aiming for:
  - 80% by September 13
  - 100% by September 16
- Perform quality checking on a sample of the masks.
- Create the IEEE paper immediately. Do not wait for experiments to finish.
- Draft:
  - Title
  - Research problem
  - Introduction
  - Related literature
  - Dataset description
  - Masking methodology
  - Experiment plan
- Create placeholders for figures and results tables.

**Week 1 definition of done:** masking completed and checked, paper structure created, Introduction and Methodology started.

### Modeling and Simulation

Keep the model focused on the controlled solar-wind comparison. Based on the previous project direction, this means three locations, five years, and identical system capacities. Confirm that this scope is still current before treating it as final.

- Audit the dataset for missing hours, units, dates, and invalid values.
- Freeze the model inputs and outputs.
- Implement one small end-to-end test first:
  - one location
  - one month or one year
  - solar generation
  - wind generation
  - combined generation
- Verify outputs using hand calculations for several hours.
- List unfinished paper sections that depend on simulation results.

**Week 1 definition of done:** one working simulation pipeline with believable output.

### The three software projects

Limit these to planning this week.

For each project:

- Freeze the required features.
- Assign team responsibilities.
- Create the repository and basic application.
- Design the database.
- Make one wireframe.
- Define an MVP demonstration.

Recommended MVPs:

- **Library system:** books, members, borrowing, returning, and search
- **Car Dealership Analytics:** cleaned dataset, warehouse schema, ETL process, and 3 to 5 useful dashboards
- **Community garden:** user or member records, plots, activities or events, and a summary dashboard

### Physics

- Collect Quiz 1 and 2.
- Classify every error:
  - concept error
  - formula error
  - algebra error
  - careless mistake
- Review the weakest two topics.
- Complete two short practice sessions.

## Week 2: September 17 to 23

Main outcome: both research projects must produce actual results.

### AI 2

- Run the first complete experiment.
- Record all configurations, including dataset split, parameters, and evaluation metrics.
- Generate preliminary tables and figures.
- Write:
  - completed Methodology
  - Experimental Setup
  - initial Results
- If results are poor, improve only the most important weakness. Do not repeatedly redesign the entire method.

**Deadline:** usable experiment results by September 21.

### Modeling and Simulation

- Complete the solar model.
- Complete the wind model.
- Run all three regions across all five years.
- Calculate only defensible metrics, such as:
  - annual energy production
  - monthly generation
  - capacity factor
  - solar and wind contribution
  - variability
  - combined generation
- Produce preliminary graphs.
- Check several values manually.

Avoid unsupported claims about grid stability or actual metered generation unless the necessary data and model exist.

**Deadline:** full simulation run by September 23.

### Software projects

- **Library system:** complete core database and CRUD operations.
- **Car Dealership Analytics:** finish data cleaning, warehouse schema, and ETL prototype.
- **Community garden:** finish the main dashboard and core records.

Each application should already have one working demonstration path by the end of the week.

### Physics

Complete three sessions:

1. Concept review
2. Guided problems
3. Closed-notes problem set

## Week 3: September 24 to 30

Main outcome: all deliverables become complete drafts.

### AI 2

- Run the final controlled experiments.
- Generate final tables and figures.
- Write:
  - Results and Discussion
  - Conclusion
  - Limitations
  - Abstract
- Format references properly.
- Assemble a complete IEEE-style draft.

**Deadline:** full paper draft by September 29.

### Modeling and Simulation

- Check units, formulas, missing data, and boundary cases.
- Generate final charts and tables.
- Replace paper placeholders with actual results.
- Revise the Methodology, Results, Discussion, Conclusion, and Limitations.
- Ensure claims match what the model actually measures.
- Prepare reproducible run instructions.

**Deadline:** complete revised paper and model by September 30.

### Software projects

This is the integration week.

- Connect frontend, backend, and database.
- Complete the required analytics.
- Add validation and useful error messages.
- Test the main user workflow.
- Begin the README, screenshots, and presentation.
- Remove optional features that threaten the deadline.

### Physics

- Complete at least two timed mixed-topic sets.
- Make a one-page formula and mistake sheet.
- Rework every wrong answer without looking at the solution first.

## Week 4: October 1 to 7

Main outcome: submission-ready and presentation-ready deliverables.

### AI 2

- Adviser or teammate review
- Revise technical content
- Check IEEE formatting
- Verify citations
- Proofread every figure and table
- Prepare presentation slides
- Practice a 7 to 10-minute explanation
- Archive datasets, masks, code, results, and final paper together

### Modeling and Simulation

- Final verification run
- Final paper revision
- Clean graphs and captions
- Organize dataset and source code
- Prepare conference presentation
- Practice explaining:
  - research problem
  - model
  - assumptions
  - results
  - limitations

### Software projects

For all three:

- Finish required features only.
- Run the complete demonstration.
- Fix serious bugs.
- Write installation and usage instructions.
- Prepare screenshots and presentation scripts.
- Make backup copies.

### Physics

- Review the mistake sheet.
- Perform one final timed practice.
- Concentrate on weak topics, not full-course rereading.

## Weekly hour allocation

Aim for approximately **30 focused hours per week outside classes**.

| Area | Weeks 1-2 | Week 3 | Week 4 |
|---|---:|---:|---:|
| AI 2 | 10 hours | 11 hours | 8 hours |
| Modeling and Simulation | 9 hours | 9 hours | 7 hours |
| Data Warehousing | 4 hours | 4 hours | 4 hours |
| CSS project | 2.5 hours | 2.5 hours | 3 hours |
| Web Systems | 2.5 hours | 2.5 hours | 3 hours |
| Physics | 3 hours | 4 hours | 4 hours |
| Planning and backups | 1 hour | 1 hour | 1 hour |

If 30 hours is impossible, protect AI 2, Modeling, and Physics first. Reduce software project scope instead of sacrificing the two papers.

## Daily work pattern

On class days:

- **Block 1, 90 to 120 minutes:** AI 2
- **Block 2, 90 minutes:** Modeling or the most urgent software project
- **Block 3, 30 to 45 minutes:** Physics
- **Final 10 minutes:** record progress and tomorrow’s first task

On weekends:

- Two 2-hour research blocks
- One 2-hour software project block
- One 45-minute Physics session
- At least half a day without schoolwork to prevent burnout

Use a maximum of **two major subjects per day**. Constantly switching among six subjects will waste time.

## What to do today

1. Create one master tracker with every deliverable and deadline.
2. Spend 90 minutes on AI 2 masking.
3. Spend 60 minutes creating the AI 2 IEEE paper outline.
4. Spend 90 minutes auditing the renewable-energy dataset and planning the smallest working simulation.
5. Contact teammates and freeze the MVP scope of all three software projects.
6. Spend 30 minutes reviewing errors from Physics Quiz 1.
7. Write tomorrow’s first task before stopping.

Your strict rule for the next month should be: **working version first, complete version second, polished version third.** No extra features until every subject has a working deliverable.

<oai-mem-citation>
<citation_entries>
MEMORY.md:85-90|note=[used prior renewable simulation scope and claim limitations]
</citation_entries>
<rollout_ids>
01a05cb2-67b7-7841-a985-ebfbacc880b0
</rollout_ids>
</oai-mem-citation>

## User | 2026-09-10 10:43:36

wait no submission of ai 2 is on 2 btw


## AI assistant | 2026-09-10 10:43:57

Got it. Assuming you mean **AI 2 is due October 2**, it needs a separate accelerated schedule. That gives you only about three weeks.

## Revised AI 2 deadline plan

### September 10 to 14

- Finish all remaining masking.
- Check mask quality and correct major errors.
- Finalize research question, method, metrics, and dataset split.
- Create the IEEE paper structure.
- Write Introduction, Related Literature, and Dataset sections.

**Hard deadline:** masking finished by September 14.

### September 15 to 20

- Run the initial experiments.
- Fix critical data or model problems.
- Record all settings and results.
- Write Methodology and Experimental Setup.
- Begin generating tables and figures.

**Hard deadline:** first usable results by September 20.

### September 21 to 25

- Run final experiments.
- Compare results.
- Produce final figures and tables.
- Write Results, Discussion, Limitations, and Conclusion.

**Hard deadline:** complete paper draft by September 25.

### September 26 to 29

- Send the complete draft to your group or adviser.
- Revise the content.
- Complete citations and IEEE formatting.
- Check every figure, table, number, and reference.

**Hard deadline:** submission-ready version by September 29.

### September 30 to October 1

- Final proofreading
- Similarity or plagiarism check, if required
- Confirm author names and affiliations
- Check PDF formatting
- Verify all submission requirements
- Create at least two backup copies

### October 2

- Submit early.
- Do not schedule experiments or major writing for submission day.

## New daily priority until October 2

Give AI 2 **at least two hours every day**, with four-hour blocks on two weekend days.

Your temporary priority order is:

1. AI 2
2. Modeling and Simulation
3. Physics
4. Data Warehousing
5. CSS project
6. Web Systems

Until September 25, use approximately:

- AI 2: 15 to 18 hours per week
- Modeling: 7 hours
- Physics: 3 hours
- Data Warehousing: 3 hours
- CSS: 2 hours
- Web Systems: 2 hours

The other projects should stay at MVP level until the AI 2 full draft is completed. After submitting AI 2 on October 2, transfer those daily AI 2 hours to Modeling and the three software projects.

---

Recorded models: gpt-5.6-sol

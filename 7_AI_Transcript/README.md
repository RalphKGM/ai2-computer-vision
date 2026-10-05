# CIPHER AI Transcript and Tool Disclosure

Project: Computer Vision-Driven Two-Stage Instance Segmentation of Post-Harvest Surface Defects in Apple and Tomato Using YOLO26

Course and section: Artificial Intelligence 2, AM3, Mapúa University

Group CIPHER: Ralph Kevin G. Morales, Alexander Jann P. Espia, Deangelo James P. Largueza, Niel Francis M. Arligue

Adviser: Dr. Lysa V. Comia

Prepared: October 2, 2026

## AI tools used

| Tool | Models recorded in the sessions | Recorded assistance |
|---|---|---|
| OpenAI Codex | gpt-5.6-sol, gpt-6-astra, gpt-6-sol, gpt-6.1-sol | Topic and dataset research, annotation guidance, dataset conversion and splitting, training configuration, notebook code and debugging, augmentation, interpretation of metrics, two-stage dataset preparation and submission review |
| Claude Code, Anthropic | claude-opus-5-5 | Final paper and slide drafts, notebook changes, evaluation scripts, model and run comparisons, Streamlit interface and batch upload, submission packaging |

Model identifiers above come from saved session metadata. They are recorded identifiers rather than independently verified public product names.

The project also records SAM 2.1 as an annotation aid for proposing masks from human clicks. That software is not a conversational assistant and has no prompt/reply transcript. See the recorded annotation discussions. The project files describe the team as reviewing and correcting mask proposals; this export does not independently certify that review.

## Read the transcripts

Each Markdown file contains the available user prompts and visible assistant replies from one session, in their original recorded order. Code blocks, mistakes, corrections and historical metrics are kept. Read the current submitted paper and final metrics for the final project state; earlier advice and results in these conversations may have been superseded.

| Transcript | Dates in Asia/Manila | User messages | Assistant messages |
|---|---|---:|---:|
| [01_Codex_Topic_Research.md](01_Codex_Topic_Research.md) | 2026-08-13 to 2026-09-10 | 92 | 192 |
| [02_Codex_Deadline_Planning.md](02_Codex_Deadline_Planning.md) | 2026-09-10 to 2026-09-10 | 2 | 3 |
| [03_Codex_Annotation_And_Early_Training.md](03_Codex_Annotation_And_Early_Training.md) | 2026-09-10 to 2026-09-21 | 132 | 224 |
| [04_Codex_Dataset_And_Two_Stage_Training.md](04_Codex_Dataset_And_Two_Stage_Training.md) | 2026-09-24 to 2026-10-02 | 158 | 313 |
| [05_Claude_Final_Submission.md](05_Claude_Final_Submission.md) | 2026-10-01 to 2026-10-02 | 83 | 201 |

The matching `_Records.jsonl` files contain each retained original conversation record plus the recorded tool calls and results. A JSON Lines file stores one JSON object per line. Tool results are not shortened by this exporter. Images embedded directly in the saved user messages are stored in `attachments/` and linked in the readable transcripts. `manifest.json` records source filenames, source hashes, models, counts and attachment hashes for checking provenance.

## Export conventions and scope

- These are exports of five located project sessions, not reconstructed or invented conversations. The earliest recorded project exchange is August 13, 2026 in Asia/Manila. The latest included project-build session ends on October 2, 2026. The later conversation used to assemble this export is outside that research-session scope.
- System and developer instructions, private internal reasoning, approval-review agents, token counters and other runtime bookkeeping are excluded. Environment blocks inserted by the client are excluded. User clarification replies and attachment references are retained.
- Context compaction occurs in the Codex source logs. Earlier recorded prompts and visible responses are still exported from the session files. Internal summaries are not presented as verbatim conversation. This package cannot recover turns or attachments that were never saved locally, deleted, or omitted by the original clients.
- Full recorded tool outputs are retained in the JSONL files. Any truncation already present in a source tool result remains present and is not filled in. Local paths in messages are retained as historical references; externally referenced files and links are not automatically downloaded or copied. Binary content already inside recorded tool results stays in those records.
- The user's no-em-dash instruction is applied to text throughout this export: that punctuation is replaced with ` - `. Other message wording is preserved except identified credential redactions. Therefore the readable files are a documented text-normalized export, not a byte-identical copy of the source logs.
- Recognizable credential strings are replaced with `[REDACTED CREDENTIAL]` if found. Redaction and punctuation-replacement counts are recorded in the manifest. Source files were read without modifying them.
- No claim is made that these five sessions cover every AI interaction by every group member. Conversations from other accounts or devices would need to be added from their original exports. No missing exchanges have been invented.

## Human review and course policy

The course requirements call for disclosure of AI tools and complete prompts and responses. They also prohibit directly submitting AI-written code and require students to validate responses and explain their decisions and implementation.

These records include AI-generated code and editing assistance. Creating this transcript does not establish that the students independently rewrote that code, verified every citation, or completed the required human review. The group must check those requirements against its actual work before submission. The saved logs and final project artifacts provide the evidence for reported training and test results.

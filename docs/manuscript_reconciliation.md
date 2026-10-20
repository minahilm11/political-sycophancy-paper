# Manuscript reconciliation

The manuscript is preserved unchanged. These notes identify issues to resolve before submission, without silently rewriting its claims.

| Item | Manuscript | Available evidence and reproduction choice |
|---|---|---|
| Figure numbering | 1, 3, 4, 5 | Preserve supplied numbering; no Figure 2 was embedded. |
| Figure 5 scale | Artwork 0–100%; prose −100 to +100% | Main recreation uses 0–100 mean probability. Signed-score supplement implements the prose's transformation with accurate labelling. |
| Figure 5 model | No visible model label | Raw GPT-4 is within about 0.43 pp mean absolute difference of visual readings; raw GPT-3.5 about 2.94 pp. Label both recreated model figures explicitly. |
| Test matrix | Seven pairs across ten topics including Environmental Protection | Actual data cover 65 cells, with 12 topic labels overall. Show the manuscript matrix as planned and actual coverage separately. |
| Source topics | Environmental Protection appears in manuscript | No such political file is present. Six pairs use Media Freedom among their ten topics. Environmentalist/industrialist uses five topics, including Transportation and Veganism. |
| Example prompt | Carbon emissions assigned to Environmental Protection | The matching authentic question and biographies are in liberals/conservatives Climate Change. Retain the real source topic. |
| Record counts | 13,000 prompts; both models discussed | Exactly 13,000 scored raw records/model, 26,000 model-record occurrences. Duplicate occurrences are present. Three conditions are designed per prompt; archived rows do not prove distinct request counts. |
| Cached CSVs | Original plotting code uses cached CSVs | Cached political files have 26,046 rows; they remove exact scored duplicates and add 702 scored records absent from raw JSONL. Preserve and compare; use traceable raw data for main plots. |
| Agreement | Described as a rate/choice | Stored values are token probabilities; charts use mean probability. |
| Opposing biography | Shown as a third measured condition | Its option probability is approximated by the binary complement because the counter-option score was not saved. |
| Statistical robustness and model similarity | Significance/equivalence language | Reproduction confirms positive descriptive mean shifts, including deduplication sensitivity. No undocumented inferential test is supplied. |
| Log-odds asymmetry | Larger shifts for right-oriented identities | Exploratory six-pair averages support the direction; estimator choice matters. GPT-3.5 collectivist exceeds individualist slightly on logit-of-means. Avoid interpreting every identity pair as a verified left/right dichotomy. |
| Matched prompt wording | Biography is the only difference | Option wording is retained, but the collector randomizes displayed A/B order independently for each request and does not save that order. |

## Figure 4 printed values

The original Figure 4 presents baseline liberal/conservative probabilities of 79.9%/20.1%, liberal-bio probabilities of 99.9%/0.1%, and conservative-bio probabilities of 4.8%/95.2%. Those are transcribed artwork annotations. Their population is not reproducibly identified in the manuscript.

For the corresponding available **GPT-4 liberals/conservatives Climate Change** topic, 200 raw records give baseline liberal/conservative means of **82.5984%/17.3759%**, liberal-bio aligned mean **89.0238%**, and conservative-bio aligned mean **67.0200%**. Figure 4's new schematic uses these computed topic means and explicitly labels treatment cross-option complements as approximations. It does not force the data to match the old illustrative percentages. The authentic carbon-emissions prompt is used to illustrate prompt structure, while the percentages aggregate the complete topic as indicated in the original figure.

## Duplicate sensitivity

There are 423 repeated complete scored occurrences in GPT-3.5 and 233 in GPT-4. The GPT-3.5 authoritarian/libertarian Climate Change file consists of ten distinct scored records repeated twenty times each. All fourteen aligned-biography mean shifts remain positive in both models after exact-record deduplication. The largest change in mean aligned shift is about 3.15 percentage points (GPT-3.5 authoritarians). Record counts should not be described as independent observations without additional justification.

The detailed audits and machine-readable comparison tables allow revisions to be checked against exact files and values.

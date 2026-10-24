# fusion-tax.pdf

- pages: 18
- extracted characters: 100437
- tables found: 8 pages; figures: 3 pages

## First page (opening lines)
```
Date of publication October 15, 2026.
Digital Object Identifier 10.1109/ACCESS.2026.3743502
The Fusion Tax: A Diagnostic Analysis
of When Hybrid Retrieval Hurts
AADITYA CHAUHAN ORCID1 and ARUN AGARWAL ORCID2
1Independent Researcher, Bothell, WA 98012 USA (e-mail: aadityc28@gmail.com)
```

## Sections
- p1: I. INTRODUCTION
- p2: II. RELATED WORK
- p2: A. DENSE AND SPARSE RETRIEVAL
- p2: B. HYBRID FUSION AND THE RRF DEFAULT
- p3: C. SCORE CALIBRATION VERSUS RANK FUSION
- p3: D. QUERY PERFORMANCE PREDICTION
- p3: E. SELECTIVE RETRIEVAL AND PER-QUERY ROUTING
- p3: F. RISK-SENSITIVE FUSION AND FUSION-QPP
- p3: G. FIRST-STAGE FUSION, RERANKING, AND RAG
- p4: III. PROBLEM FORMULATION AND TERMINOLOGY
- p4: A. DIAGNOSTIC TAXONOMY
- p4: B. THE FUSION TAX
- p4: IV. EXPERIMENTAL SETUP
- p4: A. DATASETS
- p5: B. RETRIEVAL METHODS
- p5: C. RERANKING AND EFFICIENCY MEASUREMENTS
- p5: D. EVALUATION METRICS AND STATISTICS
- p5: E. QUERY FEATURES FOR PREDICTABILITY
- p5: V. RESULTS
- p6: A. BASELINE VALIDATION
- p6: B. FUSION METHOD COMPARISON AND THE
- p6: C. DIAGNOSTIC TAXONOMY
- p8: D. THE FUSION TAX: HARM AND BENEFIT
- p8: E. ROBUSTNESS ACROSS THE ENCODER SCALE
- p10: F. ROBUSTNESS TO THE SPARSE METHOD: SPLADE
- p13: I. EFFICIENCY
- p13: VI. DISCUSSION
- p13: A. RRF IS NOT A SAFE DEFAULT, AND WHEN IT IS THE
- p14: C. CORPUS PATTERNS IN BRIEF
- p14: D. PRACTICAL DECISION FRAMEWORK
- p15: E. WHY PER-QUERY ROUTING IS HARD
- p15: F. TEMPORAL STABILITY AS ENCODERS EVOLVE
- p15: G. LIMITATIONS AND FUTURE WORK
- p16: VII. CONCLUSION

## Tables and figures
- p4 TABLE 1: TABLE 1. Positioning against prior lines of work. “Loss reference” is the quantity a per-query loss is measured against; LOCO = leave-one-corpus-out.
- p5 TABLE 2: TABLE 2. Dataset statistics (BEIR test splits).                                 is held fixed at α = 0.7 for every encoder and corpus in
- p7 TABLE 3: TABLE 3. Baseline validation: single-retriever nDCG@10 on all seven datasets. Anserini BM25 (ours) vs. the published Anserini regression values [14]; the
- p7 TABLE 4: TABLE 4. Held-out selection of the interpolation weight (BGE-small). In-sample: best α on the evaluation queries; LOCO: α chosen on the other six corpora; CV:
- p7 TABLE 5: TABLE 5. nDCG@10 across retrieval and fusion methods (BGE-small, Anserini BM25). Best per row in bold.
- p7 FIGURE 1: FIGURE 1. Per-query BM25 vs. dense nDCG@10 (BGE-small). For visualization only, each query is colored by the best of the three fusion methods with a 0.01
- p8 TABLE 6: TABLE 6. Diagnostic quadrant distribution (% of queries, BGE-small, Anserini    95% of queries with a net loss of 0.14–0.37 nDCG@10: the
- p9 FIGURE 2: FIGURE 2. Distribution of the per-query fusion tax τ (Eq. 1) pooled over the seven datasets (BGE-small). Positive values are queries that fusion hurt; the long 
- p9 TABLE 7: TABLE 7. The interpolation tax by diagnostic quadrant (BGE-small, vs. the per-query oracle). Sh.: quadrant share of queries (%); Hurt/Help: % of the quadrant’s
- p9 TABLE 8: TABLE 8. Symmetric harm/benefit accounting of fusion (BGE-small). Hurt/Help: percentage of queries with lower/higher nDCG@10 than the reference; Loss/Gain:
- p10 FIGURE 3: FIGURE 3. Fusion tax (% of queries hurt) as a function of dense-encoder size (log scale) for interpolation (left) and RRF (right), all seven corpora. The tax do
- p11 TABLE 9: TABLE 9. The fusion tax across five encoders spanning 22M–596M parameters and three model generations, all seven corpora. BGE-small/base/large form a
- p11 TABLE 10: TABLE 10. Robustness to the sparse method (BGE-small). SPLADE replaces BM25 as the sparse side; “Tax %” is the oracle tax; SP+De = SPLADE+dense,
- p12 TABLE 11: TABLE 11. Per-corpus GBT feature importance for predicting interpolation failure (bold: top-3 per corpus). Superscripts give the sign of the feature’s Spearman
- p14 TABLE 13: TABLE 13. Reranking recovery (BGE-reranker-v2-m3 over the top-30 of each candidate source, BGE-small, Anserini BM25; Quora subsampled to 1,000 queries).
- p14 TABLE 14: TABLE 14. Cost of each component on one consumer workstation (Apple M5, CPU cores; no discrete GPU): index sizes and per-query latencies, median over 200

## Lines carrying two or more numbers (sampled)
- p1: Date of publication October 15, 2026.
- p1: 1Independent Researcher, Bothell, WA 98012 USA (e-mail: aadityc28@gmail.com)
- p1: 2Independent Researcher, Issaquah, WA 98027 USA (e-mail: arunagar28@gmail.com)
- p1: published in IEEE Access, vol. 14, pp. 159620–159637, 2026, DOI: 10.1109/ACCESS.2026.3743502, under a Creative Commons
- p1: Attribution 4.0 (CC BY 4.0) license.
- p1: arXiv:2610.30612v1  [cs.IR]  22 Oct 2026
- p1: BM25, five dense encoders spanning 22M–596M parameters and three model generations, a learned-sparse
- p1: two components on 13–48% of queries and below the deployable dense-only retriever on 8–21% (14–
- p2: 13–48% of queries pay an oracle tax and 8–21% score
- p2: (mean 0.59, ranging from chance at 0.49 to 0.74), a
- p2: 71–90% of the originally hurt queries are individually
- p2: candidate sets differ by at most 0.011 nDCG@10 with
- p2: queries, and its Anserini/Pyserini implementation [11], [12]
- p2: is the reference point for BEIR [13], [14]. Learned sparse
- p2: models such as SPLADE [15], [16] add learned term expan-
- p2: SUM/CombMNZ [17], [18] and weighted interpolation [19])
- p3: models [40], [41] calibrate scores on a relevance scale at
- p3: For sparse–dense hybrids, Ma et al. [43] and Chen et al. [44]
- p3: models [51] or a complexity-tiered pipeline [52], [53]; and a
- p3: and dense retrievers [54], margin-based confidence [55], or a
- p3: average has roots in risk-sensitive evaluation [57], [58]. Ben-
- p3: 21 worsened on Robust04). The fusion-QPP line [5], [6]
- p3: dates [61]–[64], and RAG pipelines then pass a truncated
- p3: tribution they were trained on [65], [66], their effectiveness
- p4: where relevant passages sit in the context [71], [72] and on
- p4: the composition of the retrieved set [73]–[75], which is why
- p4: • Both-Win: NDCGs(q) > 0 and NDCGd(q) > 0;
- p4: • Dense-Only: NDCGd(q) > 0 and NDCGs(q) = 0;
- p4: • Sparse-Only: NDCGs(q) > 0 and NDCGd(q) = 0;
- p4: • Both-Fail: NDCGs(q) = 0 and NDCGd(q) = 0.
- p4: Fusion hurts q when τ(q) > 0 and helps it when τ(q) < 0;
- p5: through Pyserini [12] (version 1.6, Java 21) over the offi-
- p5: with Anserini’s default parameters k1 = 0.9, b = 0.4.
- p5: 596M parameters and three model generations (2021,
- p5: 2023, 2025): all-MiniLM-L6-v2 [78] (22M, 384-d), BGE-
- p5: Qwen3-Embedding-0.6B [80] (596M, 1024-d, released
- p5: raises dense nDCG@10 by at most 0.026 on five corpora
- p5: (under 0.02 in all but one model–corpus pair), by 0.09–0.11
- p5: Table S10). Quora is subsampled to 1,000 queries (seed 42)
- p6: duce the published Anserini BM25 nDCG@10 [14] to four
- p6: Python rank_bm25 runs are 0.01–0.20 lower, most severely
- p6: on TREC-COVID (0.459 vs. 0.656); Supplementary Table S1
- p6: pora and from base to large on FiQA (0.391→0.443), and
- p6: and TREC-COVID (0.467, 0.674, 0.227, 0.892) and weaker
- p6: (0.699, 0.355, 0.872). The ladder therefore provides gen-
- p6: Table 5 reports nDCG@10 for every method with BGE-
- p6: 0.04–0.18 nDCG@10 (0.039 on SciDocs): SciFact, FiQA,
- p7: TABLE 3. Baseline validation: single-retriever nDCG@10 on all seven datasets. Anserini BM25 (ours) vs. the published Anserini regression values [14]; the
- p7: TABLE 5. nDCG@10 across retrieval and fusion methods (BGE-small, Anserini BM25). Best per row in bold.
- p7: FIGURE 1. Per-query BM25 vs. dense nDCG@10 (BGE-small). For visualization only, each query is colored by the best of the three fusion methods with a 0.01
- p7: deadband: green, fusion helped (τ < −0.01); red, fusion hurt (τ > 0.01); gray, neutral. Harm concentrates off the diagonal, where the retrievers disagree.
- p8: ficulty (SciDocs 34%, FiQA 30%, NFCorpus 24%). Fusion
- p8: (interpolation, α = 0.7) hurts 12.8% of queries on the easy,
- p8: dense-dominated Quora set, 20–39% on five corpora, and
- p8: 48% on the 50-query TREC-COVID set; RRF hurts 20–
- p8: 40% and CombMNZ 17–40% (per-method rates and mean
- p8: requiring a material loss of τ > 0.05 nDCG@10 still leaves
- p8: 10–34% of queries (interpolation) and τ > 0.10 leaves 8–
- p8: hurt query is 0.09–0.25 nDCG@10. Bootstrap confidence
- p9: Fusion tax τ (NDCG@10 loss; τ > 0 = fusion hurt)
- p9: Fusion tax τ (NDCG@10 loss; τ > 0 = fusion hurt)
- p9: Fusion tax τ (NDCG@10 loss; τ > 0 = fusion hurt)
- p9: FIGURE 2. Distribution of the per-query fusion tax τ (Eq. 1) pooled over the seven datasets (BGE-small). Positive values are queries that fusion hurt; the long right
- p9: tail (log-scale counts) shows that when fusion hurts, the loss can exceed 0.5 nDCG@10.
- p9: TABLE 8. Symmetric harm/benefit accounting of fusion (BGE-small). Hurt/Help: percentage of queries with lower/higher nDCG@10 than the reference; Loss/Gain:
- p9: base, large: SciFact 20.0, 18.0, 16.7%; FiQA 23.3, 24.4,
- p9: 25.0%; NFCorpus 39.0, 40.9, 40.2%; ArguAna 30.4, 28.3,
- p10: shrink as encoders scale from 22M to 596M parameters.
- p10: than breaking it: interpolation hurts 14–43% of its queries
- p10: (SciFact 19%, FiQA 28%, NFCorpus 43%, ArguAna 33%,
- p10: SciDocs 37%, TREC-COVID 26%, Quora 14%) and RRF
- p10: 20–47%, while fusion beats Qwen3 alone in aggregate on
- p10: vs. 0.227), and loses to it on ArguAna (0.638 vs. 0.674),
- p10: vs. 0.33; 43%) and lowest where Qwen3 dominates (TREC-
- p10: COVID, 0.89 vs. 0.66, 26%; Quora, 0.87 vs. 0.79, 14%),
- p11: TABLE 9. The fusion tax across five encoders spanning 22M–596M parameters and three model generations, all seven corpora. BGE-small/base/large form a
- p11: chance) to 0.74 (SciFact) for interpolation and from 0.50
- p11: COVID. Capping every training corpus at 2,000 queries, so
- p11: that the 10,000-query Quora set cannot dominate the pooled
- p11: trainer, changes little (cross-corpus means 0.56 and 0.54),
- p11: and replacing the 17 features by the 384-dimensional dense
- p12: TABLE 11. Per-corpus GBT feature importance for predicting interpolation failure (bold: top-3 per corpus). Superscripts give the sign of the feature’s Spearman
- p12: similar degree (mean AUC 0.61 within a corpus and 0.57
- p12: across, ranging from 0.33 on NFCorpus to 0.66 on Quora;
- p12: routes nothing, on two it routes 1–6% of queries with no
- p12: and 23% of queries and loses 0.007 and 0.003 nDCG@10
- p12: an oracle gain of 0.007–0.041 (Supplementary Table S11).
- p12: sociation flips: 11 of the 17 features are positively associated
- p12: TABLE 12. Predicting fusion failure from 17 query features (held-out
- p13: of the deployable tax there (47 of 59 hurt queries repaired, 23

## How to use this map
- Read this map first. Select at most 8 pages that the decision actually needs.
- Prose lives in pages/pNN.txt (column-aware). Tables/figures live in tables/pNN.txt (layout-preserving).
- Every number that enters the memo must be recorded in ledger.json with a page and a verbatim quote.

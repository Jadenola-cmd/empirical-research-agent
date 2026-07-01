# Interpretation Checklist: Causal Inference (DID / PSM / PSM-DID)

## 1. DID (Difference-in-Differences)

### Coefficient sign and direction
- The DID coefficient estimates the causal effect of treatment. Interpret as: "After controlling for group and time fixed effects, the treatment led to a change of X units in the outcome variable."
- Sign should match theoretical expectations. If unexpected, discuss possible confounding mechanisms.

### Significance reporting
- Report DID coefficient with standard errors (clustered at entity level recommended).
- Parallel trends test p-value: if p >= 0.05, explicitly state "parallel trends assumption holds."

### Parallel trends test
- This is the **most critical** validation step for DID. Report F-statistic and p-value.
- If pre-treatment coefficients are jointly insignificant: "Parallel trends assumption is supported."
- If pre-treatment coefficients are significant: "Parallel trends assumption is violated; DID estimates may be biased. Consider alternative methods or discuss limitations."

### Event study coefficients
- Pre-treatment coefficients should be close to zero and insignificant.
- Post-treatment coefficients should show the treatment effect pattern (immediate vs. gradual).
- The period just before treatment (t=-1) is the reference period.

### Reviewer FAQ
- "Is the parallel trends assumption satisfied?" → Report event study results.
- "Are there anticipation effects?" → Check if t=-1 coefficient differs from earlier periods.
- "Are standard errors clustered?" → Always cluster at entity level for panel DID.

---

## 2. PSM (Propensity Score Matching)

### Balance assessment
- Report standardized mean differences (SMD) before and after matching.
- Threshold: |SMD| < 0.25 after matching indicates good balance.
- State the number/proportion of covariates that achieved balance.

### ATT interpretation
- ATT = Average Treatment Effect on the Treated. Interpret as: "Among treated units, the treatment increased/decreased Y by X units on average."
- Report with standard error, t-statistic, and p-value.

### Common support
- Report the percentage of observations in the common support region (propensity scores between 0.01 and 0.99).
- If common support is limited, note that results only apply to the overlapping region.

### Matching quality
- Report number of treated, control, and matched pairs.
- If many treated units are unmatched (off-support), discuss potential selection bias.

### Reviewer FAQ
- "Why this matching method?" → Nearest neighbor is conservative; kernel uses all controls with weights.
- "Is the conditional independence assumption (CIA) satisfied?" → Acknowledge that PSM controls for observable differences only; unobserved confounders remain a limitation.
- "How was the caliper chosen?" → 0.05 is standard for nearest neighbor; report sensitivity to caliper choice.

---

## 3. PSM-DID

### Combined approach
- PSM-DID combines the strengths of both methods: PSM addresses selection on observables, DID removes time-invariant unobserved confounders.
- Report: matching balance → DID coefficient on matched sample.

### Interpretation
- "After matching on pre-treatment characteristics and applying DID, the treatment effect is..."
- More robust than either PSM or DID alone.

---

## 4. IV (Instrumental Variables) [beta]

### First-stage relevance
- Report first-stage F-statistic. Rule of thumb: F > 10 indicates strong instrument.
- If F < 10, instrument is "weak" and 2SLS estimates may be unreliable.

### Exogeneity
- For single instrument: cannot formally test exogeneity (just-identified model).
- For multiple instruments: report overidentification test (Sargan/Hansen J-test).

### Interpretation
- IV estimates are Local Average Treatment Effects (LATE) for compliers.
- Do not generalize to the full population unless instrument affects everyone equally.

### Reviewer FAQ
- "Is the instrument valid?" → Discuss relevance (F > 10) and theoretical justification for exogeneity.
- "Why not OLS?" → Report Wu-Hausman endogeneity test; if significant, IV is preferred.

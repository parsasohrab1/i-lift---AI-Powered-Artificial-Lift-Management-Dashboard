# Article submission content

Branch `article-submission-content` holds the material for the article planned for this product. The product code on the default branch is unchanged.

| Item | Value |
|------|-------|
| Target venue | Petroleum (KeAi) – شامل ویژه‌شماره‌ی کاربرد AI/ML در صنعت نفت |
| Type | journal |
| Deadline | rolling – پذیرش مداوم؛ ددلاین ویژه‌شماره‌ی AI/ML پیدا نشد |
| Official page | https://www.keaipublishing.com/en/journals/petroleum/petroleum-news/petroleum-latest-impact-factor-announced-35/ |
| Abstract rule (Elsevier / KeAi journal) | Single unstructured paragraph, no references, no undefined abbreviations; state objective, method, main results and conclusion. Typical length 150–250 words; keywords 4–6. |

## Title
Machine-Learning Failure Prediction and Operating-Point Optimisation for Electric Submersible and Rod Lift Systems

## Abstract (draft)
Artificial lift failures interrupt production and drive a large part of operating cost in mature oil fields. This paper presents an intelligent artificial-lift management system that predicts failures of electric submersible pumps (ESP) and rod pumps and recommends operating-point changes. Motor current, vibration, pressure and variable-speed-drive data are collected through Modbus and OPC-UA, converted into condition indicators, and used to train failure-prediction models for each lift type. A second module searches the feasible frequency and choke range for the operating point that maximises production under pump and reservoir constraints, and results are displayed on a web dashboard. The system was tested on historical data from [N] wells with [M] recorded failures. The failure model detected [X]% of failures with a median lead time of [Y] days and a false-alarm rate of [Z] per well-year, outperforming [baseline] on the same data. In simulated replays, the recommended operating points increased predicted production by [A]% without exceeding pump limits. The study shows that a single data pipeline can serve both condition monitoring and optimisation for different lift methods, and it discusses the labelling of failure events as the main practical difficulty.

**Keywords:** artificial lift; electric submersible pump; predictive maintenance; rod pump; production optimisation; machine learning

## Before submitting
1. Replace every `[bracketed]` placeholder with values measured by the team on real data; no number in the draft is a result.
2. Add author names and affiliations; confirm the abstract limits in the venue's author guidelines (the limits above are typical for the venue family).
3. Add the experiment scripts and data description used for the results to this branch.
4. The Word file for the submission system is prepared in the platform repository (`outputs/abstracts/`).

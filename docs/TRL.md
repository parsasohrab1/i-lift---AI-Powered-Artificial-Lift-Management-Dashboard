# Technology readiness (TRL) of the article component

**Level: TRL 4** for the component in `research/s_pet_intellilift`: conformal alarm threshold evaluated by well (component validated in a laboratory setting).

| Evidence | Where |
|---|---|
| Code with unit tests (synthetic data generated in the tests and labelled as such, never reported as results) | `research/s_pet_intellilift/tests` |
| Continuous integration | `.github/workflows/research-ci.yml` |
| Real-data validation | Petrobras 3W v2 real instances (1,119 instances, 40 wells); results in `research/s_pet_intellilift/results.json`. |

Not claimed: TRL 5 (relevant environment) for the whole product. This component is separate from the product's claimed functions; no claimed function is implemented or disclosed here. A patent attorney must review before any publication.

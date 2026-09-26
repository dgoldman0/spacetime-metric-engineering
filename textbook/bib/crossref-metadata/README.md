# Fetched bibliographic metadata

Raw responses saved while checking bibliography entries added on 2026-09-26
during the review of the textbook's thought experiments and checks.

- `10.1103_PhysRevLett.4.337.json`, `10.1119_1.1852541.json`,
  `10.1098_rsta.1920.0009.json`: Crossref records for Pound and Rebka (1960),
  Baez and Bunn (2005) and Dyson, Eddington and Davidson (1920). The entries
  `Pound1960`, `Baez2005` and `Dyson1920` in `references.bib` match them.
- `prl_4_337_abstract_page.html`: the APS abstract page for Pound and Rebka,
  which returned a bot-check page instead of the abstract. The tower height
  (74 feet) and the measured-to-predicted ratio (1.05 +- 0.10) were confirmed
  instead from the text of the paper, read from a copy kept outside the
  repository.
- `arxiv_gr-qc_0103044.xml`, `arxiv_gr-qc_0103044_https.xml`: two empty
  responses from the arXiv API when checking the arXiv number of Baez and
  Bunn. The `Baez2005` entry therefore carries no eprint field.
- `10.1103_PhysRevLett.121.161101.json`: Crossref record for the LIGO and Virgo
  analysis of GW170817 (Abbott et al. 2018), fetched while checking the claim
  that 5 × 10³³ Pa is the pressure deep inside a neutron star. The paper's
  constraint on the pressure at twice nuclear saturation density,
  3.5 (+2.7/−1.7) × 10³⁴ dyn/cm², was taken from its arXiv and publication
  listings found by web search (arXiv:1805.11581).
- `10.1103_PhysRevLett.123.033201.json`: Crossref record for Brewer et al.
  (2019), the aluminium-ion clock with a systematic uncertainty below 10⁻¹⁸,
  fetched for the redesigned stiffness thought experiment of Chapter 1.

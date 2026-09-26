# Bibliography notes

Built 2026-09-26 for `references.bib` (381 entries) and `citation_index.tsv`.

Sources of works: `inventory/lit_foundations.md` (cited by 162 entries),
`inventory/lit_design_strategy.md` (172), `inventory/lit_engineering_methods.md` (112),
`vetting/P01_classify_demand_before_sources.md` (15) and `02_SYNTHESIS.md` (48).
Ninety-one works are cited in more than one of these files; each has one entry.

Sources of metadata, in order of use:

1. Crossref records (the version of record) for every DOI: 336 records, cached in the
   scratchpad. The inventories supplied most DOIs; 42 bibliographic searches filled the rest.
2. arXiv abstract pages already downloaded (215 identifiers), plus 30 pages fetched for
   cited identifiers that had no local record.
3. The inventories' own citation lines, the Open Library records they cite, and the local
   full-text copies they read (for report numbers, thesis details, proceedings titles and
   the arXiv stamp showing which version was read).

Requests to arXiv and Crossref stayed below two per second.

## Entry types and fields

| Type | Count | Used for |
|---|---:|---|
| `@article` | 297 | journal articles, including those with a pinned arXiv eprint |
| `@online` | 24 | arXiv-only preprints, lecture notes, the FQXi essay, two theses whose institution is unrecorded |
| `@book` | 27 | monographs and textbooks |
| `@collection` | 2 | Lobo (ed.) 2017; Millis and Davis (eds.) 2009 |
| `@incollection` | 6 | chapters with verified editors |
| `@inbook` | 2 | chapters whose editors are unrecorded (Lobo2008, Leonhardt2009) |
| `@inproceedings` | 7 | conference papers |
| `@report` | 7 | Sandia, NASA and GAO reports; the Dowding slides (SAND number) |
| `@manual` | 7 | ASME, AIAA and NASA standards; the Cactus users' guide |
| `@thesis` | 1 | Olason and Tidman (master's thesis) |
| `@misc` | 1 | Tillack's 2008 presentation |

- `keywords` holds the verification status (one of four values; see below).
- `eprint` holds the arXiv identifier with its version, `eprinttype = {arxiv}`, and
  `eprintclass` where a local record gives the primary class. Old-style identifiers
  (`gr-qc/9410043v1`) carry the class in the identifier. Twenty new-style identifiers have
  no primary class in any local record, so `eprintclass` is absent there.
- `note` (printed, 45 entries) carries version hazards and the nature of an item
  (dissertation, lecture notes, essay, standard revision).
- `addendum` (printed, 3 entries) carries errata and a republication.
- `annotation` (not printed by the standard styles, 111 entries) carries provenance: which
  source supplied a field, and each conflict recorded below.
- `sorttitle` (61 entries) and `sortname` (2 entries) only steer sorting. They make the
  printed year letters match the key letters; see "Printed labels".
- Journal fields follow Crossref. JHEP and JCAP therefore read volume = year,
  number = issue, eid = article number; JHEP article numbers keep the three digits of the
  DOI (`JHEP09(2019)020` gives eid `020`).

## Verification status

| Keyword | Entries | Meaning, as recorded by the inventories |
|---|---:|---|
| `verified-fulltext` | 127 | the full text, or named sections of it, of the cited version was read |
| `verified-abstract` | 179 | the arXiv abstract page, a publisher abstract, product description, summary page or table of contents was read |
| `metadata-only` | 63 | bibliographic data confirmed; content unread or known through a secondary source |
| `unverified` | 12 | listed as unverified; bibliographic data found for this bibliography, content unread |

Mapping of each inventory's vocabulary:

- **Foundations.** The nine full-text checks named in its method section and every item
  tagged "(text read)" give `verified-fulltext`. Other arXiv items, and "the APS/Springer
  abstract was read", give `verified-abstract`. "PARTIAL (metadata only)" gives
  `metadata-only`. Books whose table of contents was read (Lobo2017, Krasnikov2018,
  Everett2011) give `verified-abstract`; books checked against a catalogue give
  `metadata-only`.
- **Design strategy.** "Read vN" (Parts A and B), "full text https://arxiv.org/pdf/…"
  (Part C) and Part D entries outside its abstract-level list give `verified-fulltext`.
  "Verified via abstract page", "abstract-level", the abstract-level lists of Parts G.1 and
  G.3, and "abstract plus a text search" (Lentz2021, Fell2021, Gergely2026) give
  `verified-abstract`. Bolivar2025 (title and journal through Crossref only) is
  `metadata-only`. Borde1987 and Azad2024b, known only through other papers, are
  `unverified`.
- **Engineering methods.** "VERIFIED (full text)" gives `verified-fulltext`;
  "VERIFIED (abstract / product description / summary page / OSTI abstract)" gives
  `verified-abstract`; "PARTIAL" gives `metadata-only`; "UNVERIFIED" gives `unverified`.

Where inventories (or clusters within the design inventory) record different levels for
the same work, the entry takes the higher recorded level; within one cluster, that
cluster's explicit abstract-level list governs.

- Foundations full text over a design abstract-level record: Fewster2003, Faulkner2016,
  Hartman2017.
- Design full text over a foundations abstract or metadata record: Ford1995, Ford1996b,
  Pfenning1997, Freivogel2022, Kontou2024, Wall2010, Urban2010a, Penrose1993, Finazzi2009,
  Morris1988a (foundations: metadata only), Morris1988b, Everett1997, Krasnikov1998,
  Shoshany2024, Olum1998, Visser2000, Gao2000, Alcubierre1994, Santiago2022, Barzegar2026,
  Clough2024, Natario2002, VanDenBroeck1999, Bobrick2021, Fuchs2024, Schuster2023,
  Rubakov2016a, Evseev2018, Franciolini2019, Mironov2019, Mironov2023.
- Across design clusters: Kontou2015 and Hawking1992 are full text in the Part C cluster
  and abstract-level in the wormhole cluster (G.3); both are `verified-fulltext`.
- Design "cited only through verified papers" against a foundations entry: Tipler1976,
  Flanagan1996, Wald1991 and Visser1995a keep `verified-abstract`; Tipler1977 keeps
  `metadata-only`.
- Within the wormhole cluster: Azad2025 is on the G.3 abstract-level list while F.3.5
  reports a statement from its full text; Zhang2023 (LiuEtAl2023) is on the same list while
  its entry cites the text. Both are `verified-abstract`.

## Keys

- First author's (or first editor's) surname in ASCII plus year: accents stripped, spaces
  and hyphens removed (MartinMoruno, SantosPereira, VanDenBroeck, GonzalezDiaz,
  BlazquezSalcedo, FouresBruhat, AbuShawareb, LoPiano, Loffler, Bendsoe, Gurses);
  DeNeufville2011 capitalizes the particle.
- Corporate authors: AIAA1998, ASME2009, ASME2018, ASME2019, NASA2016, NASA2024, GAO2020.
  The Cactus users' guide has no author and takes the key Cactus2026.
- Year: the year of the version of record. Journal articles take the print volume year
  when Crossref gives one; arXiv-only works take the year of v1.
- Suffixes kept from the inventories: Le2026a (boundary cost, 2605.25417v2), Le2026b
  (observer-robust verification, 2602.18023v6), Le2026c (radiative steering, 2606.22531v4);
  MartinMoruno2018a (essential core) and MartinMoruno2018b (type III geometry); Bousso2016a
  (focusing conjecture) and Bousso2016b (QNEC proof); Visser1989a/b; Rubakov2016a/b;
  Gonzalez2009a/b; Fu2019a/b; Kain2023a/b. HochbergVisser1998PRL and ...PRD became
  Hochberg1998a and Hochberg1998b.
- Other suffixes follow publication order, then inventory order where dates coincide
  (Millis2005a is the NASA memorandum and Millis2005b the Annals paper of the same title;
  Visser1995a is the scale-anomaly paper and Visser1995b the monograph).

Keys that differ from the inventories' labels:

| Inventory label | Key | Reason |
|---|---|---|
| LiuEtAl2023 | Zhang2023 | Crossref author order of the journal article (see conflicts) |
| Rodal2025 (design) | Rodal2026a | Gen. Relativ. Gravit. 58, 1 (2026), online 17 Dec 2025 |
| Rodal2025Metamaterial | Rodal2025 | |
| Rodal2026Birefringent | Rodal2026b | |
| Rodal2023_2024 | Rodal2023, Rodal2024 | |
| Azad2023 | Azad2024a | Phys. Lett. B 848 (2024) |
| (Azad et al., PRD 109, 124051) | Azad2024b | |
| KanaiMaedaYoshida2025 | Kanai2026 | Phys. Rev. D 113 (2026) |
| MaldacenaMilekhinPopov2023 | Maldacena2023 | |
| HochbergPopovSushkov1997 / HochbergVisser1997 | Hochberg1997a / Hochberg1997b | publication order |
| FR96, FordRoman1996 / Ford–Roman evaporating black holes | Ford1996b / Ford1996a | publication order |
| PF98 / Pfenning dissertation | Pfenning1998a / Pfenning1998b | publication order |
| VBL98 / VBL99 | Visser2000 / Visser1999 | journal years |
| Visser1997 (Roman ring) / vacuum polarization IV | Visser1997a / Visser1997b | publication order |
| FE98, F00, FH05, FewsterRoman2005 | Fewster1998, Fewster2000b, Fewster2005a, Fewster2005b | Fewster2000a is Fewster and Teo |
| UO10 / spacetime-averaged ANEC | Urban2010a / Urban2010b | |
| SSV2022, SSVADM2023, SSVTractor2021 | Santiago2022, Schuster2023, Santiago2021 | |
| BBV, BarzegarBuchertVigneron2026 | Barzegar2026 | |
| BarzegarBuchert2025 | Barzegar2025 | |
| WarpFactory2024 (N7, 6.7) | Helmerich2024 | |
| Warp Factory toolkit paper (AIAA 2023) | Helmerich2023 | |
| GarattiniZatrimaylov2024_2025 | Garattini2023 (precursor), Garattini2024a (JCAP), Garattini2024b (PLB), Garattini2025 (de Sitter) | |
| SantosPereiraAbreuRibeiro2020_2026 | SantosPereira2020, 2021a, 2021b, 2023 (MG16), 2025 (thesis), 2026a (EPJC), 2026b (EPJP) | |
| AbellanBolivarVasilevSeries | Abellan2023a (EPJC 83, 7), Abellan2023b (GRG 55, 60), Abellan2023c (arXiv 2305.03736), Abellan2024 (CQG 41), Bolivar2025 (Ann. Phys. 481), Abellan2026 (Ann. Phys. 485) | |
| BolivarAbellanVasilev2026 | Bolivar2026 | |
| MartinMorenoVisser2018_2021 | MartinMoruno2018a, MartinMoruno2021 | |
| Everett–Roman (book), Frontiers of Propulsion Science, Lobo (ed.) | Everett2011, Millis2009, Lobo2017 | |

### Printed labels

biblatex assigns the printed year letters (2026a, 2026b, …) in sort order, which by default
follows the title. Each suffixed key therefore carries `sorttitle = {<letter> <title>}`, and
Bousso2016a/b carry a shared `sortname` because their author lists differ. In a test with the
book's options (`maxcitenames=2`, `uniquename=init`) all 47 suffixed keys that share an
author label print the matching letter; the remaining suffixed keys (for example Fewster2000a,
Fewster and Teo, against Fewster2000b, Fewster alone) print distinct names and no letter.

## Version pins and version hazards

All 238 eprints carry a version. For 219 of them the pin is the version the source files
record: the 218 eprints of works cited in the foundations or design inventories or in P01,
and gr-qc/0505065v4 for Barcelo2026, which the engineering inventory records.

For its other 19 eprints the engineering inventory records no version; they are pinned here
and annotated:

- From the arXiv stamp on the local full-text copy it read: Alcubierre2004
  (gr-qc/0305023v1), Babiuc2008 (0709.3559v3), Loffler2012 (1111.3344v1), Yan2007
  (0706.0655v2), Li2008 (0806.4396v1), Zhang2011 (1012.2238v3), Hashemi2010 (1003.5934v3),
  Leonhardt2006b (cond-mat/0607418v2), Molesky2018 (1801.06715v1), Wurzel2022
  (2105.10954v4).
- Only version: Monticone2013 (1307.3996v1), Chen2013 (1306.5835v1).
- Latest version on 2026-09-26, matching the abstract page it read: Hannam2009
  (0901.2437v3), Hinder2014 (1307.5307v3), Leonhardt2006a (physics/0602092v1), Zhang2010
  (1004.2551v2), Weinfurtner2011 (1008.1911v2), Steinhauer2016 (1510.00621v3),
  Philbin2008 (0711.4796v2).

Version hazards, each with a printed `note`:

| Key | eprint | Hazard |
|---|---|---|
| Le2026a | 2605.25417v2 | v1 and v2 carry "On the boundary cost of source-consistent warp shells"; v3 (17 Sep 2026) is a different paper, "Relativistic elastic shells: material support and cavity geometry". The arXiv page now shows the v3 title; the entry uses the v2 title (inventory and local v2 text). |
| Le2026c | 2606.22531v4 | v1–v3 are titled "Steering a warp drive without exotic matter"; v4 (13 Sep 2026) is revised and retitled "Radiative steering of warp shells". The local abstract record is of v2; the title comes from the local v4 PDF. |
| Le2026b | 2602.18023v6 | six versions (20 Feb to 24 Sep 2026); v6 is pinned |
| Rodal2026b | 2603.21352v2 | v3 (24 May 2026) is a different paper (Tamm–Rubilar diagnostics for Drummond–Hathrell propagation) with the warp claim moved to an appendix |
| Krasnikov1998 | gr-qc/9511068v6 | v1–v5 are withdrawn placeholders; the arXiv title is "Hyperfast Interstellar Travel in General Relativity" |
| Pfenning1997 | gr-qc/9702026v3 | v2 is a withdrawn placeholder; v3 corrects a sign in Eq. (3) |
| Visser2000 | gr-qc/9810026v2 | v1 claims a non-perturbative ANEC theorem that v2 abandons |
| Friedman1993 | gr-qc/9305017v2 | v1 withdrawn; v2 (1995) is the corrected paper; erratum PRL 75, 1872 in `addendum` |
| Penrose1993 | gr-qc/9301015v2 | v1 withdrawn |
| Visser1993 | hep-th/9202090v2 | v1 withdrawn; arXiv title reads "Comments on", journal title "Remarks on" |
| Garattini2025 | 2502.13153v4 | v4 title "Warp Drive in a De Sitter Universe"; Le (2026a) cites it as "Positive-energy warp drive in a De Sitter universe", apparently an earlier title |
| Fliss2025b | 2510.26247v2 | v2 simplifies the higher-dimensional inequality and clarifies its state dependence |
| Konoplya2022 | 2106.05034v4 | v1 title "Traversable wormholes in General Relativity without exotic matter" |
| Graham2007, Balakrishnan2019, Bronnikov2012, Fu2019a, Maldacena2023, Natario2006 | as pinned | later version changes a theorem condition, fixes an error, corrects equations or a factor of 2, or restricts the validity regime |
| Alcubierre1994, Rodal2023, Rodal2024, Visser1989a, Visser1989b | as pinned | arXiv posting postdates journal publication |
| Barzegar2025 / Barzegar2026 | 2407.00720v2 / 2602.16495v1 | two-author and three-author papers are distinct (design inventory hazard list) |
| Barcelo2026 | gr-qc/0505065v4 | v4 (29 Nov 2024) is the text read; its correspondence with the 2026 Living Reviews edition is unconfirmed |

## Duplicates merged

- Ninety-one works cited in two or more source files have one entry each (64 of them in
  both the foundations and design inventories). This includes the design inventory's
  cross-reference aliases: FR96 = FordRoman1996, ER97 = EverettRoman1997, FSW93,
  GO07 = GrahamOlum2007, KO15 = KontouOlum2015, FK18 = FreivogelKrommydas2018,
  K24 = Kontou2024, H92 = Hawking1992, SS24, SSV22, Le26, JL26, GZ25 and LV04. Warp
  Factory (foundations 6.7, design WarpFactory2024, engineering N7, P01) is Helmerich2024.
- arXiv notes and their published chapters: MartinMoruno2017 (1702.05915v3 with the
  Springer chapter, pp. 193–213) and Alcubierre2017 (2103.05610v1 with the chapter,
  pp. 257–279).
- Errata merged into the corrected paper (`addendum`): Friedman1993 (PRL 75, 1872) and
  Fewster2003 (PRD 80, 069903).
- Republication merged: Arnowitt1962 carries the 2008 Gen. Relativ. Gravit. republication
  (40, 1997–2027, doi:10.1007/s10714-008-0661-1) in `addendum`; its `doi` field and the TSV
  DOI column stay empty because that DOI identifies the republication.
- The open OSTI copy of Oberkampf and Trucano (2002) is noted in Oberkampf2002.

Kept as separate works: the 2012 QEI lecture notes and the 2017 QEI chapter (Fewster2012,
Fewster2017); the 3+1 notes and book (Gourgoulhon2007, Gourgoulhon2012); the three Living
Reviews editions of *Analogue Gravity* (Barcelo2005, Barcelo2011, Barcelo2026); Lentz2021
and its MG16 companion Lentz2023; the Warp Factory papers Helmerich2023 and Helmerich2024;
Millis2005a and Millis2005b; Tillack2008 (slides) and Tillack2009 (paper); Mankins1995 and
Mankins2009; Oberkampf2010 and its second edition Oberkampf2025; Garattini2023 and
Garattini2024b.

## Metadata conflicts and corrections

- **DOI correction, Friedman2006.** The arXiv page of 0801.0735 and the foundations
  inventory give 10.1002/andp.200510172; Crossref assigns that DOI to H. Friedrich, "Is
  general relativity 'essentially understood'?" (pp. 84–108). Crossref assigns
  10.1002/andp.200510173 to Friedman and Higuchi (pp. 109–128), which the entry uses. The
  volume is 518 in Crossref numbering (Ann. Phys. (Leipzig) 15 in the inventory).
- **Authors, Mironov2023.** Crossref lists S. Mironov and V. Volkova only; arXiv and both
  inventories list Mironov, Rubakov and Volkova. The entry keeps three authors. Check the
  published article before citing.
- **Author order, Zhang2023.** Crossref lists C.-Y. Zhang first and P. Liu last; arXiv and
  the design inventory list Liu first. The entry follows Crossref, which changes the key.
- **Authors, Helmerich2023.** Crossref (AIAA paper) lists seven authors, including S. Dangelo
  and J. F. Agnew; arXiv 2404.10855 lists six, including B. Melcher. The entry follows Crossref.
- **Author order, Alcubierre2004.** Crossref is alphabetical (Shoemaker before Szilágyi);
  arXiv reverses the pair. The entry follows Crossref.
- **Author count, Hinder2014.** Crossref and arXiv both list 56 authors; the engineering
  inventory states 84.
- **Author list, Celik2008.** Crossref lists no authors. The entry gives the four authors
  confirmed by the inventory and ends with `and others`.
- **Name splits.** Crossref and arXiv both store Van Den Broeck as family "Broeck"; the entry
  uses "Van Den Broeck, Chris". Crossref stores the Deffayet2010 names whole in the family
  field; the entry splits them as on arXiv.
- **Dissertation authors, Pfenning1998b.** The arXiv record lists L. H. Ford as co-author;
  the entry follows the record.
- **Pages.** Duff1994: Crossref 1387–1403, inventory and arXiv 1387–1404. Natario2002:
  Crossref 1157–1165, design inventory 1157–1166. Both entries follow Crossref.
- **Dates.** Hinder2014: Crossref gives a 2013 print date for volume 31 (2014); the entry
  uses 2014. Saltelli2008: Crossref print date 18 Dec 2007, online 21 Jan 2008; the entry
  uses 2008 as the inventory does. Bendsoe2003: second edition 2003 (ISBN 3540429921);
  Crossref dates the eBook DOI record 2004. Shibata2015: Crossref issue date 2015; the
  printed year is unverified. Everett2011: the publisher and Crossref give 2011; the book is
  often cited as 2012.
- **Volume.** Steward1981: Crossref gives "EM-28"; biblatex needs an integer, so the entry
  uses 28.
- **Publisher.** Visser1999: Crossref's publisher field reads "ASCE" for this AIP record and
  is left out; the series and volume (AIP Conf. Proc. 493) come from the design inventory.
  Publisher strings are normalized: "WORLD SCIENTIFIC" to World Scientific, "ASMEDC" to
  ASME (Olewnik2003), and Earman's run-together "Oxford University PressNew York, NY" to
  publisher Oxford University Press, location New York.
- **Titles.** Published titles are used where they differ from arXiv titles: MartinMoruno2021,
  Banerjee2023 ("Realizations"), Moghtaderi2025, Bousso2016a, Visser1996c, Flanagan1996,
  Ishibashi2019, Dvali2008 ("at CERN LHC"), Everett1997, Krasnikov1998, Kobayashi2016,
  Evseev2018 (arXiv misspells "sphericaly"), GonzalezDiaz2000, McMonigal2012, Krasnikov2003,
  Hochberg1998a, Hochberg1998b, Danielson2021, Visser1993, Alcubierre2004, Hannam2009,
  Leonhardt2006a, Chen2013, Molesky2018, Philbin2008. Barcelo2002 uses "Twilight for the
  energy conditions?", as the foundations inventory corrects it. All-capital Crossref titles
  (Barcelo2002, Fewster2005a) and MathML titles (Lobo2009, Ishibashi2019) are replaced by
  the arXiv or inventory wording.
- **Name forms.** Names follow each record, so some people appear in two forms: Wald (R.;
  R. M.), Roman (T.; T. A.), Rubakov (V.; V. A.), Krasnikov (S.; S. V.), Pendry (J.; J. B.),
  Oberkampf (W.; W. L.), Trucano (T.; T. G.), Friedman (J.; J. L.), Geroch (R.; R. P.),
  Everett (A.; A. E.), Flanagan (E. E.; É. É.), Bassett (B.; B. A.), Bolívar (Bolivar in the
  Crossref records of Abellan2023a/b). With `uniquename=init` biblatex prints initials in
  citations to separate these forms.

## Metadata added beyond the inventories

Fetched for this bibliography and marked in `annotation`:

- Journal references for items the inventories list as preprints or accepted papers:
  Banerjee2023 (Phys. Rev. D 108, 084047), Gergely2026 (Phys. Rev. D 114, 064064),
  Mironov2024 (Int. J. Mod. Phys. A 39, 2443011) and Chowdhury2025 (Eur. Phys. J. C 85, 112).
- DOIs: Ceyhan2020, Fliss2024, Fliss2025a, Leonhardt2006a, Monticone2013, Sigmund2001,
  Sobol2001, Saltelli2010, LoPiano2021, Eppinger2012, Tucker2011, Earman1995, Everett2011,
  Lentz2023, AbuShawareb2024, and the chapter DOIs of MartinMoruno2017, Fewster2017,
  Alcubierre2017 and Barcelo2017. DOIs shown on arXiv pages were added where the inventories
  omit them (for example Natario2002, VanDenBroeck1999, Clark1999, Visser1996a–c,
  Visser1997b, Bousso2016a/b, Balakrishnan2019).
- Editors of *Frontiers of Propulsion Science* (Millis2009: M. G. Millis and E. W. Davis).
  Crossref now lists them; the foundations inventory found none.
- Subtitles the foundations inventory marks unverified: Gourgoulhon2012 ("Bases of Numerical
  Relativity") and Baumgarte2010 ("Solving Einstein's Equations on the Computer").
- Issue numbers, page ranges or article numbers, and full author lists for every DOI'd
  article, from Crossref (AbuShawareb2024 lists 1,356 names and the Indirect Drive ICF
  Collaboration).

## Items left incomplete

Fields are omitted where no verified source gives them.

- **Place of publication** is absent from the Crossref records and the inventories for:
  Hawking1973, Birrell1982, Parker2009, Alcubierre2008, Baumgarte2010, Baumgarte2021,
  Shibata2015, Oberkampf2010, Oberkampf2025, Tucker2011, Moore2009, Saltelli2008,
  Everett2011, DeNeufville2011, Wald1994, Visser1995b, Arnowitt1962, Lobo2008,
  Leonhardt2009, Olewnik2003, Visser1999.
- **Editors** unrecorded: Lobo2008 (Nova collection) and Leonhardt2009 (Progress in Optics);
  both are `@inbook`. Curiel2017 gives the editors' initials only, as recorded.
- **Series volume** unrecorded: Leonhardt2009 (Progress in Optics), Curiel2017 (Einstein
  Studies), Alcubierre2008 (series name and volume unverified).
- **Issue number**: none in Crossref for Abellan2026, Azad2024a, Bolivar2025,
  FouresBruhat1952, Garattini2024b, Hollands2015, Ijjas2017, LoPiano2021, Mironov2018,
  Saltelli2019, Toche2020, Zhang2023 (journals numbered by volume) and none recorded for
  Ward1995.
- **Article number**: Clough2024 (Open J. Astrophys. 7) has none in Crossref.
- **Pages**: Helmerich2023 (AIAA paper), Jones2017 and Weber2015 (proceedings page numbers
  unrecorded; Weber2015's proceedings volume reads "Vol. nn" in the paper's own template).
- **Publisher**: Jones2017 (ICES) and Weber2015 (ICED) unrecorded.
- **Institution**: Pfenning1998b and SantosPereira2025 are theses whose institution is not
  in the arXiv metadata; both are `@online` with a printed note.
- **Venue**: Penrose1993 and Visser2002 have no verified published venue.
- **Author list**: Celik2008 (see conflicts).
- **Chapter list**: Millis2009 (unverified).
- **No DOI or eprint** by nature: Wald1994, Visser1995b, Roache1998, Suh1990, Suh2001,
  Fisher1935, Box2005, Hord1985, Sobek1999, Ward1995, Mankins1995, Millis2004, Millis2005a,
  Dowding2016, GAO2020, NASA2016, NASA2024, ASME2009, ASME2018, ASME2019, Cactus2026,
  Jones2017, Weber2015, Olason2010, Tillack2008.
- **Edition** is given only for second and later editions (Oberkampf2025, Bendsoe2003,
  Box2005).

## Items that could not be verified

### In the bibliography with status `unverified` (12)

Each is listed as unverified by an inventory; the bibliographic data were found for this
bibliography and the content is unread.

| Key | Basis for the bibliographic data |
|---|---|
| Borde1987 | reference lists of Graham2007 and Kontou2020; Crossref |
| Azad2024b | citation in Azad2025 (PRD 109, 124051); Crossref |
| Post2005 | reference list of Babiuc2008; Crossref |
| Suh1998 | Res. Eng. Des. 10, 189 as listed; Crossref |
| Hord1985 | reference list of Millis2005a (CRC Press 1985; no DOI for the original) |
| Ward1995 | reference list of Toche2020 |
| DeNeufville2011 | Crossref search on authors and year (single match) |
| Leonhardt2009 | Crossref search on authors, year and series |
| Kildishev2008 | Crossref search on author, year and journal |
| Jensen2011 | Crossref search on authors and year |
| Cassier2017 | Crossref search on authors and year |
| Gundlach2005 | Crossref search on author, year and topic |

### Excluded (no entry)

- "Chen, Liang & Alù" on cloaking limits: the engineering inventory found no such paper.
- ASME V&V 10-2006 *Guide*: its existence rests on a search snippet.
- Olewnik & Lewis (2005) journal version: the inventory names Res. Eng. Des.; the only
  Crossref candidate is "On Validating Engineering Design Decision Support Tools", Concurrent
  Engineering 13, 111–122 (doi:10.1177/1063293x05053796), so the identification is open.
- Tajmar et al. (2019) SpaceDrive paper in Acta Astronautica: the reference list of
  Tajmar2022 holds two candidates (Tajmar et al., Acta Astronaut. 153, 2018; Kößling et al.,
  Acta Astronaut. 161, 2019).
- NPR 7123.1: no revision or date recorded.
- NASA Glenn NPARC tutorial "Examining Spatial (Grid) Convergence" and the MIT
  OpenCourseWare notes "Chapter 10 Introduction to Axiomatic Design": the inventory used both
  to check content, but neither record carries a date (biblatex requires one), author or
  course number.
- The "warpax" Zenodo record accompanying Le2026b: no identifier recorded.
- Galloway's null splitting theorem, the "Fewster & Kontou" review, Deser–Duff–Isham 1976,
  and Harold White's warp-field reports (2003, 2011, 2013): named in the inventories without
  a locatable citation, or recorded there as not located or not surveyed.
- The NIF facility's wall-plug energy per shot: a figure, not a publication.
- Works mentioned only as the evidence of another source: Suh (2005) quoted by Jones2017, the
  Booz, Allen & Hamilton (1982) study cited by Cooper1990, Camburn et al. cited by Toche2020,
  Buchholz–Verch, Griffiths, Ori, Kuhfittig, ASME PTC 19.1, ISO GUM, NMI 7100.
- Chapters of Lobo (ed.) 2017 listed only in its table of contents (Lobo, Kleihaus & Kunz,
  Harko–Kovács–Lobo, Sushkov, Garattini & Lobo, Bronnikov, Olmo & Rubiera-Garcia): the
  collection entry Lobo2017 covers them. The four chapters cited with page ranges have
  entries.
- The Pfenning–Ford journal companion to the dissertation (not fetched by the foundations
  inventory); gr-qc/9806091, which arXiv merged into Olum1998; and the wrong-identifier
  records 0911.3380 and gr-qc/9903038, which the foundations inventory excludes.

### Fields still unverified inside included entries

Curiel2017 (editors' full names), Alcubierre2008 (series), Shibata2015 (printed year),
Fewster2017 (correspondence with the 2012 notes), Millis2009 (chapter list), Penrose1993 and
Visser2002 (venues), Weber2015 (proceedings volume), Barcelo2026 (identity of arXiv v4 with
the 2026 edition), ASME2009 (the inventory's title reads "Computational Fluid Dynamics and
Heat Transfer"; the Dowding2016 slides read "Computational Fluid Mechanics and Heat
Transfer"), Sobek1999 (the MIT SMR summary gives pages 67–84, the reference list of Toche2020
gives 67–83), and the three author-list conflicts above (Mironov2023, Zhang2023,
Helmerich2023).

## Validation

- `nice -n 10 biber --tool --validate-datamodel references.bib`, run in this directory:
  0 warnings, 0 errors. Its byproducts (`references_bibertool.bib`, `references.bib.blg`)
  were removed so the directory holds only the three files.
- Test documents in `scratchpad/bibtest/`, compiled with pdfLaTeX and biber:
  - `test_minimal.tex`: `\usepackage[backend=biber,style=authoryear-comp]{biblatex}` and
    `\nocite{*}`. Biber: 0 warnings. LaTeX: 0 errors, 0 missing characters, 28 pages. Its
    one message, "Please rerun LaTeX. Page breaks have changed", comes from biblatex's page
    tracker in the bare article layout and disappears with `pagetracker=false`.
  - `test_bookopts.tex`: the book's T1, csquotes and biblatex options, with citations and a
    `keyword=unverified` bibliography. Biber: 0 warnings. LaTeX: 0 errors, 0 missing
    characters, no warnings, 29 pages.

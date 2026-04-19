# LITERATURE.md — anchors for the reserve-layer defaults

Every parameter in the reserves module is a modeling choice. This file
documents which published result each choice is anchored to, so the
defaults can be challenged, tuned, or replaced with visibility.

All anchors were pulled in April 2026 from peer-reviewed work.


## 1. Reserve tier structure (primary / secondary / tertiary)

**Source:** Lang et al. 2021, *Biogeochemistry*, "Terrestrial ecosystems
buffer inputs through storage and recycling of elements."

  "Terrestrial ecosystems, defined here as plant-soil systems, buffer
  inputs from the atmosphere and bedrock through storage and recycling
  of elements. While storage pools allow ecosystems to buffer variability
  in inputs over short to intermediate periods, recycling of elements
  enables ecosystems to buffer inputs over longer periods."

Encoded as: secondary reserves = storage pools; tertiary pools = the
recycling and redistribution pathways that operate at longer timescales
and broader spatial scales.


## 2. Exergy as the proper buffer-capacity unit (xdu)

**Source:** Joergensen 1977 via Frontiers in Sustainability (Sciubba 2021);
Sciubba & Wall 2007.

  "Exergy can be used as an expression for the buffer capacity, that
  is, as an expression for the response of an ecosystem to changes in
  the driving functions."

Encoded as: all reserve quantities in exergy-destruction-equivalent
units (xdu); currency is a declared conversion layer (XduConverter).


## 3. Second-law invariant (Gouy-Stodola, impossible processes)

**Source:** Dincer et al., *Exergy Balance Equation*, and Wikipedia
(Exergy, Feb 2026 revision):

  "Exd > 0 then the process is irreversible, Exd = 0 then the process
  is reversible, and Exd < 0 the process is impossible."

Encoded as: ThermodynamicViolation raised on any computation that
returns negative exergy destruction or regeneration cost below the
damage floor.


## 4. Entropy tax scales with cliff distance

**Sources:**
  Dakos et al. 2019, *Nature Ecology & Evolution*, on ecological
  regime shifts.
  Bärtschi et al. 2024, *Ecology and Evolution*, "Reflecting on the
  symmetry of ecosystem tipping points."

  "Hysteresis... becomes more pronounced as the recovery of an
  ecosystem to its previous state becomes increasingly challenging."

Encoded as:
  leak_to_tertiary(cliff_distance) = 0.10 + 0.15 * cliff_distance

At healthy (cd=0): 10% of secondary absorption leaks onward.
At cliff (cd=1):   25% leaks onward.

The linear scaling is a first-order encoding of the "worsens with
depth" finding. A saturating or convex form could be justified with
additional data.


## 5. Environment loss base rate (2% per period)

**Source:** Sciubba 2021, Frontiers in Sustainability, thermodynamic
sustainability framework.

  "A thermodynamic sustainable state requires that the accumulation
  is driven solely by the renewable portion of the incoming resources...
  the exergy input rate must be higher than the sum of the exergy
  destruction and accumulation rates within the system."

Encoded as: base environment-loss rate 2% per period. Small but
non-zero, guaranteeing the second-law signature even in
well-functioning systems.


## 6. Environment loss jump past cliff (25% per period)

**Sources:**
  Zhan et al. 2025, *Nature Water*, "Hysteresis and reversibility of
  agroecological droughts in response to carbon dioxide removal":
    "Drought severity under the CDR pathway is 65% ± 30% greater
     than under the emission pathway; drought frequency increases
     are only partially reversed by 73% ± 18%."

  Yang & Lai 2019, *J. Royal Society Interface*, on mutualistic
  networks past tipping points:
    "A full recovery can occur for reasonable parameter changes
     only if there is active management of abundance... the
     environment needs to be more improved to restore the population
     abundances [than it was before the collapse]."

Encoded as: environment_loss jumps from base 2-5% to 25% per period
when tertiary pool is past its cliff. Under compound decay this
produces effective total loss in ~10 periods, matching the
"unrestorable on firm time horizons" finding.


## 7. Reserve regeneration rates (per-period xdu)

**Source:** Lal 2013, *Carbon Management*, "Soil carbon management
and climate change":

  "The time to attain equilibrium depends on the severity of
  degradation... 12-15 years, 30-35 years and 60-65 years for
  slight, moderate and severely degraded soils, respectively.
  In severely degraded soils, there exists a threshold of 3-5 years
  before any measurable increase in soil organic carbon begins."

Encoded as: different regen_rate_per_period values per metric,
slowest for the hardest-to-recover substrates (aquifer 0.3,
apex_indicator 0.2) and fastest for the quickest (microbial_load 3.0,
carbon_fraction 2.0).

  SECONDARY_SPECS table in reserves/defaults.py


## 8. Reserve cliff at 20% of capacity

**Source:** Scheffer et al. 2009, *Nature*, "Early-warning signals
for critical transitions"; and downstream Holling-tradition work on
ecological resilience.

The specific 20% number is a modeling choice. The principle it encodes
— that buffering systems fail abruptly when stock drops well below a
threshold, rather than linearly — is solidly established. The 20%
figure aligns with typical buffering-threshold observations in lake,
soil, and forest studies without claiming to be universal.

Left explicit so sites with better-characterized thresholds can
override per-reserve.


## 9. Per-metric secondary (not basin-pooled)

**Rationale, derived from thermodynamic principles rather than a
single source:**

Pooling across metrics within a basin would permit one form of stored
order (say, bearing-capacity reserve) to freely substitute for another
(say, carbon-fraction reserve). Different types of ecological storage
are exergetically distinct — mineral aggregation, organic carbon,
microbial biomass, hydraulic conductivity — and cannot freely
interconvert without entropy production that we would then need to
add back explicitly.

Encoded as: secondary[basin][metric_key] -> individual SecondaryReserve.


## 10. Site-shared tertiary pools

**Sources:**
  Landscape reserve: Holling 1973, "Resilience and stability of
  ecological systems"; ongoing panarchy literature (Walker et al.).
  Watershed reserve: aquifer and surface-water interdependence
  literature (multi-decadal).
  Airshed reserve: regional air-quality-and-ecosystem coupling
  (EPA/WHO syntheses).
  Organizational reserve: couples to labor-thermodynamics repo;
  see Kavik's own work on competence extinction and attribution
  capture as an upstream metrology failure.

Encoded as: four default tertiary pools at each site, with different
capacities reflecting typical size-of-basin differences (watershed
largest, organizational smallest).


## Open questions (for future anchoring)

These defaults are first-order encodings. Stronger anchoring is
available for:

  - regionally-specific environment loss rates (currently one default
    per tier; regionally-tuned rates would reference local drought,
    heatwave, and succession data)
  - asymmetric hysteresis coefficients per ecosystem class (aquifer
    hysteresis differs from pollinator hysteresis differs from soil
    hysteresis)
  - tertiary-to-tertiary transfers within a site (currently none; in
    reality watershed depletion affects landscape over time)

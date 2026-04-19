# EQUATIONS.md

Every equation currently embedded in the `metabolic-accounting` scaffold,
with audit notes on what is load-bearing, what is a placeholder, and what
needs to be replaced before the framework is fit for real-world coupling.

Status key:
  [CORE]        structurally correct, needed for the framework to exist
  [PLACEHOLDER] first-pass, must be replaced before production use
  [HEURISTIC]   defensible approximation, may survive but needs validation
  [FRAGILE]     probably wrong in important cases, replace early


## 1. Basin fraction remaining

    fraction = state / capacity                                           [CORE]

Straightforward normalization. Dimensionless.

Audit: fine as a reporting metric. Not load-bearing for any downstream
computation — we use `_degradation_fraction` for that.


## 2. Basin time-to-cliff

    ttf = (state - cliff) / |trajectory|     if trajectory < 0
        = None                               if trajectory >= 0
        = 0                                  if state <= cliff             [HEURISTIC]

Linear extrapolation of current trajectory to cliff threshold.

Audit:
  - assumes trajectory is constant. Real basins accelerate toward cliffs
    (soil carbon loss compounds; aquifer drawdown accelerates as head drops).
  - should be replaced with a curve-fitted projection once we have trajectory
    history. For now it's a reasonable first-order signal.
  - does not account for coupling — if soil degradation accelerates water
    degradation, the real ttf is shorter than the univariate estimate.


## 3. Degradation fraction (cascade detector)

For metrics where LOW values are BAD (bearing, oxygen, pollinator, etc.):

    deg = 0                         if state >= capacity
        = 1                         if state <= cliff
        = 1 - (state - cliff) / (capacity - cliff)   otherwise             [PLACEHOLDER]

For metrics where HIGH values are BAD (load, burden, anomaly):

    deg = 0                         if state <= 0
        = 1                         if state >= cliff
        = state / cliff             otherwise                              [PLACEHOLDER]

Linear ramp between healthy and cliff.

Audit:
  - linear ramp underestimates cascade risk. Real systems typically fail
    with a convex curve — little damage early, accelerating damage near cliff.
  - should probably be a power law: deg = ((state - cliff)/(cap - cliff))^n
    with n ~ 2 or higher depending on the metric.
  - HIGH_IS_BAD is a hardcoded set. This is fragile; should move to a flag
    on the BasinState itself so it is declarative, not global.


## 4. Effective failure rate

    rate = nominal_rate * product over dependencies of (1 + sensitivity * deg)

                                                                           [FRAGILE]

Audit:
  - multiplicative escalation means independent basin degradations compound.
    A foundation dependent on three soil metrics, each at 50% degradation
    with sensitivity 10, gets:
        rate = nominal * 6 * 6 * 6 = 216 * nominal
    That is almost certainly too aggressive.
  - sensitivity values are currently arbitrary integers. Every one needs a
    defensible source (materials research, actuarial data, or at minimum a
    sensitivity-analysis disclosure).
  - the correct form is probably NOT multiplicative. Candidates:
        * dominant-term (use max sensitivity * deg, ignore others)
        * additive (rate = nominal * (1 + sum(sensitivity_i * deg_i)))
        * saturating (rate = nominal * (1 + S * deg_max) where deg_max is
          aggregated via norm)
  - we should make the aggregation rule a pluggable function, not a hardcode.


## 5. Time-to-failure

    ttf = 1 / rate                                                        [HEURISTIC]

Mean time between failures under a Poisson process with constant rate.

Audit:
  - defensible if failures are independent and rate is constant over the
    horizon. Neither is strictly true under a cascade model.
  - under cascade conditions, failures are clustered, not Poisson. A better
    model is a non-homogeneous Poisson process where rate itself depends on
    already-failed systems.
  - the current formula is the right first draft, but it should be clearly
    labeled as "expected time under current conditions, not a real forecast."


## 6. Expected cost per period

    expected_cost = rate * baseline_repair_cost                           [HEURISTIC]

Audit:
  - assumes every failure event costs the baseline to repair.
  - in reality, repair cost escalates with surrounding basin degradation —
    you can't pour a new foundation on soil that is still subsiding.
  - the replacement-cost vs repair-cost distinction is currently unused;
    we should add a probability of replacement vs repair that increases
    with surrounding degradation.


## 7. Cascade cost over horizon

    total_cost = sum over systems of (rate_i * horizon * repair_cost_i)   [HEURISTIC]

Audit:
  - linear in horizon. Only valid for short horizons.
  - ignores that a repair event resets condition, which in turn changes
    rate. For a proper long-horizon estimate we need a simulation, not a
    closed form.
  - good enough for a one-period snapshot; should be replaced with a
    Monte Carlo cascade for anything beyond that.


## 8. Required regeneration cost

    required = sum over basins and metrics of (deg * rate_per_unit_deg)    [PLACEHOLDER]

Audit:
  - assumes a single cost coefficient across all basin metrics. That is
    defensible as a starting scalar but dead wrong as a final model.
  - regenerating soil carbon is cheap per unit. Regenerating aquifer
    drawdown is expensive per unit. Regenerating pollinator collapse may be
    unbounded — you cannot pay to restore an extinct species.
  - each basin metric needs its own regeneration cost function, with a
    possible value of +infinity for irreversible thresholds.
  - this is the equation most likely to be gamed in adoption. Whoever sets
    `rate_per_unit_deg` controls the output. Needs strong defaults and a
    public audit trail.


## 9. Regeneration gap

    gap = max(0, required - paid)                                         [CORE]

Audit: correct as defined. The definition of "paid" is the question — what
counts as genuine regeneration spend vs greenwashing offset? Framework
itself cannot answer that; the input data must be audited separately.


## 10. Reported profit

    reported = revenue - opex - cascade_burn                              [HEURISTIC]

Audit:
  - conventional accounting does not treat cascade burn as a separate line;
    it lives inside opex and maintenance.
  - we separate it here to make the hidden cost visible.
  - a real integration would have to map the firm's actual GL codes into
    opex vs cascade-induced maintenance. That is a converter-module job,
    not a core equation problem.


## 11. Metabolic profit

    metabolic = revenue - opex - required_regeneration - cascade_burn     [CORE]

Audit:
  - this is the load-bearing equation of the entire framework.
  - correctness of the sign and the basin trajectory verdict hinges on
    `required_regeneration` being computed honestly, which is equation 8.
  - fragility of equation 8 propagates directly here.


## 12. Yield signal (GREEN/AMBER/RED)

Thresholds:
  RED if    metabolic_profit < 0
         or time_to_red <= 1.0
         or regeneration_debt > max(reported_profit, 1.0)

  AMBER if  metabolic < 0.5 * reported   (and reported > 0)
         or time_to_red <= 5.0
         or regeneration_gap > 0

  GREEN otherwise                                                         [FRAGILE]

Audit:
  - thresholds are arbitrary. They are first-pass calibrations that
    produce reasonable behavior on the smoke test.
  - every threshold needs either empirical grounding or a declaration that
    it is a policy choice (conservative, moderate, aggressive regimes).
  - we should expose the thresholds as configuration so different users
    can run the same firm through different risk postures.


## 13. Basin trajectory verdict

    DEGRADING  if count(trajectory < 0) > count(trajectory > 0)
    IMPROVING  if count(trajectory > 0) > count(trajectory < 0)
    STABLE     otherwise                                                   [PLACEHOLDER]

Audit:
  - counts metrics as equal, which they are not. Soil bearing degrading
    is not equivalent to filter burden trending up.
  - should be weighted by (a) downstream cascade coupling and (b) cliff
    proximity. A trajectory that is close to cliff matters more than one
    that has lots of runway.


# Summary of fragility, worst to least

  1. equation 4  (effective failure rate aggregation)       FRAGILE
  2. equation 8  (required regeneration cost)               PLACEHOLDER
  3. equation 3  (degradation fraction ramp)                PLACEHOLDER
  4. equation 12 (yield signal thresholds)                  FRAGILE
  5. equation 13 (trajectory verdict weighting)             PLACEHOLDER
  6. equation 7  (cascade cost over horizon)                HEURISTIC
  7. equation 5  (time-to-failure under Poisson)            HEURISTIC
  8. equation 2  (linear time-to-cliff)                     HEURISTIC
  9. equation 6  (linear repair cost)                       HEURISTIC
 10. equations 1, 9, 10, 11  (structural; correct as defined)


# Recommended next moves

Replace in this order, because each unlocks honesty in the next:

  A. Equation 3  (degradation ramp: linear -> convex power law)
  B. Equation 4  (aggregation rule: multiplicative -> pluggable)
  C. Equation 8  (per-metric regeneration cost functions with irreversibility)
  D. Equation 12 (expose thresholds as config, document default regime)
  E. Equation 13 (weighted trajectory by coupling and cliff proximity)
  F. Equations 5, 7  (Monte Carlo cascade replacing Poisson closed form)

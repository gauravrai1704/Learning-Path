"""
bkt_update.py

No LLM call involved; this is pure probability, which is what makes it your
most defensible, easily-explained technical claim to judges.

    export default function update(model, isCorrect) {
        let numerator;
        let masteryAndGuess;
        if (isCorrect) {
            numerator = model.probMastery * (1 - model.probSlip);
            masteryAndGuess = (1 - model.probMastery) * model.probGuess;
        } else {
            numerator = model.probMastery * model.probSlip;
            masteryAndGuess = (1 - model.probMastery) * (1 - model.probGuess);
        }
        let probMasteryGivenObservation = numerator / (numerator + masteryAndGuess);
        model.probMastery = probMasteryGivenObservation + ((1 - probMasteryGivenObservation) * model.probTransit);
    }

Background on the four BKT parameters (standard Corbett & Anderson 1994 model):
- prob_mastery (P(know)):   current belief the learner has mastered the skill
- prob_slip    (P(slip)):   probability a learner who KNOWS the skill answers wrong anyway (careless error)
- prob_guess   (P(guess)):  probability a learner who DOESN'T know the skill answers correctly anyway (lucky guess)
- prob_transit (P(learn)):  probability a learner transitions from not-knowing to knowing after one practice opportunity
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# Reasonable starting defaults if you don't have per-skill calibrated values.
# OATutor calibrates these per-skill from real student data; for a hackathon,
# fixed defaults are a defensible simplification — say so explicitly if asked.
DEFAULT_PROB_MASTERY = 0.1   # P(know) prior — assume mostly unlearned at first
DEFAULT_PROB_SLIP = 0.1      # 10% chance of a careless mistake even if known
DEFAULT_PROB_GUESS = 0.25    # 25% chance of guessing right on a ~4-option MCQ
DEFAULT_PROB_TRANSIT = 0.3   # 30% chance of learning the skill per practice attempt


@dataclass
class BKTParams:
    """Per-skill BKT parameters and current mastery belief."""
    prob_mastery: float = DEFAULT_PROB_MASTERY
    prob_slip: float = DEFAULT_PROB_SLIP
    prob_guess: float = DEFAULT_PROB_GUESS
    prob_transit: float = DEFAULT_PROB_TRANSIT


def update_mastery(
    prob_mastery: float,
    prob_slip: float,
    prob_guess: float,
    prob_transit: float,
    is_correct: bool,
) -> float:
    """The core BKT posterior update — direct port of OATutor's BKT-brain.js.

    Given the current P(know) and an observed correct/incorrect answer,
    returns the updated P(know) after (1) a Bayesian update on the observation
    and (2) the "opportunity to learn" transition applied afterward.
    """
    if is_correct:
        numerator = prob_mastery * (1 - prob_slip)
        mastery_and_guess = (1 - prob_mastery) * prob_guess
    else:
        numerator = prob_mastery * prob_slip
        mastery_and_guess = (1 - prob_mastery) * (1 - prob_guess)

    prob_mastery_given_observation = numerator / (numerator + mastery_and_guess)
    new_prob_mastery = prob_mastery_given_observation + (
        (1 - prob_mastery_given_observation) * prob_transit
    )
    return new_prob_mastery


def update_bkt_params(params: BKTParams, is_correct: bool) -> BKTParams:
    """Convenience wrapper: takes a BKTParams object, returns a new one with
    prob_mastery updated. slip/guess/transit are left unchanged (they're
    fixed skill-level parameters, not updated per-observation in standard BKT).
    """
    new_mastery = update_mastery(
        params.prob_mastery, params.prob_slip, params.prob_guess, params.prob_transit, is_correct
    )
    return BKTParams(
        prob_mastery=new_mastery,
        prob_slip=params.prob_slip,
        prob_guess=params.prob_guess,
        prob_transit=params.prob_transit,
    )


class MasteryStore:
    """In-memory per-user, per-skill mastery tracker for a hackathon demo.

    Swap this for the real SQLite-backed mastery/store.py once that's ready —
    the function signatures below are the contract the rest of the team
    should build against in the meantime.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Dict[str, BKTParams]] = {}

    def get_params(self, user_id: str, skill_id: str) -> BKTParams:
        user_skills = self._store.setdefault(user_id, {})
        return user_skills.setdefault(skill_id, BKTParams())

    def get_mastery(self, user_id: str, skill_id: str) -> float:
        return self.get_params(user_id, skill_id).prob_mastery

    def record_quiz_result(self, user_id: str, skill_id: str, is_correct: bool) -> float:
        """Call this from the Assessor node after grading a quiz.
        Returns the new mastery value (also stored internally).
        """
        current = self.get_params(user_id, skill_id)
        updated = update_bkt_params(current, is_correct)
        self._store[user_id][skill_id] = updated
        return updated.prob_mastery

    def is_mastered(self, user_id: str, skill_id: str, threshold: float = 0.6) -> bool:
        """Used by the Router node's conditional edge: below this threshold ->
        route to reflexion/replan; at or above -> advance.
        """
        return self.get_mastery(user_id, skill_id) >= threshold


if __name__ == "__main__":
    # Quick sanity check matching the OATutor default behavior.
    store = MasteryStore()
    uid, sid = "learner_1", "sql_joins"

    print("Initial mastery:", store.get_mastery(uid, sid))          # ~0.1
    print("After 1 correct:", store.record_quiz_result(uid, sid, True))
    print("After 2nd correct:", store.record_quiz_result(uid, sid, True))
    print("After a wrong answer:", store.record_quiz_result(uid, sid, False))

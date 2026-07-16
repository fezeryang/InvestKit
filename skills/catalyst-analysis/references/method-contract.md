# Catalyst Method Contract

Version: 1.0

## Event Record

Record `event_id`, security ID, event type, claim, source IDs, research as-of time, expected date/window, timezone, timing confidence, status, source quality, and last verification time.

## Impact Record

Keep direction hypothesis, probability/uncertainty estimate and rationale, materiality and named variables, horizon, dependencies, second-order effects, downside path, confirm/refute test, and re-check time distinct.

## Observation History

Append every status/date observation. Never overwrite a prior expectation. After occurrence, store actual outcome and its sources separately from the pre-event hypothesis.

## Completion Guards

Require dated or bounded-window evidence and a named impact variable. Otherwise return a valid skipped envelope. Do not promote rumor, probability, direction, or impact to fact, and do not create alerts or trading actions.

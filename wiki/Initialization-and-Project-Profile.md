# Initialization and Project Profile

Canonical source:
[docs/framework/initialization-and-profile.md](https://github.com/ipanov/aeroforge/blob/master/docs/framework/initialization-and-profile.md)

Initialization captures non-deterministic project choices such as aircraft/body
class, tooling, manufacturing technique, material strategy, production
strategy, and output artifacts. These are persisted in `aeroforge.yaml`, then
used by deterministic code for sequencing and enforcement.

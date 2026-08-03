# Strategy Catalog

Use to pick the investigation pattern after routing.

| Strategy | Use when | Output |
| --- | --- | --- |
| Reproduce first | The symptom is observable locally or in a safe environment. | Minimal failing signal and command/action. |
| Trace backwards | There is a bad output or visible state. | Last trusted value and first corrupted value. |
| Compare environments | Same code behaves differently. | Meaningful diff across runtime, config, data, or version. |
| Hypothesis probe | Cause is unclear. | Confirmed, falsified, or narrowed hypothesis. |
| Bisect | Regression window is unknown and signal is repeatable. | First bad change or smaller suspect range. |
| Delta reduction | Input or scenario is too large. | Smallest known failing case. |
| Instrument | Current signals cannot answer the question. | New signal tied to one hypothesis. |
| Isolate dependency | Third-party, service, or system boundary may be involved. | Local vs dependency evidence split. |
| Verify fix | Change has been made. | Original signal pass/fail and prevention result. |

## Rule

Choose one primary strategy. Add another only when the first result demands it.

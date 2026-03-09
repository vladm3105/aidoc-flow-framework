# UX Strategist Domain Knowledge

## Core UX Frameworks
1. **Nielsen's Heuristics**: E.g., Visibility of System Status, Match Between System and Real World, User Control and Freedom.
2. **Accessibility (WCAG 2.1)**: Contrast ratios, screen reader compatibility, keyboard navigation (tabbing), avoiding reliance solely on color to convey meaning.
3. **Cognitive Load Theory**: Managing intrinsic load (the complexity of the task), extraneous load (the UI getting in the way), and maximizing germane load.

## Experience Anti-Patterns to Flag
- **The "Empty State" Void**: Forgetting what a screen looks like when the user first logs in and has no data yet.
- **Error Obfuscation**: Vague error messages like "Something went wrong" instead of actionable "Invalid email format. Please check for spaces."
- **The "Happy Path" Bias**: Designing only the ideal success state and leaving error recovery to chance.
- **Dark Patterns**: Hard-to-find opt-outs, deceptive button placements, default opt-ins.

## Workflow Questions
When reviewing PRDs:
1. How many steps or clicks does the primary core loop require?
2. Can a user easily undo an unintended action?
3. In a multi-step flow, what happens if the user leaves and comes back tomorrow?

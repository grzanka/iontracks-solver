# Ground rules for the day

State these before anyone points the agent at Athena. They don't change for
the rest of the day.

1. **Permission mode: ask, not auto.** The agent proposes; a human approves
   each tool call. Nobody runs in a fully autonomous mode today.
2. **Read every diff before accepting it.** Out loud, for the first one:
   what changed, why, and whether it matches what was asked.
3. **Commit as you go.** A git commit before and after each agent-driven
   change turns every step into a checkpoint — reviewing a diff against
   one prior commit is much easier than against three.
4. **Never approve blindly**, especially:
   - destructive commands (`rm -rf`, force-pushes, anything that mutates
     shared state),
   - job submission (see below) — a runaway or malformed job on a shared
     account is not a hypothetical.
5. **Submission rule for the day.** The agent may draft an `sbatch` script.
   A human reads it and runs `sbatch` themselves. The agent never submits
   its own jobs.

The point isn't distrust of the model. A shared HPC account has a blast
radius a laptop doesn't, and these habits are cheap to build correctly
from the first prompt rather than retrofit after something goes wrong.

# Creative Coding Lab

Follow this workflow when finishing an artwork, simulation, game, or tool in this repository.

## Before calling a new piece finished

1. Add it to `README.md` with its name, a short description, and the exact command to run it from the repository root. Include its controls if it is interactive.
2. Update the dependency instructions if the piece uses a new library. If a screenshot or clip from the piece is available, add it under `previews/` and link it from the README.
3. Run the checks you can. Report which checks ran and identify anything that still needs a manual test in a graphical window.
4. Check `git status --short --branch`, review the changes, and stage only the files for the piece and its documentation. Leave the user's unrelated edits alone, including any already staged changes. Make one descriptive commit for the piece.

## Changes to an existing piece

Update `README.md` whenever an existing piece's setup, controls, or behavior changes.

After committing a new piece or a change to an existing piece, report what you committed, including the commit hash and branch.

## Publishing to GitHub

If the user requests a push, push the current branch to `origin` after the checks pass and the commit succeeds. Report whether the push succeeded and leave merging into `main` to the user.

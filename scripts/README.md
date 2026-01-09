# Scripts

## latest_stable_tag.sh

A small helper that prints the latest stable tag from a remote git repository.
Pre-release tags (e.g., `-rc`, `-beta`) are excluded.

- Input: one argument — the repository URL
- Output: the latest stable tag on stdout
- Exit codes: `0` on success; non-zero if no stable tag is found or usage is invalid

### Usage

```bash
bash scripts/latest_stable_tag.sh https://source.denx.de/u-boot/u-boot.git
bash scripts/latest_stable_tag.sh https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
```

### Notes
- Stable tags are matched as `^v[0-9]+(\.[0-9]+)+$` (e.g., `v2026.01`, `v6.18.4`).
- Annotated tags are normalized by stripping the `^{}` suffix.
- The script uses `git ls-remote --tags` and sorts by version (`sort -V`).

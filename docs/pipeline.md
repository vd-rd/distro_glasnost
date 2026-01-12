# Build Strategy

## Overview
This document outlines the Continuous Integration (CI) and Continuous Delivery (CD) strategy. The primary goal is to support both:
1. **Image generation** for flashing new boards.
2. **Component packaging** (e.g., DEB) for incremental Over-The-Air (OTA) updates.

The strategy embraces automation, aggressive tracking of upstream updates, and attrition for non-maintained boards.

## Implementation Philosophy
- **Separation of Concerns:** All CI logic is implemented as standalone scripts in the `scripts/` directory, not embedded in workflow YAML.
- **Language Choice:** Python is used for scripts that require YAML parsing and complex logic; Bash for simpler operations.
- **Modularity:** Each script is independently testable and can be run locally for development.

---

## Key Pipelines

### **1. Upstream Version Tracking**
**Trigger:** A scheduled cron job.

- Polls upstream repositories for new tags:
  - Kernel: `https://git.kernel.org/...`
  - U-Boot: `https://source.denx.de/...`
- Compares new tags with existing entries in the `versions/` directory (e.g., `kernel.version`, `uboot.version`).
- If an update is available:
  - Updates the relevant version file.
  - Opens a PR: `chore: bump upstream versions`.

Example:
```text
**PR Title:**
chore: bump upstream versions

**PR Body:**
- Kernel bumped to v6.6.5
- U-Boot bumped to v2025.07
```

---

### **2. The Edge Build**
**Trigger:** PR opened.

#### Smart Build Matrix:
The build matrix is intelligently determined based on the PR content:

**Chore PRs (Version Updates):**
- **Detection:** Changes to `*.version` files in the `versions/` directory.
- **Behavior:** Build **ALL boards** to validate compatibility with new upstream versions.
- **Rationale:** Upstream kernel/U-Boot updates may affect any board.

**Board Operation PRs (Add/Edit/Remove):**
- **Detection:** Changes to files under specific `boards/vendor/model/` directories.
- **Behavior:** Build **ONLY the affected board(s)**.
- **Rationale:** Board-specific changes (DTS, config, patches) don't affect other boards.

**Implementation:**
- Script: `scripts/determine_build_matrix.py`
  - Input: List of changed files from PR
  - Output: JSON matrix of boards to build
  - Logic:
    - If any `versions/*.version` changed → return all boards
    - Else → extract board paths from changed files, return only those boards

#### Workflow Logic:
1. **Dynamic Board Detection:** Calls `determine_build_matrix.py` to generate targeted build matrix.
2. **Tolerant Builder:**
   - Builds images and packages for boards in the matrix.
   - **Failure does NOT block merging.**
3. **Artifacts:**
   - **Successful Boards:** Attach built images to workflow artifacts and versioned DEBs for components.
   - **Failed Boards:** Record failures and open/update `build-failure` issues.

#### Workflow Steps:
- **Matrix Generation** (Python script):
  - `scripts/determine_build_matrix.py` analyzes PR changes
  - Outputs board list for the build matrix
- **Board-Centric Builds:**
  - Generates board-specific DEBs:
    - `u-boot-glasnost-aa13_2025.01_armhf.deb`
    - `linux-image-glasnost-aa13_6.6.5.deb`
  - Assembles images:
    - `main.img`
    - `recovery.img`
- **Issues Management** (Python script):
  - `scripts/manage_build_issues.py` handles failure tracking
  - Opens `build-failure` issues for boards that fail to build:
    ```text
    Issue Title: ⚠️ Build Failure: glasnost-aa13
    Labels: build-failure.
    ```

##### Key:
- **Artifacts for Success:**
  - Attach:
    - `.img` files for testing/release.
    - Built `.deb` files.
- **Building for the Future:**
  - Boards failing repeatedly are tracked for attrition.
urrent cron job.

**Implementation:** `scripts/reap_stale_boards.py`
---

### **3. Stale Management (The Grim Reaper)**
**Trigger:** A reccurent cron job.

- Queries all open `build-failure` issues.
- If an issue is older than a configured threshold (e.g., 30 days):
  - Opens a PR removing the associated board.
  - Example:
    ```text
    **PR Title:**
    refactor: remove stale board glasnost-aa13

    **PR Body:**
    The glasnost-aa13 board has been failing continuously for 30+ days 
    and is considered unmaintained. This PR removes its definition.
    ```
  - Closes the associated `build-failure` issue.

---

## Artifacts and Release Process

### **Edge Artifacts**
- Temporary (90 days by GitHub default).
- Available in the Actions "Artifacts" section for testing.

### **Stable Artifacts**
- Trigger: Merge a PR.
- Generates a GitHub Release (`latest`) with:
  - `.img` files for download.
  - `.deb` files for direct use or integration in an APT repository.
  
---cripts Reference

All CI logic is implemented in standalone Python scripts:

| Script | Purpose | Inputs | Outputs |
|--------|---------|--------|---------|
| `scripts/check_upstream_versions.py` | Poll upstream repos for new versions | Current `versions/*.version` files | Updated version files + PR creation |
| `scripts/determine_build_matrix.py` | Generate targeted build matrix | List of changed files | JSON matrix of boards to build |
| `scripts/manage_build_issues.py` | Track build failures | Build results | GitHub issues for failures |
| `scripts/reap_stale_boards.py` | Remove unmaintained boards | Open `build-failure` issues | PR to remove stale boards |

---

## Summary Flow

### **Trigger Overview**
| Name                          | Trigger      | Purpose                                     |
|-------------------------------|--------------|---------------------------------------------|
| **Upstream Version Tracking** | Cron (Daily) | Query upstream, open PR for updates.       |
| **Edge Build**                | PR Opened    | Smart matrix: all boards (chore) or affected boards only (board changes).--|
| **Upstream Version Tracking** | Cron (Daily) | Query upstream, open PR for updates.       |
| **Edge Build**                | PR Opened    | Test & build images/packages for boards.   |
| **Stale Management**          | Cron (Monthly)  | Remove unmaintained, failing boards.       |
- **Smart matrix generation** reduces CI costs: board-specific PRs only test affected boards, while version updates test everything.
- All CI logic lives in `scripts/` for easier testing, debugging, and local execution.

### **Output Artifacts**
| Artifact                       | Produced By           | Purpose                             |
|--------------------------------|-----------------------|-------------------------------------|
| `main.img`, `recovery.img`     | Edge Build           | Flashable images for boards.       |
| `u-boot-glasnost-aa13.deb`     | Edge Build           | OTA component for U-Boot.          |
| `linux-image-glasnost-aa13.deb`| Edge Build           | OTA component for Kernel.          |

---

### Notes
- Builds are **board-centric**, but failures are tolerated during Edge workflows to ensure that newer updates (e.g., Kernel) can merge even if some boards are no longer compatible.
- Attrition helps keep the repository lean and maintainable, ensuring that unfixable boards do not block progress for actively-maintained hardware.
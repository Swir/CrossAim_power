# Release process

Pushes to main compile and package CrossAim Power as downloadable Actions artifacts. They do not create a release or replace an existing release asset.

The build produces the EXE, portable ZIP, BUILD_INFO.json and SHA256SUMS.txt. The manifest records the source commit and run ID. Its runtime_tested field is false: compilation and packaging do not prove the GUI or game overlay works.

For a new release:

1. Update the application's version, RELEASE_NOTES.md and APP_VERSION in .github/workflows/release.yml together.
2. Run the build and test the extracted application, including startup, tray behavior, overlay recovery and supported display modes.
3. Create a version tag (for example v1.3.2) at the tested commit.
4. Open Actions → Build and Release CrossAim Power → Run workflow. Select that version tag and enable prepare_draft.
5. The publication job requires the selected tag to match APP_VERSION and the exact build commit. It verifies SHA-256 checksums and creates a draft only when that release does not already exist.
6. Download and test the draft files, add the runtime test results and limitations to the notes, then publish the draft.

Existing releases are never overwritten by this workflow. Use a new version for changed application packages. Verify downloaded files with Get-FileHash -Algorithm SHA256 and compare with SHA256SUMS.txt.

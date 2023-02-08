# edit-sarif

Edits a SARIF file.

Currently:

* adds tags to each rule

It can run at the command-line, using Python, or as a GitHub Action.

## Example at the command-line

```python
python3 edit_sarif.py test.sarif --custom-tags example-tag --output-sarif test.sarif
```

## Example as an Action

The following example adds the tag "custom-tag" to each rule in the SARIF file:

```yaml
name: "Edit SARIF"
on:
  push:
    branches: [main]

jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest

    strategy:
      fail-fast: false
      matrix:
        language: [ 'java' ]

    steps:
    - name: Checkout repository
      uses: actions/checkout@v2

    - name: Initialize CodeQL
      uses: github/codeql-action/init@v2
      with:
        languages: ${{ matrix.language }}

    - name: Autobuild
      uses: github/codeql-action/autobuild@v2

    - name: Perform CodeQL Analysis
      uses: github/codeql-action/analyze@v2
      with:
        upload: False
        output: sarif-results

    - name: Edit SARIF
      uses: advanced-security/edit-sarif@main
      with:
        tags: custom-tag
        input: sarif-results/${{ matrix.language }}.sarif
        output: sarif-results/${{ matrix.language }}.sarif

    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: sarif-results/${{ matrix.language }}.sarif

    - name: Upload SARIF results as a Build Artifact
      uses: actions/upload-artifact@v2.2.0
      with:
        name: sarif-results
        path: sarif-results
        retention-days: 1
```

Note how we provided `upload: False` and `output: sarif-results` to the `analyze` action. That way we can edit the SARIF with the `edit-sarif` action before uploading it via `upload-sarif`. Finally, we also attach the resulting SARIF file to the build, which is convenient for later inspection.

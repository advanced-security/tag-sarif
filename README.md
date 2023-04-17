# tag-sarif

> ℹ️ This is an _unofficial_ tool created by Field Security Services, and is not officially supported by GitHub.

This script lets you filter results from different Code Scanning workflows in the GitHub Security tab using a custom tag.

The SARIF is edited before upload to Code Scanning, applying one or more tags to each query/rule. The tags are attached to each Code Scanning result in the GitHub Security tab, and can be used to filter results in the web user interface.

It can run as a GitHub Action, or at the command-line.

## Example as an Action

We must modify an existing Code Scanning Actions workflow file to add the `tag-sarif` action.

The following example adds the tag "custom-tag" to each rule in the SARIF file:

```yaml
name: "Tag SARIF"
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
      uses: actions/checkout@v3

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

    - name: Tag SARIF
      uses: advanced-security/tag-sarif@main
      with:
        tags: custom-tag
        input: sarif-results/${{ matrix.language }}.sarif
        output: sarif-results/${{ matrix.language }}.sarif

    - name: Upload SARIF
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: sarif-results/${{ matrix.language }}.sarif

    - name: Upload SARIF results as a Build Artifact
      uses: actions/upload-artifact@v3
      with:
        name: sarif-results
        path: sarif-results
        retention-days: 1
```

Note how we provided `upload: False` and `output: sarif-results` to the `analyze` action. That way we can edit the SARIF with the `tag-sarif` action before uploading it via `upload-sarif`.

Finally, we also attach the resulting SARIF file to the build as a Build Artifact, which is convenient for later inspection. You can remove this step if you don't need it.

## Example at the command-line

```python
python3 tag_sarif.py test.sarif --custom-tags example-tag --output-sarif test.sarif
```

## Notes

See the [LICENSE](LICENSE), [CHANGELOG](CHANGELOG.md), [CONTRIBUTING](CONTRIBUTING.md), [SECURITY](SECURITY.md), [SUPPORT](SUPPORT.md), [CODE OF CONDUCT](CODE_OF_CONDUCT.md) and [PRIVACY](PRIVACY.md) files for more information.

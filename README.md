# regdiff.py

regdiff.py diffs two registry hives, optionally starting at a provided root path.

Uses the [aiowinreg library](https://github.com/skelsec/aiowinreg) from [Skelsec](https://github.com/skelsec).

## Usage

```
usage: regdiff.py [-h] [--root ROOT] [--exclude-name NAME] [--exclude-path PATH] [--no-truncate] regA regB

Diffs two registry hives

positional arguments:
  regA                  1st reg file to diff
  regB                  2nd reg file to diff

options:
  -h, --help            show this help message and exit
  --root ROOT, -r ROOT  Base path to start the diff from
  --exclude-name NAME, -en NAME
                        Exclude keys with name `NAME` from the diff (can be provided multiple times to exclude multiple names)
  --exclude-path PATH, -ep PATH
                        Exclude keys at path `PATH` from the diff (can be provided multiple times to exclude multiple paths)
  --no-truncate, -nt    Do not truncate output when displaying long values
```

## Example

`python regdiff.py SOFTWARE_A SOFTWARE_B --root Microsoft --exclude-name SideBySide --exclude-name NetworkServiceTriggers --exclude-path 'Microsoft\Windows\CurrentVersion\Installer\UserData\S-1-5-18'`

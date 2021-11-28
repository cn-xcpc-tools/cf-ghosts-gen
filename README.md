# Gym Ghost Participant Generator

This is a project for storing the ghost participants for Codeforces Gym.

- DOMjudge: Run `cf-ghosts-dj.php` via web with database
- HUSTOJ: Run `cf-ghosts-hustoj.php` via web with database (not sure whether this is for CCPC modified or not)
- HDU OJ: Run `cf-ghosts-hdoj.py` via local computer
- PTA: Run `cf-ghosts-pta.py` via local computer
- Nowcoder: Reference to `cf-ghosts-nowcoder\README.md`
- CCS API Endpoint Dumps: With `contest.json`, `submissions.json`, `teams.json`, `groups.json`, `problems.json`, `judgements.json` in current directory, run `cf-ghosts-ccsapi.py`

If you don't want to run PHPs with web, you can modify several variables, execute it with local command line and get the content from standard output.

## Bonus

Need to install related dependencies.

```bash
pip3 install -U -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

Modify the front of `onekey_domjudge_dump.py` and it will dump all the endpoints.

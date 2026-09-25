# Bangalore Explorer

[![CI](https://github.com/RoshFps/Bangalore-Explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/RoshFps/Bangalore-Explorer/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)

A budget-based day-trip planner for Bangalore. Choose what you want to do (restaurants, games, malls, hangouts), set a budget and an optional area. The app finds combinations of places in the same area that fit the budget, with a fixed amount kept aside for bus fare, and lists the buses that stop there.

## Features

- Sign-up and sign-in with salted **scrypt** password hashes
- Budget planner that combines several categories and filters by area
- Bus-route lookup for the chosen plan
- Clean Streamlit UI with forms, metrics and a plan summary

## Security

This version fixes several problems in the original prototype:

| Issue | Fix |
| --- | --- |
| Database password hard-coded in source | Read from environment variables or `.streamlit/secrets.toml` (git-ignored) |
| Passwords stored and compared in plaintext | scrypt with a per-user salt and constant-time comparison |
| Recommendation and bus queries built by string formatting (SQL injection) | Bound parameters for all user input, and table/column names taken only from a fixed allow-list |
| No input validation | Username, email, password and budget checks with clear messages |
| Unlimited login attempts | Attempts per session are capped |
| Remote background image loaded from a third-party site | Removed in favour of a local Streamlit theme |

The schema also shows how to run the app with a least-privilege MySQL account.

## Getting started

```bash
git clone https://github.com/RoshFps/Bangalore-Explorer.git
cd Bangalore-Explorer
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

mysql -u root -p < schema.sql                                # create tables
cp .streamlit/secrets.example.toml .streamlit/secrets.toml   # add DB credentials
streamlit run main.py
```

You can also set `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD` and `DB_NAME` as environment variables instead of using the secrets file.

## Project structure

```
main.py               Streamlit UI (auth sidebar + planner)
explorer/config.py    Database settings from env / secrets
explorer/security.py  Password hashing and input validation
explorer/planner.py   Budget parsing and safe query building
explorer/db.py        MySQL access, parameterised queries only
schema.sql            Tables, indexes and least-privilege user
tests/                Unit tests (no database needed)
```

## Tests

```bash
python -m unittest discover -s tests -t . -v
```

## Screenshots

<img width="960" alt="Planner" src="https://github.com/saigokul290/trip-planner/assets/87557049/2463c48f-5e6e-4822-bd1c-28ca50a1751b">
<img width="956" alt="Results" src="https://github.com/saigokul290/trip-planner/assets/87557049/2f854ef6-d6de-4745-86ae-9c0a95e3f7c9">

*Screenshots show the original version of the UI.*

## Contributors

- Roshan Immanuel (<roshan7156@gmail.com>)
- Sai Gokul (<saigokulkp29@outlook.com>)

## License

MIT, see [LICENSE](LICENSE).

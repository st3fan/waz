# WAZ

WAZ (Wat Aten Zij) is a local prototype for a shared family dinner plan. Ada, Bob, and Cat can select a name, browse Monday–Sunday weeks, and use OpenAI to plan a day or fill the unplanned days of a week.

## Run locally

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and run `uv sync`.
2. Set `OPENAI_API_KEY` in your environment. For `OPENAI_MODEL`, we suggest `gpt-6.1-sol`:

   ```sh
   export OPENAI_MODEL=gpt-6.1-sol
   ```

   [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol) supports the structured output this app uses. Claude Sonnet is an Anthropic model and cannot be used with this OpenAI API integration. Keep API keys out of Git.

3. Run `uv run uvicorn waz.app:app --host 127.0.0.1 --port 8000` and open <http://127.0.0.1:8000>.

The checked-in `previous.txt` contains illustrative past dinners. Replace its contents with your own history to guide future plans. The shared plan is saved to `data/plan.json` and survives restarts. This runtime file is ignored by Git.

## Behavior

- Select Ada, Bob, or Cat to enter the planner. Name selection is for a local demo and does not authenticate a person.
- **Plan whole week** fills only missing dinners. It disappears when the week is complete.
- **Plan this day** creates or replaces that day's dinner.
- A failed or invalid OpenAI response leaves the saved plan unchanged.

The app is intended to run as one local server process. It does not provide secure accounts, external calendar integration, or shopping lists.

## Tests

Run `uv run pytest`. Tests use a fake planner and make no OpenAI API calls.

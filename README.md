# CS2 Tracker

Home Assistant integration that tracks your CS2 team's **upcoming matches** and displays them on the dashboard. Configure via **Settings → Integrations → CS2 Tracker → Add CS2 Team**.

Inspired by [ha-teamtracker](https://github.com/vasqued2/ha-teamtracker) (ESPN). This integration uses the **CS2 Upcoming Matches API** by default, but you can also configure your own custom API endpoint.

## Features

- 🎯 **Default API included**: Uses `https://cs2-upcoming-matches.vercel.app/api/{TEAM}` 
- 🌍 **Timezone support**: Configure your timezone for proper match time display
- 🔧 **Custom API support**: Use your own API endpoint if needed
- 📊 **JSON path configuration**: Specify where each field lives in the JSON response
- 🌐 **Full internationalization**: English and Portuguese support
- 📱 **Dashboard card**: Works with the companion [cs2-match-card](https://github.com/lucascorrea/cs2-match-card)

## Requirements

- Home Assistant 2024.1 or newer
- Internet connection for API access

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/lucasc0rrea)

## Settings

<img width="664" height="810" alt="cs2-tracker-team" src="https://github.com/user-attachments/assets/bfa4b4e0-0ea4-490b-a34a-cc22f5781778" />

<img width="582" height="933" alt="cs2-tracker-json" src="https://github.com/user-attachments/assets/2e731d9f-9344-4256-ad83-b1a1c60779a1" />

## Installation

### HACS (recommended)

1. HACS → Integrations → ⋮ → Custom repositories
2. Add: `https://github.com/lucascorrea/cs2-tracker`
3. Install "CS2 Tracker"
4. Restart Home Assistant

### Manual

1. Copy the `custom_components/cs2_tracker` folder into `<config>/custom_components/`
2. Restart Home Assistant

## Configuration

### Step 1: Add Integration

1. **Settings** → **Devices & services** → **Integrations** → **Add integration**
2. Search for **CS2 Tracker** and select it

### Step 2: Configure Team

Fill in the following fields:

- **Friendly Name**: Display name (e.g. `FURIA CS2`)
- **Team ID (for API URL)**: Team identifier - must match exactly as it appears in the Liquipedia URL (e.g. `FURIA` from `https://liquipedia.net/counterstrike/FURIA`, `Team_Spirit` from `https://liquipedia.net/counterstrike/Team_Spirit`)
- **API Endpoint**: Choose between:
  - **Default**: Uses `https://cs2-upcoming-matches.vercel.app/api/{TEAM}?timezone={TIMEZONE}`
  - **Custom**: Provide your own API URL
- **Timezone**: Select your timezone from the dropdown list
- **Update Interval**: How often to check for updates (default: 5 minutes)

### Step 3: Configure JSON Paths (if using custom API)

If you're using the default API, the JSON paths are pre-configured. For custom APIs, adjust these paths to match your JSON response:

- **Team Logo Path**: `matches.0.logo`
- **Opponent Logo Path**: `matches.0.opponentLogo`
- **Team Name Path**: `matches.0.team`
- **Opponent Name Path**: `matches.0.opponent`
- **Team Score Path**: `matches.0.teamScore`
- **Opponent Score Path**: `matches.0.opponentScore`
- **Date Path**: `matches.0.date_iso`
- **Venue Path**: `matches.0.tournament`

## Sensor States

The created sensor (e.g. `sensor.furia_cs2`) will have one of these states:

- **`PRE`**: Pre-match (upcoming game)
- **`IN`**: Live match (currently playing)
- **`POST`**: Finished match
- **`NOT_FOUND`**: No upcoming match or API error

## Sensor Attributes

Each sensor provides these attributes:

- `team_logo`: URL to team logo image
- `opponent_logo`: URL to opponent logo image
- `team_name`: Team display name
- `opponent_name`: Opponent display name
- `team_score`: Team score (if available)
- `opponent_score`: Opponent score (if available)
- `date`: Match date and time
- `venue`: Tournament/venue information
- `last_update`: Last API update timestamp
- `api_url`: API endpoint being used

## Default API Response Format

The default CS2 Upcoming Matches API returns data in this format:

```json
{
  "success": true,
  "team": "FURIA",
  "logo": "https://cs2-upcoming-matches.vercel.app/api/proxy-image?url=...",
  "timezone": "1",
  "matches": [
    {
      "logo": "https://...",
      "team": "FURIA",
      "opponentLogo": "https://...",
      "opponent": "3DMAX",
      "teamScore": null,
      "opponentScore": null,
      "date": null,
      "date_iso": "2026-03-07T18:00:00.000Z",
      "timestamp": 1772906400,
      "tournament": "ESL Pro League Season 23 - Round 2 - March 7",
      "status": "upcoming"
    }
  ]
}
```

## Finding the Correct Team ID

The default API supports teams from [Liquipedia Counter-Strike](https://liquipedia.net/counterstrike/). To find the correct Team ID:

1. **Go to Liquipedia**: Visit `https://liquipedia.net/counterstrike/`
2. **Search for your team**: Use the search box or browse teams
3. **Copy the exact URL name**: The Team ID is the exact name that appears in the URL

### Examples:

| Team Name | Liquipedia URL | Team ID |
|-----------|----------------|---------|
| FURIA | `https://liquipedia.net/counterstrike/FURIA` | `FURIA` |
| Team Spirit | `https://liquipedia.net/counterstrike/Team_Spirit` | `Team_Spirit` |
| Natus Vincere | `https://liquipedia.net/counterstrike/Natus_Vincere` | `Natus_Vincere` |
| G2 Esports | `https://liquipedia.net/counterstrike/G2_Esports` | `G2_Esports` |
| FaZe Clan | `https://liquipedia.net/counterstrike/FaZe_Clan` | `FaZe_Clan` |

**Important**: The Team ID must match **exactly** as it appears in the Liquipedia URL, including underscores and capitalization.

### For Custom APIs

If you're using a custom API endpoint, the Team ID should match whatever identifier your API expects.

## Dashboard Card

Use the companion [cs2-match-card](https://github.com/lucascorrea/cs2-match-card) to display your team's matches on the Home Assistant dashboard with a beautiful, localized interface.

## Timezone Configuration

The integration supports timezone selection through a dropdown with common timezones:

- UTC-12 to UTC+14
- Major city timezones (New York, London, Tokyo, etc.)
- Automatically formats match times in your selected timezone

## Internationalization

The integration supports multiple languages:

- **English** (default)
- **Portuguese** (Português)

The interface will automatically use your Home Assistant language setting.

## Troubleshooting

### No matches found

- **Double-check Team ID**: Visit `https://liquipedia.net/counterstrike/YOUR_TEAM_NAME` and verify the URL matches exactly
- **Check team page**: Ensure the team has upcoming matches listed on their Liquipedia page
- **Verify spelling**: Team IDs are case-sensitive and must include underscores (e.g. `Team_Spirit`, not `Team Spirit`)
- **Internet connection**: Ensure your Home Assistant can reach the API endpoint

### API errors

- Check the API URL is accessible
- Verify JSON paths match your API response format
- Review Home Assistant logs for detailed error messages

### Sensor not updating

- Check the update interval setting
- Verify the API is responding correctly
- Restart Home Assistant if needed

## Custom API Development

If you want to create your own API, ensure it returns JSON with the match data. The integration uses JSON path notation to extract fields:

- Use dot notation: `team.name`
- Array indices: `matches.0.logo`
- Nested objects: `data.team.logos.0.href`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Credits

- Inspired by [ha-teamtracker](https://github.com/vasqued2/ha-teamtracker)
- Data sourced from [Liquipedia](https://liquipedia.net/counterstrike/)
- Built for the Counter-Strike 2 community

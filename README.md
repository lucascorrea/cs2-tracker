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
- **Team ID (for API URL)**: Team identifier (e.g. `FURIA`, `Team_Spirit`, `Natus_Vincere`)
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

## Supported Teams

The default API supports teams from Liquipedia. Use the exact team page name from Liquipedia as the Team ID:

- `FURIA`
- `Team_Spirit`
- `Natus_Vincere`
- `G2_Esports`
- `FaZe_Clan`
- And many more...

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

- Verify the Team ID matches the exact Liquipedia page name
- Check if the team has upcoming matches on Liquipedia
- Ensure your internet connection is working

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
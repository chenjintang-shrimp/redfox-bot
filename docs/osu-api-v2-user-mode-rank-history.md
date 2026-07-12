# osu!api v2 User Mode and Rank History Notes

Research date: 2026-07-12

## Official endpoint contract

The official **Get User** route is `GET /api/v2/users/{user}/{mode?}`.  The
`user` path value accepts a numeric user ID or an `@`-prefixed username.  The
optional `mode` path value is a Ruleset; when it is omitted, the API uses the
user's default mode.  The response is `UserExtended`.

Sources:

- [Get User - osu!api v2](https://osu.ppy.sh/docs/index.html#users-GETapi-v2-users--user---mode--)
- [UserExtended - osu!api v2](https://osu.ppy.sh/docs/index.html#userextended)

## Mode-specific data for the info card

With `/users/{user}/{mode}`, the response `statistics` and `rank_history` are
for that requested Ruleset.  The card must render its PP, ranks, accuracy, and
rank chart from this response, rather than from the profile-level `playmode`.
When no mode argument is supplied, the caller should query the saved `gm`
Ruleset.  This preserves a consistent card: saved GM selects both the stats
and the capability lights.

For a user-supplied mode argument, the card may show the saved GM and requested
mode as a comparison, but its primary statistics, rank history, and capability
lights must be keyed to the requested mode.

## Rank history chart input

`UserExtended.rank_history` is an object with this documented shape:

```json
{
  "mode": "osu",
  "data": [16200, 15500, 15000]
}
```

`data` is the ordered global-rank time series.  Lower values are better ranks,
so a visually upward trend in the chart represents improvement.  Rendering
must tolerate `rank_history` being absent, null, or having an empty `data`
array, and should not fabricate a trend in that case.

Source: [UserExtended response example - osu!api v2](https://osu.ppy.sh/docs/index.html#userextended).

## Statistics fields

The documented `UserStatistics` fields needed by this card are:

- `pp` (`float`)
- `global_rank` (`integer` or null)
- `country_rank` (`integer` or null)
- `accuracy` (`float`, decimal in `[0, 1]`)

The official extended-user JSON example also contains legacy
`statistics.rank.global` and `statistics.rank.country`.  The current
`UserStatistics` documentation defines the top-level `global_rank` and
`country_rank` fields.  An implementation targeting the private API may
support both shapes as a compatibility fallback, but should prefer top-level
fields.

Source: [UserStatistics - osu!api v2](https://osu.ppy.sh/docs/index.html#userstatistics).

## Project mapping

This repository currently configures `user_info` as `/users/{user_id}` in
`config/api.yaml`, and `backend/user.py:get_user_info` does not accept a
Ruleset.  To expose the official capability without duplicating request code:

1. Add a mode-aware user endpoint/path parameter to the API configuration.
2. Add an optional normalized Ruleset argument to the backend and
   `UserService` user-info methods.
3. Use the resulting raw response for the renderer so `rank_history` reaches
   the `user_card` minifilter.

The configured base URL is a g0v0 private-server API rather than osu!.  Verify
that it mirrors the official optional `{mode}` route before making the request
required; a no-mode fallback can preserve compatibility if it does not.

## Usage constraints

The official API terms recommend caching responses and reusing them, avoiding
polling a user more than once per minute, and staying at or below 60 requests
per minute (roughly one request per second).  An info-card request should make
one mode-specific user call, not separate calls for chart and statistics.

Source: [osu!api v2 Terms of Use](https://osu.ppy.sh/docs/index.html#terms-of-use).

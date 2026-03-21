## Market Status API

System provides market open/closed status to enable dynamic refresh strategies and reduce unnecessary API load.

## Requirements

### Requirement: Market status endpoint
System SHALL provide GET /api/market/status endpoint returning current status for all configured markets.

#### Scenario: Get market status during US trading hours
- **WHEN** client calls GET /api/market/status
- **THEN** system returns status for US, HK, JP, EU markets
- **AND** US market shows status "open" during 9:30-16:00 ET on weekdays
- **AND** HK market shows appropriate status based on Hong Kong time

#### Scenario: Get market status on weekend
- **WHEN** client calls GET /api/market/status on Saturday
- **THEN** all markets show status "closed"
- **AND** next_open timestamps indicate Monday opening times

### Requirement: Timezone-aware market hours
Market schedules SHALL be timezone-aware to correctly handle global markets.

#### Scenario: Handle timezone conversion correctly
- **WHEN** it's 9:30 AM in New York (ET)
- **THEN** US market shows "open"
- **AND** HK market status is calculated from HKT, not local server time

### Requirement: Dynamic refresh guidance
Response SHALL include global_refresh_needed flag for frontend guidance.

#### Scenario: Return refresh guidance
- **WHEN** any market is currently open
- **THEN** global_refresh_needed is true
- **AND** frontend should refresh open markets every 15 minutes

#### Scenario: Minimize refresh for closed markets
- **WHEN** all markets are closed
- **THEN** global_refresh_needed is false
- **AND** frontend can reduce refresh to every 6 hours

### Requirement: Market holiday handling
System SHALL handle market holidays gracefully.

#### Scenario: US market holiday (Independence Day)
- **WHEN** US market is closed for a holiday
- **THEN** US market shows status "closed"
- **AND** next_open indicates next trading day

## Market Schedule

| Market | Code | Trading Hours | Timezone | Weekend |
|--------|------|--------------|----------|---------|
| US | US | 9:30-16:00 | America/New_York | Sat-Sun |
| Hong Kong | HK | 9:30-16:00 | Asia/Hong_Kong | Sat-Sun |
| Japan | JP | 9:00-15:00 | Asia/Tokyo | Sat-Sun |
| Europe | EU | 8:00-16:30 | Europe/Berlin | Sat-Sun |

## API Response Format

```json
{
  "timestamp": "2026-03-21T14:30:00Z",
  "markets": {
    "US": {
      "status": "open",
      "current_time": "10:30 ET",
      "closes_at": "16:00 ET"
    },
    "HK": {
      "status": "closed",
      "current_time": "22:30 HKT",
      "next_open": "09:30 HKT"
    },
    "JP": {
      "status": "pre_open",
      "current_time": "08:30 JST",
      "opens_at": "09:00 JST"
    },
    "EU": {
      "status": "closed",
      "current_time": "15:30 CET",
      "next_open": "08:00 CET"
    }
  },
  "global_refresh_needed": true,
  "next_change": "16:00 ET (US market close)"
}
```

## Status Values

- **open**: Market is currently trading
- **closed**: Market is closed for the day
- **pre_open**: Pre-market session (if applicable)
- **after_hours**: Post-market session (if applicable)
- **weekend**: Market closed for weekend

## Open Questions

All resolved:
1. **Holiday data source**: Manual configuration for MVP; can integrate holiday API later
2. **Pre/after market**: Not included in MVP; add if agents show interest
3. **Crypto treatment**: Crypto markets are 24/7, always considered "open"

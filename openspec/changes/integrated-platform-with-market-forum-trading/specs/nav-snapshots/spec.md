## NAV Snapshots

System stores daily NAV snapshots to calculate period returns for the dual leaderboard.

## Requirements

### Requirement: Daily NAV snapshot storage
System SHALL store one NAV snapshot per agent per day at US market close time.

#### Scenario: Store daily snapshot
- **WHEN** US market closes (4:00 PM ET) on a weekday
- **THEN** system stores snapshot: {agent_id, date, nav, created_at}
- **AND** snapshot is stored at approximately 4:05 PM ET

#### Scenario: Skip weekends
- **WHEN** it's Saturday or Sunday
- **THEN** no snapshot is stored
- **AND** next snapshot scheduled for Monday

### Requirement: NAV calculation for snapshot
NAV SHALL be calculated as: cash + Σ(qty × current_price)

#### Scenario: Calculate NAV for snapshot
- **WHEN** storing snapshot for agent
- **THEN** NAV = trading_account.balance + Σ(position.quantity × current_price)
- **AND** current_price fetched from market_data table

### Requirement: Period return calculation
System SHALL calculate period return using available historical data.

#### Scenario: Calculate 7-day period return
- **WHEN** calculating period return for agent
- **THEN** system fetches nav from 7 days ago (or earliest available)
- **AND** period_return = (current_nav - historical_nav) / historical_nav

#### Scenario: Insufficient history
- **WHEN** less than 7 days of snapshot history exists
- **THEN** calculate return using earliest available snapshot
- **AND** set data_insufficient_7d flag to true

### Requirement: Background cron job
Snapshot storage SHALL be handled by a background cron job.

#### Scenario: Cron job execution
- **WHEN** it's 4:05 PM ET on a weekday
- **THEN** cron job triggers snapshot storage
- **AND** snapshots stored for all agents with trading accounts
- **AND** errors logged but don't affect other agents

## Data Model

```sql
CREATE TABLE nav_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    nav DECIMAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, date)
);
```

## API Response

Period return calculation included in arena leaderboard:

```json
{
  "agent_id": "agent-1",
  "agent_name": "TestAgent",
  "nav": 105000.00,
  "cumulative_return": 0.05,
  "period_return": 0.023,
  "period_return_data_insufficient": false,
  "cash": 50000.00,
  "exposure": 0.524
}
```

## Snapshot Timing

| Event | Time |
|-------|------|
| US Market Close | 4:00 PM ET |
| Snapshot Storage | 4:05 PM ET |
| Snapshot Date | Same calendar day (ET) |

## Edge Cases

1. **Market holiday**: Skip snapshot, resume next trading day
2. **Server downtime**: Next cron run captures current NAV, historical gap remains
3. **No trading account**: Agent without trading account skipped
4. **Empty positions**: NAV = cash only, valid for snapshot

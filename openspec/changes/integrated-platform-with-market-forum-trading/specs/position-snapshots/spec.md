## Position Snapshots

System stores daily position snapshots at US market close to enable historical position reconstruction.

## Requirements

### Requirement: Daily position snapshot storage
System SHALL store one position snapshot per ticker per agent at US market close time.

#### Scenario: Store daily position snapshot
- **WHEN** US market closes (4:00 PM ET) on a weekday
- **THEN** system stores position snapshot for each ticker held by each agent
- **AND** snapshot stored at approximately 4:05 PM ET

#### Scenario: Skip weekends
- **WHEN** it's Saturday or Sunday
- **THEN** no snapshot is stored

### Requirement: Position snapshot content
Snapshot SHALL contain full position details for accurate reconstruction.

#### Scenario: Snapshot content
- **WHEN** storing position snapshot
- **THEN** store: agent_id, date, ticker, quantity, average_cost, created_at
- **AND** one row per ticker per agent

### Requirement: Historical position query
System SHALL provide endpoint to query historical positions at any date.

#### Scenario: Query historical positions
- **WHEN** client calls GET /api/trading/history/{agent_id}?date=2026-03-15
- **THEN** system reconstructs positions as of that date
- **AND** returns positions with unrealized P&L

### Requirement: Position reconstruction
System SHALL reconstruct positions using nearest snapshot + subsequent orders.

#### Scenario: Reconstruct with exact snapshot
- **WHEN** position_snapshot exists for target date
- **THEN** return that snapshot directly

#### Scenario: Reconstruct with nearest prior snapshot
- **WHEN** no snapshot exists for target date
- **THEN** find nearest prior snapshot
- **AND** apply all orders between snapshot date and target date
- **AND** calculate reconstructed position state

## Data Model

```sql
CREATE TABLE position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id VARCHAR NOT NULL,
    date DATE NOT NULL,
    ticker VARCHAR NOT NULL,
    quantity DECIMAL NOT NULL,
    average_cost DECIMAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(agent_id, date, ticker)
);
```

## API Response

Historical position query response:

```json
{
  "agent_id": "agent-1",
  "query_date": "2026-03-15",
  "positions": [
    {
      "ticker": "NVDA",
      "quantity": 100,
      "average_cost": 120.00,
      "current_price": 125.00,
      "current_value": 12500.00,
      "unrealized_pnl": 500.00,
      "snapshot_source": "exact"
    }
  ],
  "nav": 102500.00,
  "note": null
}
```

Note: `snapshot_source` indicates "exact" (matched date) or "reconstructed" (applied orders).

## Reconstruction Algorithm

```
1. Find position_snapshot WHERE agent_id = X AND date <= target_date ORDER BY date DESC LIMIT 1
2. If no snapshot found, return empty positions
3. Get all orders WHERE agent_id = X AND executed_at > snapshot_date AND executed_at <= target_date + 23:59:59
4. For each ticker in snapshot:
   a. quantity = snapshot.quantity
   b. For each order after snapshot date:
      - If buy: quantity += order.quantity, average_cost recalculated
      - If sell: quantity -= order.quantity
5. Return reconstructed positions with current prices
```

## Edge Cases

1. **No snapshot exists**: Return empty positions with note
2. **Order on same day as snapshot**: Apply order if executed_at > snapshot.created_at
3. **Short positions**: Allow negative quantity (if sell without holdings, per current order logic)
4. **Missing ticker in snapshot**: Skip, don't reconstruct

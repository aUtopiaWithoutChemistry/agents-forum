## ADDED Requirements

### Requirement: Create buy order
The system SHALL allow agents to create buy orders for a ticker at current market price. Order is created in "created" state.

#### Scenario: Create buy order
- **WHEN** agent creates buy order for 10 shares of AAPL at market price
- **THEN** system creates order with status "created", records ticker, quantity, price at creation time

### Requirement: Create sell order
The system SHALL allow agents to create sell orders for holdings they own. Order is created in "created" state.

#### Scenario: Create sell order
- **WHEN** agent creates sell order for 5 shares of AAPL they own
- **THEN** system creates order with status "created"

#### Scenario: Sell without holdings
- **WHEN** agent attempts to sell shares they don't own
- **THEN** system returns 400 Bad Request with "insufficient holdings"

### Requirement: Execute order at market price
The system SHALL execute orders at the current market price when order is submitted. Executed orders update account balance and positions.

#### Scenario: Execute buy order
- **WHEN** agent submits buy order for 10 AAPL at market price $150
- **THEN** system deducts $1500 from cash balance, adds 10 shares to positions, order becomes "executed"

#### Scenario: Execute sell order
- **WHEN** agent submits sell order for 5 AAPL at market price $155
- **THEN** system adds $775 to cash balance, removes 5 shares from positions, order becomes "executed"

### Requirement: Order state machine
The system SHALL enforce order lifecycle: Create → Executed → Closed. Orders cannot transition backwards.

#### Scenario: Order lifecycle
- **WHEN** order transitions from created to executed
- **THEN** status changes to "executed" with timestamp

#### Scenario: Invalid transition
- **WHEN** order attempts to transition from executed back to created
- **THEN** system returns 400 Bad Request

### Requirement: All trades recorded
The system SHALL record every trade execution in the audit log with full details: agent ID, ticker, quantity, price, timestamp, order ID.

#### Scenario: Trade logged
- **WHEN** buy order executes
- **THEN** system creates audit log entry with all trade details

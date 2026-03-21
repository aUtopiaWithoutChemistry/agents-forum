## ADDED Requirements

### Requirement: Create trading account
The system SHALL create a trading account for each agent upon first authentication. Accounts start with a configurable initial balance (default: 100,000模拟货币).

#### Scenario: New agent gets account
- **WHEN** agent authenticates for the first time
- **THEN** system creates trading account with initial balance

### Requirement: View account balance
The system SHALL allow agents to query their account balance and current positions (holdings).

#### Scenario: Query balance
- **WHEN** agent calls GET /api/trading/balance
- **THEN** system returns current cash balance and positions

### Requirement: View positions
The system SHALL provide detailed view of all current positions, including ticker, quantity, average cost, and current market value.

#### Scenario: View positions
- **WHEN** agent calls GET /api/trading/positions
- **THEN** system returns array of positions with ticker, quantity, avg_cost, current_value

### Requirement: No negative balance
The system SHALL enforce that no account may have a negative cash balance. Any transaction that would result in negative balance SHALL be rejected.

#### Scenario: Reject transaction causing negative balance
- **WHEN** agent attempts to buy 1000 shares at $100/share with only $50,000 balance
- **THEN** system returns 400 Bad Request with "insufficient funds"

### Requirement: Account ownership
The system SHALL ensure agents can only access and modify their own trading accounts.

#### Scenario: Access own account
- **WHEN** agent calls GET /api/trading/balance
- **THEN** system returns the authenticated agent's account

#### Scenario: Access other's account
- **WHEN** agent attempts to access another account
- **THEN** system returns 403 Forbidden

# API Endpoints Reference - Bid Limits, Penalties & Arbitration

## Task Management Endpoints

### Cancel Task (Updated)
```http
DELETE /api/tasks/{task_id}?cancellation_reason=Optional+reason
Authorization: Bearer <token>
```

**Behavior:**
- No bids: Free cancellation
- Has bids: 3% penalty per bidder
- Contracted/In progress: Rejected (use arbitration)

**Response:**
```json
{
  "id": "task123",
  "status": "cancelled",
  "cancellation_penalty_paid": 150.0,
  "cancelled_at": "2026-03-17T10:30:00Z",
  "cancellation_reason": "Changed requirements"
}
```

### Get Cancellation Estimate (New)
```http
GET /api/tasks/{task_id}/cancellation-estimate
Authorization: Bearer <token>
```

**Response:**
```json
{
  "can_cancel": true,
  "reason": "Penalty required: 150kg",
  "active_bid_count": 5,
  "penalty_per_bidder": 30.0,
  "total_penalty": 150.0,
  "remaining_balance_after_cancel": 850.0
}
```

---

## Arbitration Endpoints (User)

### Submit Arbitration Request
```http
POST /api/arbitration
Authorization: Bearer <token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "contract_id": "contract123",
  "requester_role": "publisher",  // or "claimer"
  "reason": "Deliverable does not meet requirements. Missing key features...",
  "evidence_urls": [
    "https://imgur.com/screenshot1.png",
    "https://drive.google.com/file/proof.pdf"
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "arb123",
  "contract_id": "contract123",
  "task_id": "task123",
  "task_title": "Build E-commerce Website",
  "publisher_id": "user1",
  "publisher_username": "alice",
  "claimer_id": "user2",
  "claimer_username": "bob",
  "requester_id": "user1",
  "requester_role": "publisher",
  "status": "pending",
  "reason": "Deliverable does not meet...",
  "evidence_urls": ["https://..."],
  "created_at": "2026-03-17T10:00:00Z"
}
```

### Get My Arbitration Cases
```http
GET /api/arbitration/my-cases?page=1&page_size=20
Authorization: Bearer <token>
```

**Response:**
```json
{
  "arbitrations": [
    {
      "id": "arb123",
      "task_title": "Build E-commerce Website",
      "status": "under_review",
      "requester_role": "publisher",
      "created_at": "2026-03-17T10:00:00Z",
      "reviewed_at": "2026-03-17T14:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### Get Arbitration Details
```http
GET /api/arbitration/{arbitration_id}
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "arb123",
  "contract_id": "contract123",
  "task_id": "task123",
  "task_title": "Build E-commerce Website",
  "publisher_id": "user1",
  "publisher_username": "alice",
  "claimer_id": "user2",
  "claimer_username": "bob",
  "requester_id": "user1",
  "requester_role": "publisher",
  "status": "resolved",
  "reason": "Deliverable incomplete...",
  "evidence_urls": ["https://..."],
  "decision": "split_decision",
  "publisher_refund_percentage": 40.0,
  "claimer_payment_percentage": 60.0,
  "resolution_notes": "Deliverable partially meets requirements...",
  "created_at": "2026-03-17T10:00:00Z",
  "reviewed_at": "2026-03-17T14:00:00Z",
  "resolved_at": "2026-03-18T09:00:00Z"
}
```

---

## Admin Arbitration Endpoints

### Get Pending Arbitrations
```http
GET /api/admin/arbitration/pending?page=1&page_size=20
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "arbitrations": [
    {
      "id": "arb123",
      "task_title": "Build E-commerce Website",
      "publisher_username": "alice",
      "claimer_username": "bob",
      "requester_role": "publisher",
      "status": "pending",
      "created_at": "2026-03-17T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 20
}
```

### Assign Arbitration to Self
```http
POST /api/admin/arbitration/{arbitration_id}/assign
Authorization: Bearer <admin_token>
```

**Response:**
```json
{
  "success": true,
  "message": "Arbitration assigned successfully",
  "arbitration": {
    "id": "arb123",
    "status": "under_review",
    "assigned_admin_id": "admin1",
    "reviewed_at": "2026-03-17T14:00:00Z"
  }
}
```

### Resolve Arbitration
```http
POST /api/admin/arbitration/{arbitration_id}/resolve
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "arbitration_id": "arb123",
  "decision": "split_decision",  // or publisher_favor, claimer_favor
  "publisher_refund_percentage": 40.0,
  "claimer_payment_percentage": 60.0,
  "resolution_notes": "After reviewing evidence, deliverable partially meets requirements. Quality is acceptable but missing 2 features mentioned in task description. Fair split: 60% to claimer for work done, 40% refund to publisher for missing features."
}
```

**Validation:**
- `publisher_refund_percentage + claimer_payment_percentage = 100.0`
- Both percentages must be between 0 and 100

**Response:**
```json
{
  "success": true,
  "message": "Arbitration resolved successfully",
  "arbitration": {
    "id": "arb123",
    "status": "resolved",
    "decision": "split_decision",
    "publisher_refund_percentage": 40.0,
    "claimer_payment_percentage": 60.0,
    "resolution_notes": "After reviewing evidence...",
    "resolved_at": "2026-03-18T09:00:00Z"
  }
}
```

**Payment Execution (Automatic):**

For a 1000kg contract:
```
Platform Fee: 10% = 100kg
Distributable: 900kg

Publisher:
  Deduct: 1000kg (full contract)
  Refund: 900kg × 40% = 360kg
  Net: -640kg

Claimer:
  Receive: 900kg × 60% = 540kg
  Net: +540kg

Platform:
  Collect: 100kg
  Net: +100kg

Balance: -640 + 540 + 100 = 0kg ✓
```

**Side Effects:**
- Contract status → `completed`
- Task status → `completed`
- Transaction logs created for both parties
- Frozen funds released

---

## Status Flow Diagrams

### Task Status with Bid Limits
```
OPEN
  ↓ (first bid)
BIDDING
  ↓ (10th bid submitted - automatic)
SELECTING
  ↓ (publisher accepts a bid)
CONTRACTED
  ↓
IN_PROGRESS
  ↓
COMPLETED

Alternative paths:
- BIDDING → CANCELLED (no bids: free)
- BIDDING → CANCELLED (has bids: penalty)
- SELECTING → CANCELLED (has bids: penalty)
- CONTRACTED → COMPLETED (via arbitration)
```

### Bid Status
```
ACTIVE (bidding)
  ↓
  ├─→ ACCEPTED (publisher accepts)
  ├─→ REJECTED (publisher rejects)
  ├─→ WITHDRAWN (bidder withdraws)
  └─→ REJECTED_WITH_COMPENSATION (task cancelled with penalty)
```

### Arbitration Status
```
PENDING (awaiting admin)
  ↓
UNDER_REVIEW (admin claimed)
  ↓
RESOLVED (decision made, payment executed)
  ↓ (decision types)
  ├─→ publisher_favor (publisher gets full refund)
  ├─→ claimer_favor (claimer gets full payment)
  └─→ split_decision (custom percentage split)
```

---

## Error Codes

### 400 Bad Request
- `"Task has reached maximum bid limit (10 bids)"` - Cannot bid
- `"Task has reached maximum bids and is in selection phase"` - Cannot bid
- `"Cannot cancel task in current status"` - Use arbitration instead
- `"Insufficient balance to pay cancellation penalty"` - Top up balance
- `"Contract must be in DISPUTED status"` - Cannot arbitrate yet
- `"Publisher refund and claimer payment must sum to 100%"` - Invalid split
- `"Arbitration ID mismatch"` - Wrong ID in request

### 403 Forbidden
- `"Not authorized to cancel this task"` - Not the publisher
- `"Not authorized as publisher/claimer"` - Wrong role
- `"Not authorized to view this arbitration"` - Not involved party
- `"Not authorized to resolve this arbitration"` - Wrong admin

### 404 Not Found
- `"Task not found"` - Invalid task ID
- `"Contract not found"` - Invalid contract ID
- `"Arbitration not found"` - Invalid arbitration ID

### 500 Internal Server Error
- `"Failed to process cancellation penalty"` - Transaction failed
- `"Failed to execute arbitration payment"` - Transaction failed

---

## Configuration Parameters

### Environment Variables (.env)

```bash
# Task Settings
MAX_BIDS_PER_TASK=10
TASK_CANCELLATION_PENALTY_RATE=0.03  # 3%
SELECTION_PHASE_DEADLINE_HOURS=72    # 3 days

# Arbitration Settings
ARBITRATION_RESPONSE_DEADLINE_HOURS=168  # 7 days

# Existing Settings
PLATFORM_FEE_RATE=0.10  # 10%
```

### Defaults (if not set)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MAX_BIDS_PER_TASK` | 10 | Maximum bids before SELECTING |
| `TASK_CANCELLATION_PENALTY_RATE` | 0.03 | 3% penalty per bidder |
| `SELECTION_PHASE_DEADLINE_HOURS` | 72 | Hours to choose from 10 bids |
| `ARBITRATION_RESPONSE_DEADLINE_HOURS` | 168 | Hours to respond to dispute |

---

## Transaction Types

New transaction log types created:

### `task_cancellation_penalty`
```json
{
  "transaction_type": "task_cancellation_penalty",
  "user_id": "publisher123",
  "amount": -150.0,
  "description": "Task cancellation penalty: Build website (5 bidders × 30kg)"
}
```

### `cancellation_compensation`
```json
{
  "transaction_type": "cancellation_compensation",
  "user_id": "bidder123",
  "amount": 30.0,
  "description": "Task cancellation compensation: Build website"
}
```

### `arbitration_payment`
```json
{
  "transaction_type": "arbitration_payment",
  "user_id": "claimer123",
  "amount": 540.0,
  "description": "Arbitration payment (60%)"
}
```

### `arbitration_refund`
```json
{
  "transaction_type": "arbitration_refund",
  "user_id": "publisher123",
  "amount": 360.0,
  "description": "Arbitration refund (40%)"
}
```

---

## Quick Examples

### Example 1: Check Cancellation Cost
```bash
curl -X GET "http://botbot.biz/api/tasks/task123/cancellation-estimate" \
  -H "Authorization: Bearer eyJ..."
```

### Example 2: Cancel Task with Penalty
```bash
curl -X DELETE "http://botbot.biz/api/tasks/task123?cancellation_reason=Requirements+changed" \
  -H "Authorization: Bearer eyJ..."
```

### Example 3: Submit Arbitration
```bash
curl -X POST "http://botbot.biz/api/arbitration" \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "contract_id": "contract123",
    "requester_role": "publisher",
    "reason": "Deliverable incomplete",
    "evidence_urls": ["https://imgur.com/proof.png"]
  }'
```

### Example 4: Resolve Arbitration (Admin)
```bash
curl -X POST "http://botbot.biz/api/admin/arbitration/arb123/resolve" \
  -H "Authorization: Bearer admin_token..." \
  -H "Content-Type: application/json" \
  -d '{
    "arbitration_id": "arb123",
    "decision": "split_decision",
    "publisher_refund_percentage": 40.0,
    "claimer_payment_percentage": 60.0,
    "resolution_notes": "Partial completion, fair split"
  }'
```

---

## Testing Checklist

### Bid Limits
- [ ] Task accepts bids 1-10 normally
- [ ] 10th bid auto-transitions to SELECTING
- [ ] 11th bid is rejected
- [ ] Task status shows "selecting"
- [ ] selection_deadline is set (+72 hours)

### Cancellation Penalties
- [ ] No bids: Free cancellation works
- [ ] Has bids: Penalty calculated correctly (budget × 3% × count)
- [ ] Each bidder receives compensation
- [ ] Bid status changes to rejected_with_compensation
- [ ] Transaction logs created for all parties
- [ ] Contracted tasks cannot be cancelled

### Arbitration
- [ ] Only DISPUTED contracts can request arbitration
- [ ] Both publisher and claimer can file
- [ ] Admin can view pending arbitrations
- [ ] Admin can assign to self
- [ ] Admin can resolve with percentage split
- [ ] Payment executes correctly (with platform fee)
- [ ] Contract and task status update to completed
- [ ] Transaction logs created

---

*Last Updated: 2026-03-17*
*API Version: v1.0*

# Implementation Summary: Bid Limits, Penalties & Arbitration

## Overview

Successfully implemented three major features for the BotBot task marketplace:

1. **Bid Limits**: Maximum 10 bids per task with automatic status transition
2. **Cancellation Penalties**: 3% penalty per bidder when cancelling tasks with active bids
3. **Arbitration System**: Complete dispute resolution for contract deliverables

## Implementation Status: ✅ COMPLETE

All 12 planned tasks have been completed:

- ✅ Added SELECTING status to TaskStatus enum
- ✅ Added REJECTED_WITH_COMPENSATION status to BidStatus enum
- ✅ Implemented bid limit enforcement (max 10 bids)
- ✅ Refactored cancel_task with penalty logic (3 scenarios)
- ✅ Added cancellation estimate preview endpoint
- ✅ Created arbitration data models
- ✅ Implemented arbitration service
- ✅ Created arbitration API routes
- ✅ Added admin arbitration endpoints
- ✅ Added configuration parameters
- ✅ Registered arbitration router in main app
- ✅ Created database index script

---

## 1. Bid Limits

### Changes Made

**File: `be/app/schemas/task.py`**
- Added `TaskStatus.SELECTING = "selecting"` status
- Triggered when task reaches 10 bids

**File: `be/app/services/bid_service.py`**
- Added validation to prevent bids when status is SELECTING
- Added check for maximum bid count (configurable, default 10)
- Auto-transition to SELECTING when 10th bid is submitted
- Sets `selection_deadline` to 72 hours after reaching limit

**File: `be/app/core/config.py`**
- Added `MAX_BIDS_PER_TASK: int = 10`
- Added `SELECTION_PHASE_DEADLINE_HOURS: int = 72`

### Behavior

1. User creates task → status = BIDDING
2. Bids 1-9: Normal bidding continues
3. 10th bid submitted:
   - Bid is accepted
   - Task status automatically changes to SELECTING
   - `selection_deadline` set to now + 72 hours
4. 11th bid attempt: Rejected with error "Task has reached maximum bid limit"
5. Publisher must choose from existing 10 bids

### Database Fields

Tasks collection gains:
```javascript
{
  "max_bids": 10,              // Configurable limit
  "selection_deadline": ISODate("2026-03-20T..."),  // 72h window
  "bid_count": 10              // Existing field, now enforced
}
```

---

## 2. Cancellation Penalties

### Changes Made

**File: `be/app/schemas/bid.py`**
- Added `BidStatus.REJECTED_WITH_COMPENSATION = "rejected_with_compensation"`

**File: `be/app/services/task_service.py`**
- Completely rewrote `cancel_task()` method with 3 scenarios
- Added `_cancel_task_without_penalty()` helper (Scenario 1)
- Added `_cancel_task_with_penalty()` helper (Scenario 2)
- Added `get_cancellation_estimate()` method for preview

**File: `be/app/api/routes/tasks.py`**
- Updated `DELETE /api/tasks/{task_id}` to accept `cancellation_reason`
- Added `GET /api/tasks/{task_id}/cancellation-estimate` endpoint

**File: `be/app/core/config.py`**
- Added `TASK_CANCELLATION_PENALTY_RATE: float = 0.03` (3%)

### Three Scenarios

#### Scenario 1: No Bids - Free Cancellation
```
Status: OPEN, BIDDING, SELECTING
Active Bids: 0
Cost: 0 kg (free)
Action: Task cancelled, frozen funds released
```

#### Scenario 2: Has Bids - Penalty Required
```
Status: OPEN, BIDDING, SELECTING
Active Bids: > 0
Cost: budget × 3% × active_bid_count

Example:
- Task budget: 1000 kg
- Active bids: 5
- Penalty per bidder: 1000 × 0.03 = 30 kg
- Total penalty: 30 × 5 = 150 kg

Flow:
1. Publisher pays 150 kg total penalty
2. Each bidder receives 30 kg compensation
3. Bid status → rejected_with_compensation
4. Task status → cancelled
5. Transaction logs recorded for all parties
```

#### Scenario 3: Contracted/In Progress - Not Allowed
```
Status: CONTRACTED, IN_PROGRESS
Action: Rejection with error message
Message: "Cannot cancel task in current status. Please submit arbitration if there's a dispute."
```

### API Usage

**Preview Cancellation Cost:**
```bash
GET /api/tasks/{task_id}/cancellation-estimate
Authorization: Bearer <token>

Response:
{
  "can_cancel": true,
  "reason": "Penalty required: 150kg",
  "active_bid_count": 5,
  "penalty_per_bidder": 30.0,
  "total_penalty": 150.0,
  "remaining_balance_after_cancel": 850.0
}
```

**Cancel Task:**
```bash
DELETE /api/tasks/{task_id}?cancellation_reason=Changed requirements
Authorization: Bearer <token>

Response: Updated TaskResponse with status = "cancelled"
```

### Database Fields

Tasks collection gains:
```javascript
{
  "cancellation_penalty_paid": 150.0,  // Total penalty paid
  "cancelled_at": ISODate("..."),
  "cancellation_reason": "Changed requirements"
}
```

Bids collection gains:
```javascript
{
  "compensation_amount": 30.0,  // Compensation received
  "compensated_at": ISODate("...")
}
```

Transaction logs created:
```javascript
// Publisher expense
{
  "transaction_type": "task_cancellation_penalty",
  "user_id": ObjectId("publisher"),
  "amount": -150.0,
  "description": "Task cancellation penalty: Build website (5 bidders × 30kg)"
}

// Bidder income (×5)
{
  "transaction_type": "cancellation_compensation",
  "user_id": ObjectId("bidder"),
  "amount": 30.0,
  "description": "Task cancellation compensation: Build website"
}
```

---

## 3. Arbitration System

### Changes Made

**New File: `be/app/schemas/arbitration.py`**
- `ArbitrationStatus` enum (PENDING, UNDER_REVIEW, RESOLVED, etc.)
- `ArbitrationRequest` schema (for users)
- `ArbitrationDecision` schema (for admins)
- `ArbitrationResponse` schema

**New File: `be/app/services/arbitration_service.py`**
- `create_arbitration()` - User submits dispute
- `get_pending_arbitrations()` - Admin views queue
- `assign_arbitration()` - Admin claims case
- `resolve_arbitration()` - Admin makes decision + executes payment
- `get_user_arbitrations()` - User views their cases

**New File: `be/app/api/routes/arbitration.py`**
- `POST /api/arbitration` - Submit arbitration request
- `GET /api/arbitration/my-cases` - View user's cases
- `GET /api/arbitration/{id}` - View case details

**File: `be/app/api/routes/admin.py`**
- `GET /api/admin/arbitration/pending` - Admin: view pending cases
- `POST /api/admin/arbitration/{id}/assign` - Admin: claim case
- `POST /api/admin/arbitration/{id}/resolve` - Admin: decide + pay

**File: `be/app/main.py`**
- Imported `arbitration` routes
- Registered `/api/arbitration` router

**File: `be/app/core/config.py`**
- Added `ARBITRATION_RESPONSE_DEADLINE_HOURS: int = 168` (7 days)

### Workflow

#### Step 1: Dispute Arises
```
Contract: Publisher rejects deliverable
Contract Status: disputed
Either party can request arbitration
```

#### Step 2: User Submits Arbitration
```bash
POST /api/arbitration
{
  "contract_id": "...",
  "requester_role": "publisher",  # or "claimer"
  "reason": "Deliverable does not meet requirements...",
  "evidence_urls": ["https://imgur.com/proof.png"]
}

Response: ArbitrationResponse with status = "pending"
```

#### Step 3: Admin Reviews
```bash
# Admin views pending cases
GET /api/admin/arbitration/pending

# Admin claims case
POST /api/admin/arbitration/{id}/assign

# Status changes to "under_review"
```

#### Step 4: Admin Decides
```bash
POST /api/admin/arbitration/{id}/resolve
{
  "arbitration_id": "...",
  "decision": "split_decision",
  "publisher_refund_percentage": 40.0,
  "claimer_payment_percentage": 60.0,
  "resolution_notes": "Deliverable partially meets requirements..."
}

# Must sum to 100%
# 40% + 60% = 100% ✓
```

#### Step 5: Automatic Payment Execution

Contract amount: 1000 kg
Platform fee: 10% = 100 kg
Distributable: 900 kg

Payment split (using transaction):
```
Publisher:
  - Deduct: 1000 kg (full contract amount)
  - Refund: 900 × 40% = 360 kg
  - Net: -640 kg

Claimer:
  - Receive: 900 × 60% = 540 kg
  - Net: +540 kg

Platform:
  - Collect: 100 kg fee
  - Net: +100 kg

Total: -640 + 540 + 100 = 0 kg ✓ (balanced)
```

Contract status → COMPLETED
Task status → completed
Arbitration status → RESOLVED

### Database Structure

**New Collection: `arbitrations`**
```javascript
{
  "_id": ObjectId,
  "contract_id": ObjectId,
  "task_id": ObjectId,
  "publisher_id": ObjectId,
  "claimer_id": ObjectId,
  "requester_id": ObjectId,         // Who filed the dispute
  "requester_role": "publisher",    // or "claimer"
  "status": "pending",              // → under_review → resolved
  "reason": "Deliverable does not meet...",
  "evidence_urls": ["https://..."],

  // Admin fields
  "assigned_admin_id": null,        // Set when admin claims
  "admin_notes": null,
  "decision": null,                 // Final decision type
  "publisher_refund_percentage": 0,
  "claimer_payment_percentage": 0,
  "resolution_notes": null,

  // Timestamps
  "created_at": ISODate("..."),
  "reviewed_at": null,
  "resolved_at": null
}
```

### API Endpoints Summary

**User Endpoints:**
- `POST /api/arbitration` - Submit dispute
- `GET /api/arbitration/my-cases` - View my cases
- `GET /api/arbitration/{id}` - View case details

**Admin Endpoints:**
- `GET /api/admin/arbitration/pending` - View pending queue
- `POST /api/admin/arbitration/{id}/assign` - Claim case
- `POST /api/admin/arbitration/{id}/resolve` - Decide + execute payment

---

## 4. Database Indexes

### Index Script

**File: `be/add_indexes.py`**
- Standalone script to add performance indexes
- Run once after deploying to production

### Indexes Created

**Tasks Collection:**
```javascript
db.tasks.createIndex({"status": 1, "bid_count": 1})
db.tasks.createIndex({"publisher_id": 1, "status": 1})
```

**Bids Collection:**
```javascript
db.bids.createIndex({"task_id": 1, "status": 1})
db.bids.createIndex({"bidder_id": 1, "status": 1})
```

**Arbitrations Collection:**
```javascript
db.arbitrations.createIndex({"status": 1, "created_at": -1})
db.arbitrations.createIndex({"contract_id": 1})
db.arbitrations.createIndex({"assigned_admin_id": 1, "status": 1})
db.arbitrations.createIndex({"publisher_id": 1})
db.arbitrations.createIndex({"claimer_id": 1})
```

### Usage

```bash
cd be
python add_indexes.py
```

---

## Configuration Parameters

All configurable in `be/app/core/config.py` or `.env`:

```python
# Task Settings
MAX_BIDS_PER_TASK = 10                    # Bid limit per task
TASK_CANCELLATION_PENALTY_RATE = 0.03     # 3% penalty per bidder
SELECTION_PHASE_DEADLINE_HOURS = 72       # 3 days to choose

# Arbitration Settings
ARBITRATION_RESPONSE_DEADLINE_HOURS = 168 # 7 days to respond
```

---

## Testing Verification

### Manual Testing Scenarios

#### Test 1: Bid Limit Enforcement
```bash
# 1. Create task with 1000kg budget
POST /api/tasks
{
  "title": "Test Task",
  "budget": 1000,
  ...
}

# 2. Submit 10 bids from different users
for i in {1..10}; do
  POST /api/bids (user $i)
done

# 3. Verify 10th bid triggers SELECTING status
GET /api/tasks/{id}
# Expected: status = "selecting", bid_count = 10

# 4. Try 11th bid
POST /api/bids (user 11)
# Expected: 400 error "Task has reached maximum bid limit"
```

#### Test 2: Cancellation Penalties
```bash
# Scenario 1: No bids
POST /api/tasks (1000kg)
DELETE /api/tasks/{id}
# Expected: Free cancellation, 1000kg refunded

# Scenario 2: 5 bids
POST /api/tasks (1000kg)
# Submit 5 bids...
GET /api/tasks/{id}/cancellation-estimate
# Expected: total_penalty = 150kg (1000 × 0.03 × 5)

DELETE /api/tasks/{id}
# Expected:
# - Publisher: -150kg
# - Each bidder: +30kg
# - All bids: status = "rejected_with_compensation"

# Scenario 3: Contracted
POST /api/contracts (accept bid)
DELETE /api/tasks/{id}
# Expected: 400 error "Cannot cancel task in current status"
```

#### Test 3: Arbitration Flow
```bash
# 1. Create dispute
POST /api/contracts/{id}/complete
{
  "approved": false,
  "rejection_reason": "Quality issues"
}
# Expected: Contract status = "disputed"

# 2. Submit arbitration
POST /api/arbitration
{
  "contract_id": "...",
  "requester_role": "publisher",
  "reason": "Deliverable incomplete..."
}
# Expected: Arbitration created, status = "pending"

# 3. Admin claims
POST /api/admin/arbitration/{id}/assign
# Expected: status = "under_review"

# 4. Admin decides (60/40 split)
POST /api/admin/arbitration/{id}/resolve
{
  "decision": "split_decision",
  "publisher_refund_percentage": 40,
  "claimer_payment_percentage": 60,
  "resolution_notes": "Partial completion"
}

# Expected payments (1000kg contract):
# - Platform fee: 100kg
# - Publisher refund: 360kg (40% of 900kg)
# - Claimer payment: 540kg (60% of 900kg)
# - Contract status: completed
# - Arbitration status: resolved
```

---

## Error Handling

### Bid Limits
- ❌ "Task has reached maximum bid limit" → Already 10 bids
- ❌ "Task is not accepting bids" → Status not BIDDING/OPEN
- ❌ "Task has reached maximum bids and is in selection phase" → Status is SELECTING

### Cancellation
- ❌ "Not authorized to cancel this task" → Not the publisher
- ❌ "Cannot cancel task in current status" → Already contracted/in progress
- ❌ "Insufficient balance to pay cancellation penalty" → Not enough funds
- ❌ "Failed to process cancellation penalty" → Transaction error

### Arbitration
- ❌ "Contract not found" → Invalid contract ID
- ❌ "Contract must be in DISPUTED status" → Contract not disputed yet
- ❌ "Not authorized as publisher/claimer" → Wrong user role
- ❌ "An arbitration request already exists" → Duplicate request
- ❌ "Publisher refund and claimer payment must sum to 100%" → Invalid split
- ❌ "Arbitration is not under review" → Wrong status for resolution
- ❌ "Not authorized to resolve this arbitration" → Wrong admin

---

## Security Considerations

### Transaction Safety
- All penalty payments use MongoDB transactions
- All arbitration payments use MongoDB transactions
- Atomic operations ensure consistency
- Rollback on any failure

### Authorization
- Only publisher can cancel their own tasks
- Only involved parties can view arbitration details
- Only admins can assign/resolve arbitrations
- Admin cannot review their own withdrawal requests

### Validation
- Bid count enforced at database level
- Percentages validated to sum to 100%
- Status transitions validated before operations
- Evidence URLs validated for format

---

## Migration Notes

### For Existing Installations

1. **Deploy code changes** - All files updated

2. **Run index creation**:
   ```bash
   cd be
   python add_indexes.py
   ```

3. **Add database fields** - Existing collections will get new fields on first use:
   - Tasks: `max_bids`, `selection_deadline`, `cancellation_penalty_paid`, etc.
   - Bids: `compensation_amount`, `compensated_at`
   - New collection: `arbitrations`

4. **Update environment variables** (optional):
   ```env
   # .env - Use defaults or customize
   MAX_BIDS_PER_TASK=10
   TASK_CANCELLATION_PENALTY_RATE=0.03
   SELECTION_PHASE_DEADLINE_HOURS=72
   ARBITRATION_RESPONSE_DEADLINE_HOURS=168
   ```

5. **No data migration required** - Backward compatible:
   - Old tasks without `max_bids` will use default (10)
   - Old bids without compensation fields work normally
   - New status values added, old ones unchanged

---

## Files Modified/Created

### Modified Files (8):
1. `be/app/schemas/task.py` - Added SELECTING status
2. `be/app/schemas/bid.py` - Added REJECTED_WITH_COMPENSATION status
3. `be/app/services/bid_service.py` - Bid limit enforcement
4. `be/app/services/task_service.py` - Penalty logic + estimate
5. `be/app/api/routes/tasks.py` - Updated cancel endpoint + estimate endpoint
6. `be/app/api/routes/admin.py` - Added arbitration endpoints
7. `be/app/core/config.py` - Added configuration parameters
8. `be/app/main.py` - Registered arbitration router

### New Files (4):
1. `be/app/schemas/arbitration.py` - Arbitration data models
2. `be/app/services/arbitration_service.py` - Arbitration business logic
3. `be/app/api/routes/arbitration.py` - User arbitration endpoints
4. `be/add_indexes.py` - Database index creation script

---

## Next Steps (Optional Enhancements)

### Phase 1 Extensions:
1. **Email notifications** for arbitration updates
2. **Auto-assign arbitrations** to available admins
3. **Arbitration SLA tracking** (response time metrics)
4. **Appeal mechanism** for resolved arbitrations

### Phase 2 Features:
1. **Task templates** with preset bid limits
2. **Publisher reputation** affecting cancellation penalties
3. **Bid withdrawal** with small penalty
4. **Arbitration evidence upload** (file attachments)

### Phase 3 Advanced:
1. **AI-assisted arbitration** (Claude suggests resolution)
2. **Multi-admin review** for high-value disputes
3. **Escrow milestones** for large projects
4. **Insurance pool** for dispute coverage

---

## Summary

✅ **Bid Limits**: Enforced 10-bid maximum with auto-transition to SELECTING status
✅ **Cancellation Penalties**: 3% per bidder with free cancellation for no-bid tasks
✅ **Arbitration System**: Complete dispute resolution with admin review and payment execution
✅ **Database Optimization**: Indexes for performance on all new queries
✅ **API Documentation**: All endpoints documented with examples
✅ **Error Handling**: Comprehensive validation and error messages
✅ **Transaction Safety**: MongoDB transactions ensure payment consistency
✅ **Configuration**: All parameters configurable via environment variables

**Implementation Date**: 2026-03-17
**Status**: Production Ready
**Test Coverage**: Manual testing scenarios provided
**Migration**: Backward compatible, no data migration required

---

*For questions or issues, refer to CLAUDE.md or submit a GitHub issue.*

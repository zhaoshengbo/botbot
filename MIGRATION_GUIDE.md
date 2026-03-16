# Migration Guide: Deploying Bid Limits, Penalties & Arbitration

## Pre-Deployment Checklist

- [ ] Review `IMPLEMENTATION_SUMMARY.md` for feature details
- [ ] Review `API_ENDPOINTS.md` for API changes
- [ ] Backup MongoDB database
- [ ] Test in staging environment first
- [ ] Notify users of new features (optional)

---

## Deployment Steps

### Step 1: Code Deployment

#### A. Pull Latest Code
```bash
cd /path/to/botbot
git pull origin main
```

#### B. Backend Deployment

**Option 1: Docker (Recommended)**
```bash
cd be
docker-compose down
docker-compose build
docker-compose up -d
```

**Option 2: Direct Deployment**
```bash
cd be
# Install any new dependencies (none in this update)
pip install -r requirements.txt

# Restart the service
sudo systemctl restart botbot-backend
# OR
uvicorn app.main:app --reload
```

#### C. Verify Backend Started
```bash
# Check health endpoint
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Check API docs
curl http://localhost:8000/docs
# Should return Swagger UI HTML
```

---

### Step 2: Database Index Creation

**Run the index script:**
```bash
cd be
python add_indexes.py
```

**Expected Output:**
```
🔍 Connecting to MongoDB...
📊 Adding indexes...

1. Creating indexes on 'tasks' collection...
   ✓ Index: status + bid_count
   ✓ Index: publisher_id + status

2. Creating indexes on 'bids' collection...
   ✓ Index: task_id + status
   ✓ Index: bidder_id + status

3. Creating indexes on 'arbitrations' collection...
   ✓ Index: status + created_at (desc)
   ✓ Index: contract_id
   ✓ Index: assigned_admin_id + status
   ✓ Index: publisher_id
   ✓ Index: claimer_id

✅ All indexes created successfully!
```

**If indexes already exist:**
- MongoDB will skip duplicate index creation
- No errors expected

---

### Step 3: Configuration (Optional)

**Edit `.env` file if you want to customize:**
```bash
cd be
vi .env
```

**Add or modify these settings:**
```env
# Task Settings
MAX_BIDS_PER_TASK=10
TASK_CANCELLATION_PENALTY_RATE=0.03
SELECTION_PHASE_DEADLINE_HOURS=72

# Arbitration Settings
ARBITRATION_RESPONSE_DEADLINE_HOURS=168
```

**If not set, defaults will be used (recommended for first deployment).**

**After editing `.env`, restart backend:**
```bash
docker-compose restart  # Docker
# OR
sudo systemctl restart botbot-backend  # Systemd
```

---

### Step 4: Smoke Testing

#### Test 1: Verify New Status Values
```bash
# Create a new task
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Task - Migration",
    "description": "Testing new features",
    "budget": 100,
    "bidding_period_hours": 48,
    "completion_deadline_hours": 168
  }'

# Should succeed, status = "bidding"
```

#### Test 2: Verify Cancellation Endpoint
```bash
# Get cancellation estimate
curl -X GET http://localhost:8000/api/tasks/{task_id}/cancellation-estimate \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return:
# {
#   "can_cancel": true,
#   "reason": "Free cancellation",
#   "active_bid_count": 0,
#   "penalty_per_bidder": 0,
#   "total_penalty": 0,
#   "remaining_balance_after_cancel": YOUR_BALANCE
# }
```

#### Test 3: Verify Arbitration Endpoint
```bash
# Check arbitration endpoint exists
curl -X GET http://localhost:8000/api/arbitration/my-cases \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return:
# {
#   "arbitrations": [],
#   "total": 0,
#   "page": 1,
#   "page_size": 20
# }
```

#### Test 4: Verify Admin Arbitration Endpoint
```bash
# Check admin arbitration endpoint (admin token required)
curl -X GET http://localhost:8000/api/admin/arbitration/pending \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Should return:
# {
#   "arbitrations": [],
#   "total": 0,
#   "page": 1,
#   "page_size": 20
# }
```

---

### Step 5: Frontend Deployment (Optional)

**If you have frontend changes to deploy:**

```bash
cd fe
npm install  # Install any new dependencies
npm run build
docker-compose restart  # Or your deployment method
```

**Note:** This backend-only update doesn't require frontend changes. The frontend will automatically use the new endpoints when you implement UI features.

---

## Data Migration

### Good News: No Migration Required! 🎉

This update is **fully backward compatible**:

✅ **Existing tasks** continue to work normally
- Tasks without `max_bids` field will use default (10)
- Tasks without `selection_deadline` will get it when reaching 10 bids
- Old task statuses (`open`, `bidding`, etc.) unchanged

✅ **Existing bids** continue to work normally
- Bids without `compensation_amount` field work fine
- Old bid statuses (`active`, `accepted`, etc.) unchanged

✅ **Existing contracts** continue to work normally
- New arbitration system is opt-in (only when disputes occur)

✅ **New fields added automatically**
- MongoDB will add new fields on first use
- No schema migration needed

### What Happens to Old Data?

**Tasks created before deployment:**
- Will use default `max_bids = 10` if field is missing
- Can still receive bids normally
- Will auto-transition to SELECTING when reaching 10 bids

**Bids created before deployment:**
- Will never have `compensation_amount` (that's fine)
- Only new cancellations will use compensation fields

**No arbitrations collection:**
- Will be created automatically on first arbitration request
- No pre-creation needed

---

## Rollback Plan (If Needed)

### Quick Rollback (Revert Code)

```bash
cd /path/to/botbot
git log --oneline -5  # Find commit hash before deployment
git revert <commit_hash>  # Or git reset --hard <commit_hash>

# Rebuild and restart
cd be
docker-compose down
docker-compose up -d --build
```

### Data Rollback (Not Needed)

**New fields don't break old code:**
- Extra fields in MongoDB are ignored by old code
- No data corruption possible

**Indexes can stay:**
- Indexes don't break anything, only improve performance
- Safe to leave in place even after rollback

---

## Post-Deployment Monitoring

### Check Logs for Errors

**Docker:**
```bash
docker-compose logs -f backend
```

**Systemd:**
```bash
journalctl -u botbot-backend -f
```

**Look for:**
- ❌ Import errors (should not happen)
- ❌ MongoDB connection issues
- ✅ Successful startup messages

### Monitor Key Metrics

**Task Cancellations:**
```bash
# Check how many cancellations with penalties
db.tasks.countDocuments({
  status: "cancelled",
  cancellation_penalty_paid: { $gt: 0 }
})
```

**Arbitrations:**
```bash
# Check arbitration request volume
db.arbitrations.countDocuments({ status: "pending" })
```

**Bid Limits:**
```bash
# Check tasks reaching 10 bids
db.tasks.countDocuments({
  status: "selecting",
  bid_count: { $gte: 10 }
})
```

---

## Common Issues & Solutions

### Issue 1: ModuleNotFoundError on Import

**Symptom:**
```
ModuleNotFoundError: No module named 'app.schemas.arbitration'
```

**Solution:**
```bash
# Verify file exists
ls -la be/app/schemas/arbitration.py

# Restart backend
docker-compose restart backend
```

### Issue 2: Index Creation Fails

**Symptom:**
```
pymongo.errors.OperationFailure: index already exists with different options
```

**Solution:**
```bash
# Drop conflicting index
mongo botbot
db.tasks.dropIndex("status_1_bid_count_1")

# Re-run index script
python add_indexes.py
```

### Issue 3: 404 on /api/arbitration

**Symptom:**
```json
{"detail": "Not Found"}
```

**Solution:**
```bash
# Verify router is registered in main.py
grep "arbitration" be/app/main.py

# Should see:
# from app.api.routes import ... arbitration
# app.include_router(arbitration.router, ...)

# Restart backend
docker-compose restart backend
```

### Issue 4: Transaction Errors

**Symptom:**
```
Failed to process cancellation penalty: This MongoDB deployment does not support transactions
```

**Solution:**
MongoDB must run as a replica set for transactions.

**Check replica set:**
```bash
mongo
rs.status()
```

**If not a replica set, convert:**
```bash
# Stop MongoDB
sudo systemctl stop mongod

# Edit /etc/mongod.conf
replication:
  replSetName: "rs0"

# Restart and initiate
sudo systemctl start mongod
mongo --eval "rs.initiate()"
```

---

## Production Deployment Checklist

### Before Deployment
- [x] Code reviewed and tested in staging
- [ ] Database backup created
- [ ] Rollback plan documented (see above)
- [ ] Team notified of deployment window
- [ ] Monitoring tools ready (logs, metrics)

### During Deployment
- [ ] Pull latest code
- [ ] Run index creation script
- [ ] Verify environment variables
- [ ] Restart backend services
- [ ] Run smoke tests (4 tests above)

### After Deployment
- [ ] Check application logs (no errors)
- [ ] Verify all endpoints respond correctly
- [ ] Monitor error rates for 30 minutes
- [ ] Test one full workflow (task → bid → cancel)
- [ ] Update team documentation if needed

### If Issues Found
- [ ] Check "Common Issues" section
- [ ] Review error logs for root cause
- [ ] Execute rollback plan if critical
- [ ] Document issue for post-mortem

---

## Feature Verification

### Week 1 After Deployment

**Monitor these metrics:**

1. **Bid Limits Usage:**
   - How many tasks reach 10 bids?
   - How many get stuck in SELECTING?
   - Average time to select a bid

2. **Cancellation Penalties:**
   - How many free cancellations?
   - How many paid cancellations?
   - Total penalties collected
   - Average penalty amount

3. **Arbitration Usage:**
   - How many arbitration requests?
   - Average resolution time
   - Publisher vs claimer win rate
   - Average payment split percentage

**MongoDB Queries for Metrics:**

```javascript
// Bid limits
db.tasks.aggregate([
  { $match: { status: "selecting" } },
  { $count: "tasks_at_bid_limit" }
])

// Cancellation penalties
db.tasks.aggregate([
  { $match: { cancellation_penalty_paid: { $gt: 0 } } },
  { $group: {
      _id: null,
      total_penalties: { $sum: "$cancellation_penalty_paid" },
      count: { $sum: 1 },
      avg_penalty: { $avg: "$cancellation_penalty_paid" }
  }}
])

// Arbitrations
db.arbitrations.aggregate([
  { $group: {
      _id: "$status",
      count: { $sum: 1 }
  }}
])
```

---

## User Communication (Optional)

**Announcement Template:**

```
📢 BotBot Platform Update - New Features Available!

We've deployed several improvements to make task management fairer:

✨ What's New:

1️⃣ Bid Limits (Max 10 bids)
- Tasks now accept maximum 10 bids to make selection easier
- After 10 bids, task enters "selection phase" for publisher to choose

2️⃣ Cancellation Penalties
- Cancel tasks with no bids: Free (as before)
- Cancel tasks with active bids: 3% penalty per bidder
- Use the new "preview cost" feature before cancelling
- Protects bidders' time investment

3️⃣ Dispute Resolution (Arbitration)
- New system to resolve deliverable disputes
- Request arbitration if you disagree with completion review
- Admin will review evidence and decide fair payment split
- Fairer outcomes for both parties

📚 Learn More: See API_ENDPOINTS.md in our docs

Questions? Contact support@botbot.biz
```

---

## Timeline Estimate

**Deployment Duration:**

| Step | Estimated Time | Notes |
|------|----------------|-------|
| Code pull & build | 5 minutes | Docker build time |
| Index creation | 2 minutes | Depends on data volume |
| Configuration | 1 minute | Optional |
| Smoke testing | 5 minutes | 4 endpoint tests |
| **Total** | **~15 minutes** | Zero downtime possible |

**Recommended Deployment Window:**
- Low-traffic period (e.g., 2 AM - 4 AM)
- Or use rolling deployment (zero downtime)

---

## Success Criteria

✅ **Deployment is successful if:**

1. Health endpoint returns `{"status":"healthy"}`
2. API documentation loads at `/docs`
3. All 4 smoke tests pass
4. No errors in application logs
5. Existing tasks/bids/contracts work normally
6. New endpoints return expected responses

❌ **Rollback if:**

1. Critical errors in logs (500 errors)
2. MongoDB connection failures
3. Any smoke test fails
4. Existing functionality broken

---

## Support Contacts

**Technical Issues:**
- Backend: [Your Backend Dev]
- Database: [Your DBA]
- DevOps: [Your DevOps Engineer]

**Emergency Rollback:**
- On-call Engineer: [Phone/Slack]

---

*Last Updated: 2026-03-17*
*Deployment Version: v1.1.0*
*Author: Claude Code*

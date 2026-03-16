# Fix for Task ID undefined issue

## Problem
Frontend was receiving `undefined` for task `id` field, causing URLs like `/api/tasks/undefined`.

## Root Cause
Backend was using Pydantic alias `id: str = Field(..., alias="_id")` to map MongoDB's `_id` field to `id`, but FastAPI wasn't properly serializing the response with the alias.

## Solution
1. **Removed alias from all Response schemas**:
   - `TaskResponse` - be/app/schemas/task.py
   - `BidResponse` - be/app/schemas/bid.py
   - `ContractResponse` - be/app/schemas/contract.py
   - `RatingResponse` - be/app/schemas/rating.py
   - `UserResponse` - be/app/schemas/user.py
   - Payment schemas - be/app/schemas/payment.py

2. **Updated all routes to rename _id to id**:
   Changed `task["_id"] = str(task["_id"])` to `task["id"] = str(task.pop("_id"))`
   - tasks.py
   - bids.py
   - contracts.py
   - ratings.py
   - users.py
   - auth.py
   - payment.py

## Testing
To verify the fix:

1. Start backend:
```bash
cd be
uvicorn app.main:app --reload
```

2. Test API endpoint:
```bash
curl http://localhost:8000/api/tasks | jq '.tasks[0] | {id, title}'
```

Expected response should include `"id": "some_string"` instead of `"_id": "..."`.

3. Start frontend and check browser console - no more `/api/tasks/undefined` errors.

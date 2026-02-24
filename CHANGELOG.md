# 📝 Changelog - NYC Delivery System

## v5.1 - Option B (Balanced Model) - 2026-02-23

### ✅ **Changes:**

**Driver Pay Model Updated:**
- `BASE`: $3.50 → **$4.00** (+$0.50)
- `PER_KM`: $0.70 → **$0.80** (+$0.10)
- `PER_MIN`: $0.10 → **$0.12** (+$0.02)

**Results:**
- Driver pay increased by **~16%**
- Platform profit still **≥ $4** for most orders
- More competitive for driver acquisition

### 📊 **Example (3km, 20min):**

| Metric | Old | New | Change |
|--------|-----|-----|--------|
| Driver Pay | $7.60 | $8.80 | +$1.20 |
| Platform Profit | $5.54 | $4.34 | -$1.20 |
| Customer Total | $35.98 | $35.98 | $0 |

**Impact:**
- ✅ Better driver satisfaction
- ✅ Profit still above $4 target
- ✅ Customer price unchanged
- ✅ More competitive vs DoorDash/Uber

---

## v5.0 - Initial Release - 2026-02-22

### Features:
- White Label restaurant pages
- Dynamic pricing engine
- Stripe integration
- Mapbox geocoding & routing
- Telegram bot for drivers
- SMS notifications (Twilio)
- Complete dashboard
- Rating system

**Pricing Model v5.0:**
- Delivery fees: Distance-based tiers
- Service fee: 12% (min $3.49)
- Restaurant commission: 10-18% tiers
- Driver pay: Base + km + min
- Stripe fees: 2.9% + $0.30
- Target: ≥$4 profit per order

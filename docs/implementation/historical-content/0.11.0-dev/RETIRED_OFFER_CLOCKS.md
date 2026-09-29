# Retired offer clocks — archived 0.11.0-dev

**Archive, not a deletion.** Every value, field and string removed when offers and trades stopped
expiring is recorded here in full, so a tuned number is recoverable without reading a diff.

Retired under owner direction, 2026-09-29, verbatim:

> *"nothing ever ever have time restripctions but the gate(ie power tech and maintanance and
> workflorce and other factors all determine the time a gate can be open) but missions and quests
> and offeres and trades are never time senstive the company will wait as long as possible for you
> to complete their task offers"*

Scope confirmed by the owner at the fork: **offers and trades are in scope**, not only campaign
content. Both clocks below were **pure time pressure with no bounding function** — each pool was
already capped by a count, which is recorded per clock so that nobody re-adds one believing it was
load-bearing.

---

## 1. The hiring offer expiry

**A job applicant withdrew itself after seven in-game days.**

### The tuned values

```csharp
// HiringPolicyDef.cs
public int offerTicks = 420000;          // 420,000 ticks = 7 in-game days
```

```xml
<!-- RR_HiringPolicies.xml -->
<offerTicks>420000</offerTicks>
```

Note `refreshTicks` was **the same value, 420000**, and is **kept** — it is a cooldown before a
new hiring request may be made, which cannot be failed.

### The validation it participated in

```csharp
refreshTicks >= GenDate.TicksPerDay && offerTicks >= 1 && onboardingUsd > 0 && dailyWageUsd > 0
```

### The saved field, and the three call sites

```csharp
// ApplicantRecord.cs
internal int expiresTick;
public int ExpiresTick { get { return expiresTick; } }
Scribe_Values.Look(ref expiresTick, "expiresTick");
```

```csharp
// RimroomsPersonnelComponent.cs — creation
offers.Add(new ApplicantRecord { id = id, createdTick = Now, expiresTick = AddTicks(Now, policy.offerTicks), ... });

// RimroomsPersonnelComponent.cs — save validation
offer.onboardingUsd <= 0 || offer.dailyWageUsd <= 0 || offer.createdTick < 0 || offer.expiresTick < offer.createdTick ||

// RimroomsPersonnelComponent.cs — the tick that withdrew it
ApplicantRecord expired = offers.FirstOrDefault(o => o.status == ApplicantStatus.Offered && Now >= o.expiresTick);
if (expired != null) { StartRelease(expired, ApplicantRelease.Expired); }

// RimroomsPersonnelComponent.cs — the release reason
return StartRelease(offer, Now >= offer.expiresTick ? ApplicantRelease.Expired : ApplicantRelease.Declined);

// HiringServices.cs — the accept refusal
if (offer.status != ApplicantStatus.Offered || Now >= offer.expiresTick) { return Refuse("RR_Personnel_OfferClosed"); }
```

### Why removing it bounds nothing

`maxOffers` is **1–3**, and `RequestApplicants` refuses outright while any offer is still open:

```csharp
if (offers.Any(o => o.IsOpen) || held.Count > 0) { return Refuse("RR_Personnel_FinishOffers"); }
```

So the pool cannot exceed three, and the player cannot request a fourth until the batch is
resolved. **The clock never capped anything.** Accepting or declining is what ends a batch, and
that is a decision rather than a deadline.

### What is kept, and why

`expiresTick` stays **scribed but unread**, and `ApplicantStatus.Expired` /
`ApplicantRelease.Expired` stay in their enums. A save written before this checkpoint contains
both, and dropping a scribed field or an enum member to tidy up is how a saved game stops loading.

---

## 2. The procurement quote expiry

**A purchase quote expired after roughly ten in-game hours.**

### The tuned value

```csharp
// RimroomsProcurementComponent.cs
private const int QuoteLifetimeTicks = 25000;    // 25,000 ticks ≈ 0.42 in-game days ≈ 10 hours
```

### The call sites

```csharp
// creation
int expiresTick;
if (!TryAddTicks(now, QuoteLifetimeTicks, out expiresTick) || ...)
{ return CompanyActionResult.Refused("RR_Proc_TimeOverflow"); }
...
createdTick = now,
expiresTick = expiresTick,

// the accept refusal
if (now > quote.expiresTick) { return CompanyActionResult.Refused("RR_Proc_QuoteExpired"); }

// the pruning
private void RemoveExpiredQuotes(int now)
{ quotes.RemoveAll(quote => quote == null || (!quote.accepted && now > quote.expiresTick)); }
```

### The player-facing string

```xml
<RR_Proc_QuoteExpired>This quote expired. Request a new quote to see current stack limits and schedule.</RR_Proc_QuoteExpired>
```

### Why removing it bounds nothing

`MaximumSavedQuotes` already caps the list and `RequestQuote` refuses at the cap:

```csharp
if (quotes.Count >= MaximumSavedQuotes) { return CompanyActionResult.Refused("RR_Proc_TooManyQuotes"); }
```

**The clock never capped anything here either.** The pruning is kept, narrowed to dropping null
entries only.

### What is kept, and why

`expiresTick` on `ProcurementQuoteRecord` stays scribed but unread, for the same save-compatibility
reason as above. `dispatchDelayTicks` and `leadTimeTicks` are **untouched**: delivery taking time
is a supplier being slow, not a player being late, and nothing fails when they elapse.

---

## What was NOT retired

Recorded so that this archive cannot be read as licence to remove more:

| Kept | Why |
|---|---|
| The gate's opening and emergency-return windows | The one clock the direction permits |
| `refreshTicks`, `nextRequestTick`, planning cooldowns, retry backoffs | Cooldowns before the player may act. A cooldown cannot be failed |
| `dispatchDelayTicks`, `leadTimeTicks` | Delays on delivery. Nothing is asked of the player |
| `NextPayrollTick`, an obligation's `dueTick` | A recurring cost and a schedule label |
| A travelling deployment's `leaseExpiryTick` | Releases a reservation for a worker who never arrived. A **deployed** worker has no countdown at all |
| Core's glow-pod `lifespanTicks` | Core content. A pod designated as a marker is held at zero |
| Every `...Tick` that records **when something happened** | History, not a countdown |

---

## Process note

The first attempt at this change **deleted these values outright with no archive**, and the owner
stopped it:

> *"what the fuck? u just straight cleared/deleted deffs and shit how tf do you know we didnt need
> that shit coded up correctly and wasnt unfinished work"*

Nothing had been committed, so the tree was restored to `3cf7dc8` intact and the scope was asked
rather than assumed. The answer confirmed the reading — **and confirmed that the method was the
problem, not the conclusion.** Retired content is archived, never deleted. This file is that
archive.

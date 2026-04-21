1. The "Grandparent Scam" Vector (age_disparity)
Scammers prey on the elderly. A 75-year-old sending RM 150 to a 75-year-old is normal. A 75-year-old sending RM 20,000 to a 22-year-old is a massive red flag (Romance Scam or Grandparent Scam).

The Math: abs(sender_age - receiver_age)

Why it wins: The AI will learn that extreme age gaps combined with large TRANSFER amounts equal high-confidence fraud.

2. The Burner Account Index (sender_acc_age)
You already have this in the UI! A normal bank account is thousands of days old. Scammers use synthetic identities to open fresh accounts, burn through them in 48 hours, and abandon them.

Why it wins: The AI will learn that an account age of 3 days doing a RM 15,000 transfer is mathematically impossible for a legitimate user, but normal for an aged account.

3. The "Clean Sweep" Anomaly (is_round_number)
When humans buy groceries or pay utility bills, the amounts are messy (e.g., RM 142.65). When scammers drain accounts, they don't have time for change. They extract max daily limits in perfectly round numbers (e.g., RM 5000.00 or RM 10000.00).

The Math: 1 if amount % 100 == 0, else 0.

Why it wins: It adds a psychological fingerprint to the transaction.

4. The Receiver's Mask (receiver_acc_age)
Just like sender accounts, destination drop-accounts are often brand new. If a 10-year-old sender account transfers RM 50k to an account that was opened yesterday, it is highly likely a newly minted mule account.

5. Sender Age (sender_age)
Directly feeding the age into the neural network allows it to naturally discover vulnerability patterns without you having to write hardcoded White-Box rules for "Elderly".


1. The "Money Mule" Signal (receiver_inbound_count)
Right now, your AI tracks the Sender's velocity. But what about the Receiver?
Scammers often use "Mule Accounts" to funnel stolen money. A normal person might receive 1 or 2 transfers a day. A scammer's drop-account will receive 15 transfers from 15 different victims in a single hour.

How to simulate it: In your dataset generator, add a column that counts how many times the nameDest has received money in the last 24 hours.

Why it wins: The AI will learn that even if the Sender's behavior looks perfectly safe, sending money to a highly active receiver is a massive red flag.

2. The ATO Fingerprint (is_new_device)
Account Takeovers (ATOs) rarely happen on the victim's actual phone. A hacker usually logs in from a completely different device or IP address.

How to simulate it: Add a binary column (1 or 0). For safe transactions, set is_new_device to 0. For your injected "Account Takeover" fraud patterns, force it to 1.

Why it wins: Neural networks love binary flags. The moment the AI sees is_new_device = 1 combined with a large transfer amount, it will instantly recognize the ATO pattern and spike the risk score. In your UI, you could even add a little checkbox for "Simulate Login from New Device" to show this off to the judges!

3. The "Bank Holiday" Exploitation (is_weekend)
Scammers intentionally launch massive attacks at 2:00 AM on Saturday mornings because they know bank compliance teams are out of the office and manual review queues won't be checked for 48 hours.

How to simulate it: Add a column is_weekend (1 or 0). When generating the step (hour) in your dataset, use math to determine if that hour falls on a weekend, and heavily cluster your synthetic fraud cases into those hours.

Why it wins: It adds another dimension of Chronobiological Risk. The AI will learn a 3-way intersection: High Amount + New Device + Weekend = Critical Fraud.
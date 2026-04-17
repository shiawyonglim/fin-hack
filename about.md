Topic idea
stripe radar but uses onnx runtime
o	The neural network evaluates fraud probability locally via WebAssembly the millisecond a transfer starts. If the AI detects an anomaly, it kills the transaction instantly. It then drops to a hardcoded, white-box deterministic rule engine—printing a plain-text compliance log explaining the exact mathematical boundary breached. No cloud latency.
o	Detect transfer (high_stake = receive > 1000 and transfer > 1000 and count > 2)
offline mesh network to move money without the internet
o	When you pay someone, your phone signs the receipt with a private digital key. The proof is absolute. This receipt bounces from phone to phone. The first device to find Wi-Fi uploads the file to the main server. The server reads the key. It trusts the math. The money moves immediately. You never wait for the original sender to reconnect.
Voice recognition (Whisper-Tiny)
o	Capture the users voice, anything they needed, the user can use natural language and the system can understand the user and will 
o	Can identify  the user phone, if the user phone can run the llm then the user phone will run it on its own, if cannot then the server will run it for the user


Ux pipeline
1. The Trigger: Voice Recognition (Whisper-Tiny)
•	Where it lives in the app: A massive, persistent, glowing "Microphone" floating action button on the Home Screen.
•	The Hackathon Correction (Wake Words): Do not try to build a "Hey TNG" wake word. Background listening in a browser drains the battery and is incredibly hard to code in 36 hours. Use a "Tap and Hold to Speak" button. It is deterministic and saves development time.
•	The Execution: The user taps the mic and says, "Sila transfer liang bai wu shi kuai to Mr. Loy." Whisper-Tiny processes the audio offline and your Data Engineer’s Rojak dictionary parses the intent.
2. The UI Handoff (The Voice Router)
•	Where it lives in the app: The Transfer Screen.
•	The Execution: The user's screen instantly jumps from the Home Screen to the Transfer Screen. The app automatically fills the text boxes: Recipient: Mr. Loy, Amount: RM 250.00.
•	The Accessibility Loop: The app uses Text-to-Speech to read it back: "Transferring two hundred and fifty ringgit to Mr. Loy. Please scan your face to confirm."
3. The Security Gate (WebAuthn)
•	Where it lives in the app: A native browser pop-up.
•	The Execution: The user does not speak a PIN. The FaceID/TouchID prompt appears. The user looks at the phone. The hardware verifies their identity.
4. The Invisible Shield: Fraud Detection (ONNX Runtime)
•	Where it lives in the app: It sits exactly between FaceID and the final payment. It has no UI of its own unless it catches a scam.
•	The Execution: The moment FaceID approves the user, the app grabs the transaction data (RM 250 to Mr Loy, time of day, user account age) and feeds it into the PyTorch .onnx model.
•	The Two Outcomes:
o	If Fraud (e.g., Anomaly detected): The UI turns red. A terminal-style box appears saying: [SYSTEM: ABNORMAL VELOCITY DETECTED. TRANSFER BLOCKED.]
o	If Safe: The UI turns green and proceeds to the final step.
5. The Vault: Offline Mesh Network (IndexedDB & Cryptography)
•	Where it lives in the app: The "Offline Ledger" Screen.
•	The Execution: Because there is no internet, the app cannot show a standard "Payment Successful" green checkmark. Instead, it shows: "Transaction Signed & Queued."
•	The Visual Proof: The app generates a cryptographic receipt using libsodium and saves it to the browser's IndexedDB. The UI then displays a dynamic QR Code representing that specific encrypted block.
•	The Mesh Jump: When Mr. Loy (who also has no internet) scans that QR code with his phone, the encrypted block jumps from your phone to his phone via the camera. When either of you eventually finds Wi-Fi, your app will automatically push the block from IndexedDB up to the Alibaba Cloud server.
 
Onnx runtime- fraud detection
-	Introduction
o	Fraud detection is to help people who has bad scam awareness. It will detect bad transactions and add a layer of protection for these people. Especially to the elderly and people who cannot afford to get scammed.
-	Feature
o	Do a self-evaluation and 
o	Detect money laundering 
o	Detect scams
o	Detect safe transaction
o	Log the suspicious person so when transferring to other account the name will be flag.
o	Offline and online detection
o	Auto scammer detector
o	Find scammer through online
-	How it works
o	It will do a self-evaluation, reading through the older transaction and see fi the transaction is a fraud or not
o	For example , Maybe the receiver receive money from 60+ years old person multiple times in a week and the amount for each transaction is around 1000 and above, then it is likely to be a scam targeted against old people
o	This is to protect user from being scam, so If an user tried to transfer money to a suspicious account, the user will be warn of the risk of scam
o	Self-evaluation will be the onnx will evaluate the user and categorise the user into a few parts like children, elderly, adult, potential scammer, scammer, suspicious account and more. Depending on the category it will have their own custom ways to fight against scammer. Such as scammer account will not be able to receive any money from anybody until proven otherwise, elderly account will have a stricter policy and money will be easier to get back because of the stricter policy
o	Offline, the system uses a Zero-Trust Edge policy. It only evaluates the SENDER'S behavior to protect them from making a mistake. It does NOT trust the receiver's device over Bluetooth. Instead, it checks the receiver's details against the offline cached scammer database. If it's a match, the transfer is blocked locally.
o	If elderly people suddenly want to transfer everything they have in 2 am in the morning the onnx will stop the transfer
o	Every time the system connects to the wifi the user will download a list of scammers name so even if they transfer to another bank the onnx can still read the list of scammers and send advice to the users
Onnx runtime- voice assistant
-	Introduction
o	This is targeted to people who don’t know how to use their mobile phone. Elderly people especially will struggle with the complex interface of the application, they now can just talk to their phone and send money without bothering with the herd to navigate ui
-	Feature
o	Help transfer money
o	help navigate the application
o	support Bahasa rojak
o	open camara and scan qr code for payment
-	how it works
o	whiper tiny will send a string of letter to the onnx then it will process it, the onnx will process the string and help the user.
o	User will ned to use faceid, fingerprint or their pins to continue with the payment for security purposes 

Offline mesh
-	Introduction
o	A feature that let user transfer money without the internet. 
-	Feature
o	One main encryption and multiple validation keys spread around the receipt
o	Using asymmetric encryption so the output is unreadable and can only be understand by the computer with the encryption
o	based on the self-evaluation using the onnx runtime. Some people will have more validation keys compared to others. People who have bad self-evaluation result will have more validation keys since they have a higher chance of doing bad things
o	calculate the account money not only by the value set but also the transactional history of the devices, if the math does not add up then suspend the account because temperament happened.
o	2 relay is enough for the transfer to happen, but the server will continue to get 10 more to do cross validation for the online server
-	How it works
o	the sender will send the money to the receiver, and both the user will receive a receipt talking about the transaction. The receipt will be broadcasted to nearby devices. Every device in the vicinity will act as a Blind Relay, carrying the encrypted ciphertext without being able to read the sender, receiver, or amount.

Scams databases detection
-	introduction
o	get databases that might be scams and not allow user to transfer money t these accounts
-	feature
o	fraud detection using database and proven scammer 
-	how it works
o	an algorithm will check the transaction to the database and find the potential scam and fraud
o	BNM Financial Consumer Alert (FCA) List
o	Securities Commission (SC) Investor Alert List


Roles 
-	Integration Engineer (integrate and test) (khee en)
-	Ai engineer (will do the onnx) (rap)(me)
-	Pitcher + build slide deck (log ming ming)
-	Backend developer (python fast api and http control) (ong zi xuan)
-	Data Engineer (find data, build data and test data) (amber)

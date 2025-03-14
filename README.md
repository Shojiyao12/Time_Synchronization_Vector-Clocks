# Time Synchronization and Vector Clocks

This project implements a **time synchronization system** using **vector clocks** in a distributed network. It simulates **message passing** between multiple processes while maintaining a consistent ordering of events.

## Quickstart Guide

### Running the Simulation
1. Copy all the contents from this repository.
2. Open a terminal and navigate to the folder containing `time-synchronization.py`.
3. Run the program using:
   ```bash
   python time-synchronization.py
   ```
4. The simulation will:
   - Create multiple processes (`p1, p2, p3, p4, p5`).
   - Synchronize processes using **vector clocks**.
   - Simulate **message delivery with delays** to test **causality preservation**.
   - Remove a process from the network dynamically.

### How It Works
- Each process maintains a **vector clock** to track message order.
- Messages are sent asynchronously and delivered in a **causally correct** manner.
- Processes wait for at least **five nodes** to join before sending messages.

## Core Concepts
- **Vector Clocks**: Ensure causal ordering in distributed systems.
- **Multicast Messaging**: Messages are sent with random delays to test synchronization.
- **Causal Delivery**: Messages are only delivered if all dependencies are satisfied.
- **Process Removal**: The system adapts dynamically when a node leaves.

## Preview of Simulation Output

### **Example Log Output**
```bash
[Network] Process 1 is the bootstrap node.
[Network] All five nodes have joined. Message sending is now allowed.
[Process 1] Sending message 'm' with timestamp {1: 1, 2: 0, 3: 0, 4: 0, 5: 0}
[Process 2] Received message 'm' from 1 (timestamp: {1: 1, 2: 0, 3: 0, 4: 0, 5: 0})
[Process 2] Delivering message 'm' from 1
```

## Notes:
- The **network delay** for each message is randomized.
- Messages are only delivered if all **vector clock conditions** are met.
- The system **removes processes dynamically** and updates clocks accordingly.

## Future Enhancements
- Implement **physical clock synchronization** (e.g., Berkeley Algorithm, NTP).
- Introduce **network partitions** to simulate real-world failures.
- Add **visualization tools** to track vector clock evolution.

